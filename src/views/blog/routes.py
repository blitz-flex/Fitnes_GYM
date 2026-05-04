import urllib.request
import json
import datetime
import os
from flask import render_template, request, jsonify, current_app, url_for, abort
from flask_login import login_required, current_user
from functools import wraps
from . import blog_bp
from ...models.blog import BlogPost
from ...extensions import db

@blog_bp.route('/')
def index():
    """Blog index page with pagination and filters"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'newest')
    reading = request.args.get('reading', '')
    category = request.args.get('category', '')

    query = BlogPost.query.filter_by(published=True)

    if search:
        query = query.filter(BlogPost.title.ilike(f'%{search}%'))
    if category:
        query = query.filter(BlogPost.category == category)
    if sort == 'oldest':
        query = query.order_by(BlogPost.created_at.asc())
    elif sort == 'popular':
        query = query.order_by(BlogPost.views.desc())
    else:
        query = query.order_by(BlogPost.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    db_posts_raw = pagination.items
    formatted_posts = []

    for db_post in db_posts_raw:
        rt = db_post.reading_time or 5
        # Apply reading time filter AFTER fetching (reading_time is a property)
        if reading == 'short' and rt >= 5:  continue
        if reading == 'medium' and (rt < 5 or rt > 10): continue
        if reading == 'long' and rt <= 10: continue

        if db_post.author and db_post.author.is_admin and not db_post.author_name:
            author_name = 'admin'
        else:
            author_name = db_post.author_name if db_post.author_name else (
                db_post.author.name if db_post.author else 'admin')
            if author_name in ['Administrator', 'Admin']:
                author_name = 'admin'

        formatted_posts.append({
            'id': db_post.id,
            'title': db_post.title,
            'excerpt': db_post.excerpt or (
                db_post.content[:150] + '...' if len(db_post.content) > 150 else db_post.content),
            'slug': db_post.slug,
            'featured_image': db_post.featured_image if db_post.featured_image and db_post.featured_image.startswith(
                'http') else (url_for('static',
                                      filename='images/blog/' + db_post.featured_image) if db_post.featured_image else 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=800'),
            'author_name': author_name,
            'created_at': db_post.created_at,
            'views': db_post.views or 0,
            'reading_time': rt,
            'category': db_post.category or 'Training'
        })

    return render_template('blog/index.html',
                           posts=formatted_posts,
                           pagination=pagination,
                           search=search,
                           sort=sort,
                           reading=reading,
                           category=category,
                           all_categories=['Training', 'Nutrition', 'Cardio', 'Recovery', 'Lifestyle'])


@blog_bp.route('/post/<slug>')
def post_detail(slug):
    """Individual blog post page"""

    db_post = BlogPost.query.filter_by(slug=slug, published=True).first()
    if not db_post:
        abort(404)

    db_post.increment_views()

    if db_post.author and db_post.author.is_admin and not db_post.author_name:
        author_name = 'admin'
    else:
        author_name = db_post.author_name if db_post.author_name else (
            db_post.author.name if db_post.author else 'admin')
        if author_name in ['Administrator', 'Admin']:
            author_name = 'admin'

    post = {
        'title': db_post.title,
        'excerpt': db_post.excerpt,
        'content': db_post.content,
        'featured_image': db_post.featured_image if db_post.featured_image and db_post.featured_image.startswith(
            'http') else (url_for('static',
                                  filename='images/blog/' + db_post.featured_image) if db_post.featured_image else 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200'),
        'author_name': author_name,
        'created_at': db_post.created_at,
        'reading_time': db_post.reading_time or 5
    }

    return render_template('blog/post_detail.html', post=post)


def extract_ai_content(text, topic=""):
    """Robustly extract html_content and excerpt from AI response (JSON or Regex)."""
    import re as pyre
    import json as pyjson

    text = text.strip()
    # Remove markdown
    text = pyre.sub(r'^```(?:json|html)?\s*', '', text, flags=pyre.IGNORECASE | pyre.MULTILINE)
    text = pyre.sub(r'\s*```$', '', text, flags=pyre.IGNORECASE | pyre.MULTILINE)

    ai_data = {}

    try:
        first = text.find('{')
        last = text.rfind('}')
        if first != -1 and last != -1:
            candidate = text[first:last + 1]
            ai_data = pyjson.loads(candidate, strict=False)
    except:
        pass

    if not ai_data.get('html_content'):
        hc_match = pyre.search(r'"html_content":\s*"(.*?)(?<!\\)"', text, pyre.DOTALL)
        if hc_match:
            try:
                val = hc_match.group(1).encode().decode('unicode_escape')
                ai_data['html_content'] = val
            except:
                ai_data['html_content'] = hc_match.group(1)

    if not ai_data.get('excerpt'):
        ex_match = pyre.search(r'"excerpt":\s*"(.*?)(?<!\\)"', text, pyre.DOTALL)
        if ex_match:
            try:
                val = ex_match.group(1).encode().decode('unicode_escape')
                ai_data['excerpt'] = val
            except:
                ai_data['excerpt'] = ex_match.group(1)

    content = ai_data.get('html_content', '')
    excerpt = ai_data.get('excerpt', topic + "...")

    if content:
        content = content.replace('```html', '').replace('```json', '').replace('```', '').strip()
        for _ in range(5):
            content = pyre.sub(r'^\s*Title:\s*.*?\n+', '', content, flags=pyre.IGNORECASE)
            content = pyre.sub(r'^\s*#+\s*.*?\n+', '', content, flags=pyre.IGNORECASE)
            content = content.strip()
        content = pyre.sub(r'\n{3,}', '\n\n', content)

    return content, excerpt


@blog_bp.route('/generate-ai-post', methods=['POST'])
@login_required
def generate_ai_post():
    """Generates a full blog post using Google Gemini AI SDK and saves it to DB"""
    import google.generativeai as genai

    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized. Please login.'}), 403

    topic = request.json.get('topic')
    category = request.json.get('category', 'Training')
    featured_image = request.json.get('image')
    custom_prompt = request.json.get('custom_prompt', '')

    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'Gemini API Key is missing in configuration'}), 500

    # Translate topic to English for better image search
    topic_en = topic
    if any(ord(c) > 127 for c in topic):
        try:
            genai.configure(api_key=api_key)
            trans_model = genai.GenerativeModel('gemini-1.5-flash')
            trans_resp = trans_model.generate_content(f"Translate this fitness topic to a short English search keyword: '{topic}'")
            if trans_resp.text:
                topic_en = trans_resp.text.strip().replace("'", "").replace('"', '')
        except:
            pass

    # Strategy: Fetch image ONLY via Official Unsplash API
    if not featured_image or 'unsplash.com/photo-1517836357463-d25dfeac3438' in featured_image:
        import random
        import urllib.parse
        import urllib.request
        import json
        
        unsplash_key = current_app.config.get('UNSPLASH_ACCESS_KEY')
        featured_image = "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200" # Default static fallback
        
        if unsplash_key and unsplash_key != 'DEMO_MODE':
            try:
                query = urllib.parse.quote(f"fitness {topic_en}")
                url = f"https://api.unsplash.com/search/photos?query={query}&per_page=15&client_id={unsplash_key}"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=8) as response:
                    data = json.loads(response.read().decode())
                    if data.get('results'):
                        chosen = random.choice(data['results'][:10])
                        featured_image = chosen['urls']['regular']
            except Exception as e:
                print(f"Unsplash API Error: {e}")

    try:
        genai.configure(api_key=api_key)
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except:
            available_models = ['models/gemini-1.5-flash', 'models/gemini-pro']

        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        content = None
        used_model = ""
        detailed_errors = []

        for model_path in available_models:
            try:
                model_name = model_path.split('/')[-1]
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
                model = genai.GenerativeModel(model_name, safety_settings=safety_settings)

                prompt_context = ""
                if category == 'Training':
                    from ...models.exercise import Exercise
                    import random
                    exercise = Exercise.query.filter(Exercise.name.ilike(f'%{topic}%')).first()
                    if not exercise:
                        all_ex = Exercise.query.limit(50).all()
                        if all_ex: exercise = random.choice(all_ex)
                    if exercise:
                        prompt_context = f"Reference Data for accuracy: Exercise: {exercise.name}, Primary Muscles: {', '.join(exercise.primary_muscles)}, Level: {exercise.level}. Include these physiological details in your advice. "

                from flask_babel import get_locale
                current_lang = get_locale()
                lang_name = "Georgian" if current_lang == 'ka' else "English"
                lang_instruction = f"IMPORTANT: Write EVERYTHING (title, html_content, excerpt) in {lang_name}. Ensure the tone and cultural nuances are appropriate for {lang_name} speakers."

                custom_instruction_block = f"\n[CRITICAL OVERRIDE]: {custom_prompt}\n(Follow the above override even if it contradicts the default style below)\n" if custom_prompt else ""

                default_requirements = ""
                if not custom_prompt:
                    default_requirements = (
                        "Use an expert yet highly motivational and practical tone suited for gym members and fitness enthusiasts. "
                        "Focus on actionable advice, workout integration, and real-world results. "
                        "Length: Approximately 500 words with expert technical detail."
                    )
                else:
                    default_requirements = "If the custom instructions above don't specify length or tone, use a motivational expert tone and aim for 500 words."

                prompt = (
                    f"You are a world-class Elite Performance Scientist and Peak Performance Coach. {lang_instruction} "
                    f"{custom_instruction_block}"
                    f"Task: Write an expert article about '{topic}' for the '{category}' category. "
                    f"Context: {prompt_context} "
                    f"General Requirements: {default_requirements} "
                    "Output Format: Output exactly ONE SINGLE JSON object. DO NOT include any text before or after the JSON. "
                    "The JSON must have exactly two fields: "
                    "1. 'html_content': The article in raw HTML (using <h2>, <h3>, <p>, <ul>, <li>, <strong>, <blockquote>). "
                    "2. 'excerpt': A concise, high-level executive summary (2 lines). "
                )
                response = model.generate_content(prompt)

                if response.text:
                    content, excerpt = extract_ai_content(response.text, topic)
                    if content:
                        used_model = model_name
                        break
            except Exception as e:
                detailed_errors.append(f"{model_path} Error: {str(e)}")
                continue

        # --- DeepSeek Fallback ---
        if not content:
            deepseek_key = current_app.config.get('DEEPSEEK_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
            if deepseek_key:
                try:
                    import requests as req
                    headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                    data = {
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": "You are a world-class Elite Coach. Output ONLY JSON with 'html_content' and 'excerpt'."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"}
                    }
                    ds_response = req.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=30)
                    if ds_response.status_code == 200:
                        ds_data = ds_response.json()
                        ds_content = ds_data['choices'][0]['message']['content']
                        content, excerpt = extract_ai_content(ds_content, topic)
                        if content: used_model = "deepseek-chat (Fallback)"
                except Exception as ds_err:
                    detailed_errors.append(f"DeepSeek Exception: {str(ds_err)}")

        # --- Mistral Fallback ---
        if not content:
            mistral_key = current_app.config.get('MISTRAL_API_KEY') or os.environ.get('MISTRAL_API_KEY')
            if mistral_key:
                try:
                    import requests as req
                    headers = {"Authorization": f"Bearer {mistral_key}", "Content-Type": "application/json"}
                    data = {
                        "model": "mistral-tiny",
                        "messages": [
                            {"role": "system", "content": "You are a world-class Elite Coach. Output ONLY JSON with 'html_content' and 'excerpt'."},
                            {"role": "user", "content": prompt}
                        ]
                    }
                    m_response = req.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data, timeout=30)
                    if m_response.status_code == 200:
                        m_data = m_response.json()
                        m_content = m_data['choices'][0]['message']['content']
                        content, excerpt = extract_ai_content(m_content, topic)
                        if content: used_model = "Mistral AI (Fallback)"
                except Exception as m_err:
                    detailed_errors.append(f"Mistral Exception: {str(m_err)}")

        if not content:
            return jsonify({'error': f"AI Failed. Errors: {' | '.join(detailed_errors)}"}), 500

        slug = topic.lower().replace(' ', '-').replace('/', '-')[:50]
        base_slug = slug
        counter = 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        import re
        clean_text = re.sub('<[^<]+?>', '', content)
        excerpt = clean_text[:200].strip() + "..."

        new_post = BlogPost(
            title=topic,
            content=content,
            excerpt=excerpt,
            slug=slug,
            category=category,
            featured_image=featured_image,
            author_id=current_user.id,
            author_name='AI Generation',
            published=True
        )

        db.session.add(new_post)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Article generated successfully using {used_model}!',
            'slug': slug
        })

    except Exception as e:
        return jsonify({'error': f"AI Error: {str(e)}"}), 500


@blog_bp.route('/ask-expert', methods=['POST'])
def ask_expert():
    """Handles real-time chat with the AI Expert with fallback and model discovery"""
    question = request.json.get('question')
    if not question:
        return jsonify({'error': 'Question is required'}), 400

    api_key = current_app.config.get('GEMINI_API_KEY')
    answer = None
    detailed_errors = []

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            available_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
            except:
                available_models = ['models/gemini-1.5-flash', 'models/gemini-pro']

            for model_path in available_models:
                try:
                    model_name = model_path.split('/')[-1]
                    model = genai.GenerativeModel(model_name)
                    prompt = f"You are a world-class Peak Performance Coach and Fitness Expert. Detect the language of the question and respond in that SAME language. Answer concisely (max 3-4 sentences): '{question}'"
                    response = model.generate_content(prompt)
                    if response.text:
                        answer = response.text
                        break
                except Exception as e:
                    detailed_errors.append(f"Gemini {model_name}: {str(e)}")
                    continue
        except Exception as e:
            detailed_errors.append(f"Gemini Global: {str(e)}")

    if not answer:
        deepseek_key = current_app.config.get('DEEPSEEK_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
        if deepseek_key:
            try:
                import requests as req
                headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a world-class Fitness Expert. Respond in the same language as the user. Answer concisely."},
                        {"role": "user", "content": question}
                    ]
                }
                ds_response = req.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=10)
                if ds_response.status_code == 200:
                    answer = ds_response.json()['choices'][0]['message']['content']
            except Exception as e:
                detailed_errors.append(f"DeepSeek: {str(e)}")

    if not answer:
        mistral_key = current_app.config.get('MISTRAL_API_KEY') or os.environ.get('MISTRAL_API_KEY')
        if mistral_key:
            try:
                import requests as req
                headers = {"Authorization": f"Bearer {mistral_key}", "Content-Type": "application/json"}
                data = {
                    "model": "mistral-tiny",
                    "messages": [{"role": "user", "content": f"As a fitness coach, detect the language and answer briefly in that same language: {question}"}]
                }
                m_response = req.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data, timeout=10)
                if m_response.status_code == 200:
                    answer = m_response.json()['choices'][0]['message']['content']
            except Exception as e:
                detailed_errors.append(f"Mistral: {str(e)}")

    if not answer:
        err_msg = "Expert is currently overloaded. Please try again in a few minutes."
        return jsonify({'error': err_msg}), 500

    return jsonify({'success': True, 'answer': answer})
