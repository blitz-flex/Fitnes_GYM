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

# Simple cache for NewsAPI to avoid hitting rate limits
NEWS_CACHE = {
    'data': None,
    'timestamp': None
}

CATEGORY_KEYWORDS = {
    'Nutrition':  ['nutrition','diet','food','meal','protein','carb','fat','vitamin','supplement','calorie','eating','drink','hydrat'],
    'Recovery':   ['recover','sleep','rest','stretch','foam','injury','pain','therapy','soreness','ice bath'],
    'Cardio':     ['cardio','running','cycling','swim','hiit','endurance','marathon','jogging','aerobic'],
    'Lifestyle':  ['lifestyle','mental','stress','habit','motivation','mindset','wellbeing','wellness','balance','routine'],
    'Training':   ['workout','exercise','gym','strength','muscle','weight','lift','squat','bench','deadlift','fitness'],
}

# Blacklist for non-fitness noise that often slips through API
NOISE_KEYWORDS_BLACKLIST = [
    'github', 'api ', 'marketing', 'influencer', 'meta ', 'facebook', 'voyages', 
    'cruise', 'sales report', 'teenage boy', 'hevy-cli', 'pypi', 'counselor', 
    'tech news', 'startup', 'programming', 'developer', 'software'
]

def guess_category(title, description=''):
    text = (title + ' ' + (description or '')).lower()
    
    # Strict noise check
    if any(noise in text for noise in NOISE_KEYWORDS_BLACKLIST):
        return None
        
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in kws):
            return cat
    return None

def sync_fitness_news():
    api_key = current_app.config.get('NEWS_API_KEY', '') 
    
    if api_key and api_key != 'DEMO_MODE':
        now = datetime.datetime.now()
        if NEWS_CACHE['timestamp']:
            if (now - NEWS_CACHE['timestamp']).total_seconds() < 600:
                return

        try:
            import urllib.parse
            # Search specifically in titles for highest relevance
            query = urllib.parse.quote("title:(fitness OR workout OR gym OR exercises OR bodybuilding OR cardio)")
            url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=60&apiKey={api_key}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                if data.get('status') == 'ok':
                    from ...models.user import UserAccount
                    admin = UserAccount.query.filter(UserAccount.username.in_(['admin', 'administrator'])).first()
                    if not admin: admin = UserAccount.query.first()
                    if not admin: return
                        
                    for idx, article in enumerate(data.get('articles', [])):
                        title = article.get('title', '')
                        desc = article.get('description', '')
                        
                        # Only save if it clearly fits a fitness category and isn't noise
                        category = guess_category(title, desc)
                        if not category:
                            continue
                            
                        if not article.get('urlToImage'): 
                            continue
                            
                        clean_title = title.lower().replace(' ', '-').replace('/', '-')[:30]
                        slug = f"api-news-{clean_title}"
                        
                        if BlogPost.query.filter_by(slug=slug).first():
                            continue
                            
                        try:
                            pub_date_obj = datetime.datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                        except:
                            pub_date_obj = now

                        import re
                        raw_content = article.get('content') or desc or ''
                        clean_content = re.sub(r'\[\+\d+\s+chars\]', '', raw_content).strip()

                        content_html = f"<p>{clean_content}</p><br><p><a href='{article.get('url')}' target='_blank' style='display:inline-block; padding:12px 24px; background:var(--primary-color); color:white; text-decoration:none; border-radius:12px; font-weight:bold;'>Read Full Article</a></p>"

                        new_post = BlogPost(
                            title=title,
                            content=content_html,
                            excerpt=(desc[:150] + '...') if desc else '',
                            slug=slug,
                            featured_image=article.get('urlToImage'),
                            category=category,
                            author_id=admin.id,
                            author_name=article.get('author')[:100] if article.get('author') else 'Fitness Expert',
                            created_at=pub_date_obj,
                            published=True,
                            views=1000 + idx * 50
                        )
                        db.session.add(new_post)
                        
                    db.session.commit()
                    NEWS_CACHE['timestamp'] = now
                    
                    # Cleanup: Ensure only 100 latest API posts exist
                    api_posts = BlogPost.query.filter(BlogPost.slug.like('api-news-%')).order_by(BlogPost.created_at.desc()).all()
                    if len(api_posts) > 100:
                        for p in api_posts[100:]:
                            db.session.delete(p)
                        db.session.commit()
                        
        except Exception as e:
            print(f"NewsAPI Sync Error: {e}")
            db.session.rollback()

@blog_bp.route('/')
def index():
    """Blog index page with pagination and filters"""
    # sync_fitness_news() - Disabled as requested. Only AI/Admin posts allowed now.

    page     = request.args.get('page', 1, type=int)
    per_page = 12
    search   = request.args.get('search', '').strip()
    sort     = request.args.get('sort', 'newest')
    reading  = request.args.get('reading', '')
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

    pagination   = query.paginate(page=page, per_page=per_page, error_out=False)
    db_posts_raw = pagination.items
    formatted_posts = []

    for db_post in db_posts_raw:
        rt = db_post.reading_time or 5
        # Apply reading time filter AFTER fetching (reading_time is a property)
        if reading == 'short'  and rt >= 5:  continue
        if reading == 'medium' and (rt < 5 or rt > 10): continue
        if reading == 'long'   and rt <= 10: continue

        if db_post.author and db_post.author.is_admin and not db_post.author_name:
            author_name = 'admin'
        else:
            author_name = db_post.author_name if db_post.author_name else (db_post.author.name if db_post.author else 'admin')
            if author_name in ['Administrator', 'Admin']:
                author_name = 'admin'

        formatted_posts.append({
            'id': db_post.id,
            'title': db_post.title,
            'excerpt': db_post.excerpt or (db_post.content[:150] + '...' if len(db_post.content) > 150 else db_post.content),
            'slug': db_post.slug,
            'featured_image': db_post.featured_image if db_post.featured_image and db_post.featured_image.startswith('http') else (url_for('static', filename='images/blog/' + db_post.featured_image) if db_post.featured_image else 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=800'),
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
                           all_categories=['Training','Nutrition','Cardio','Recovery','Lifestyle'])

@blog_bp.route('/post/<slug>')
def post_detail(slug):
    """Individual blog post page"""
    
    db_post = BlogPost.query.filter_by(slug=slug, published=True).first()
    if not db_post:
        abort(404)
        
    db_post.increment_views()
    
    # If it's an API post with a saved author name, use it. Otherwise use 'admin'
    # Force 'admin' for any administrator
    if db_post.author and db_post.author.is_admin and not db_post.author_name:
        author_name = 'admin'
    else:
        author_name = db_post.author_name if db_post.author_name else (db_post.author.name if db_post.author else 'admin')
        # Safety check for old synced posts
        if author_name in ['Administrator', 'Admin']:
            author_name = 'admin'
        
    post = {
        'title': db_post.title,
        'excerpt': db_post.excerpt,
        'content': db_post.content,
        'featured_image': db_post.featured_image if db_post.featured_image and db_post.featured_image.startswith('http') else (url_for('static', filename='images/blog/' + db_post.featured_image) if db_post.featured_image else 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200'),
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
    
    # Try 1: Balanced brace search and JSON parse
    # Using a simpler balanced brace search since Python 're' doesn't support recursion
    try:
        # Find the first { and matching-ish last }
        first = text.find('{')
        last = text.rfind('}')
        if first != -1 and last != -1:
            candidate = text[first:last+1]
            ai_data = pyjson.loads(candidate, strict=False)
    except:
        pass
        
    # Strategy 2: Direct Regex Extraction (The Tank)
    if not ai_data.get('html_content'):
        # Look for "html_content": " and then anything until a " followed by , or }
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
    
    # Final cleanup
    if content:
        # Basic cleanup
        content = content.replace('```html', '').replace('```json', '').replace('```', '').strip()
        # Aggressive removal of redundant headers
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
    
    # Simple admin check - allowing current logged in user for testing
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized. Please login.'}), 403

    topic = request.json.get('topic')
    category = request.json.get('category', 'Training')
    featured_image = request.json.get('image')
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    # Try to fetch a relevant image from NewsAPI based on the topic
    if not featured_image or 'unsplash' in featured_image:
        news_api_key = current_app.config.get('NEWS_API_KEY', '')
        if news_api_key and news_api_key != 'DEMO_MODE':
            try:
                import urllib.parse
                import urllib.request
                import json
                query = urllib.parse.quote(f"{topic} fitness")
                url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=relevance&pageSize=5&apiKey={news_api_key}"
                req_obj = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_obj, timeout=5) as response:
                    news_data = json.loads(response.read().decode())
                    if news_data.get('status') == 'ok' and news_data.get('articles'):
                        for article in news_data['articles']:
                            if article.get('urlToImage'):
                                featured_image = article['urlToImage']
                                break
            except Exception as e:
                print(f"Failed to fetch dynamic image from NewsAPI: {e}")
                
    if not featured_image:
        featured_image = 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200'

    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'Gemini API Key is missing in configuration'}), 500

    try:
        # Configure Gemini SDK
        genai.configure(api_key=api_key)
        
        # Auto-discover available models to avoid 404 errors
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            print(f"Auto-discovered Gemini models: {available_models}")
        except Exception as e:
            print(f"Model discovery failed: {e}")
            # Fallback to defaults if listing fails
            available_models = ['models/gemini-1.5-flash', 'models/gemini-pro']

        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        content = None
        used_model = ""
        detailed_errors = []

        for model_path in available_models:
            try:
                # Clean model name (some return with 'models/' prefix, some without)
                model_name = model_path.split('/')[-1]
                
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
                
                model = genai.GenerativeModel(model_name, safety_settings=safety_settings)
                
                # Enhanced Expert Persona Prompt
                prompt_context = ""
                if category == 'Training':
                    from ...models.exercise import Exercise
                    # Try to find a related exercise to ground the AI
                    import random
                    exercise = Exercise.query.filter(Exercise.name.ilike(f'%{topic}%')).first()
                    if not exercise:
                        # Pick a random exercise to add flavor if topic is generic
                        all_ex = Exercise.query.limit(50).all()
                        if all_ex: exercise = random.choice(all_ex)
                    
                    if exercise:
                        prompt_context = f"Reference Data for accuracy: Exercise: {exercise.name}, Primary Muscles: {', '.join(exercise.primary_muscles)}, Level: {exercise.level}. Include these physiological details in your advice. "

                lang_instruction = "IMPORTANT: Write EVERYTHING (title, html_content, excerpt) in English."

                prompt = (
                    f"You are a world-class Elite Performance Scientist and Peak Performance Coach. {lang_instruction} "
                    f"Write a sophisticated, academically-rigorous, yet highly engaging expert article about '{topic}' for the '{category}' category. "
                    f"{prompt_context}"
                    "Use a professional, authoritative, and clinical yet motivating tone. "
                    "Include physiological mechanisms, biomechanical insights, and evidence-based protocols. "
                    "Output exactly ONE SINGLE JSON object. DO NOT include any text before or after the JSON. "
                    "The JSON must have exactly two fields: "
                    "1. 'html_content': The full article in raw HTML (using <h2>, <h3>, <p>, <ul>, <li>, <strong>, <blockquote>). "
                    "Ensure headings are thought-provoking and use sophisticated vocabulary (e.g., instead of 'Tips', use 'Strategic Protocols' or 'Biomechanical Considerations'). "
                    "2. 'excerpt': A concise, high-level executive summary (2 lines). "
                    "The article should be approximately 800 words with deep technical detail."
                )
                response = model.generate_content(prompt)
                
                if response.text:
                    content, excerpt = extract_ai_content(response.text, topic)
                    if content:
                        used_model = model_name
                        break
                
            except Exception as e:
                print(f"Generation Error: {e}")
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
            return jsonify({'error': f"AI Failed. Available models were: {available_models}. Errors: {' | '.join(detailed_errors)}"}), 500
        
        # Create slug
        slug = topic.lower().replace(' ', '-').replace('/', '-')[:50]
        
        # Ensure slug uniqueness
        base_slug = slug
        counter = 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Extract excerpt
        import re
        clean_text = re.sub('<[^<]+?>', '', content)
        excerpt = clean_text[:200].strip() + "..."

        # Create DB Record
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
        
        if featured_image and len(featured_image) < 200:
            new_post.featured_image = featured_image

        db.session.add(new_post)
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': f'Article generated successfully using {used_model}!',
            'slug': slug
        })

    except Exception as e:
        print(f"AI Generation Error (SDK): {str(e)}")
        return jsonify({'error': f"AI Error: {str(e)}"}), 500

@blog_bp.route('/ask-expert', methods=['POST'])
def ask_expert():
    """Handles real-time chat with the AI Expert"""
    question = request.json.get('question')
    if not question:
        return jsonify({'error': 'Question is required'}), 400

    api_key = current_app.config.get('GEMINI_API_KEY')
    answer = None

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            prompt = f"You are a world-class Peak Performance Coach and Fitness Expert. Answer the following user question concisely and professionally: '{question}'"
            response = model.generate_content(prompt)
            if response.text:
                answer = response.text
        except Exception as e:
            print(f"Gemini Chat Error: {e}")

    # DeepSeek Fallback
    if not answer:
        deepseek_key = current_app.config.get('DEEPSEEK_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
        if deepseek_key:
            try:
                import requests as req
                headers = {
                    "Authorization": f"Bearer {deepseek_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a world-class Peak Performance Coach and Fitness Expert. Answer concisely."},
                        {"role": "user", "content": question}
                    ]
                }
                ds_response = req.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=10)
                if ds_response.status_code == 200:
                    ds_data = ds_response.json()
                    answer = ds_data['choices'][0]['message']['content']
            except Exception as e:
                print(f"DeepSeek Chat Error: {e}")

    if not answer:
        return jsonify({'error': 'Expert is currently unavailable. Please try again later.'}), 500

    return jsonify({'success': True, 'answer': answer})
