import urllib.request
import json
import datetime
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

def guess_category(title):
    t = title.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return cat
    return 'Training'

def sync_fitness_news():
    api_key = current_app.config.get('NEWS_API_KEY', '') 
    
    if api_key and api_key != 'DEMO_MODE':
        now = datetime.datetime.now()
        # Rate limit the sync to once every 10 minutes (600 seconds)
        if NEWS_CACHE['timestamp']:
            if (now - NEWS_CACHE['timestamp']).total_seconds() < 600:
                return

        try:
            import urllib.parse
            # Strict query: Must contain 'workout' and at least one of (fitness, gym, exercises)
            query = urllib.parse.quote("workout AND (fitness OR gym OR exercises)")
            url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=100&apiKey={api_key}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                if data.get('status') == 'ok':
                    from ...models.user import UserAccount
                    admin = UserAccount.query.filter(UserAccount.username.in_(['admin', 'administrator'])).first()
                    if not admin:
                        admin = UserAccount.query.first()
                        
                    if not admin:
                        return
                        
                    for idx, article in enumerate(data.get('articles', [])):
                        if not article.get('urlToImage'): 
                            continue
                            
                        # Create unique slug to identify API posts
                        clean_title = article.get('title', '').lower().replace(' ', '-').replace('/', '-')[:30]
                        slug = f"api-news-{clean_title}"
                        
                        # Check if already saved
                        if BlogPost.query.filter_by(slug=slug).first():
                            continue
                            
                        try:
                            pub_date_obj = datetime.datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                        except:
                            pub_date_obj = now

                        import re
                        raw_content = article.get('content') or article.get('description', '')
                        clean_content = re.sub(r'\[\+\d+\s+chars\]', '', raw_content).strip()

                        content_html = f"<p>{clean_content}</p><br><p><a href='{article.get('url')}' target='_blank' style='display:inline-block; padding:12px 24px; background:var(--primary-color); color:white; text-decoration:none; border-radius:12px; font-weight:bold;'>Read Full Article</a></p>"

                        new_post = BlogPost(
                            title=article.get('title', 'Fitness News'),
                            content=content_html,
                            excerpt=article.get('description', '')[:150] + '...',
                            slug=slug,
                            featured_image=article.get('urlToImage'),
                            category=guess_category(article.get('title', '')),
                            author_id=admin.id,
                            author_name=article.get('author')[:100] if article.get('author') else 'Fitness Expert',
                            created_at=pub_date_obj,
                            published=True,
                            views=1000 + idx * 50
                        )
                        db.session.add(new_post)
                        
                    db.session.commit()
                    NEWS_CACHE['timestamp'] = now
                    
                    # Cleanup: Ensure only 20 latest API posts exist
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
    sync_fitness_news()

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
            'created_at': db_post.created_at.strftime('%d.%m.%Y'),
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
        'content': db_post.content,
        'featured_image': db_post.featured_image if db_post.featured_image and db_post.featured_image.startswith('http') else (url_for('static', filename='images/blog/' + db_post.featured_image) if db_post.featured_image else 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200'),
        'author_name': author_name,
        'created_at': db_post.created_at.strftime('%d.%m.%Y'),
        'reading_time': db_post.reading_time or 5
    }

    return render_template('blog/post_detail.html', post=post)

@blog_bp.route('/generate-ai-post', methods=['POST'])
@login_required
def generate_ai_post():
    """Generates a full blog post using Google Gemini AI SDK and saves it to DB"""
    import google.generativeai as genai
    
    # Simple admin check - allowing current logged in user for testing
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized. Please login.'}), 403

    topic = request.json.get('topic')
    featured_image = request.json.get('image', 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200')
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

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
                prompt = (
                    f"Write a professional, highly engaging, and comprehensive fitness blog article about '{topic}'. "
                    "Output ONLY a JSON object with two fields: "
                    "1. 'html_content': The full article in raw HTML (using <h2>, <h3>, <p>, <ul>, <li>, <strong>). "
                    "2. 'excerpt': A short 2-line summary. "
                    "The article should be at least 600 words with clear headings."
                )
                response = model.generate_content(prompt)
                
                if response.text:
                    # Improved Parsing: Use regex to extract JSON block if wrapped in markers
                    import re as pyre
                    json_match = pyre.search(r'\{.*\}', response.text, pyre.DOTALL)
                    if json_match:
                        raw_text = json_match.group()
                    else:
                        raw_text = response.text.replace('```json', '').replace('```', '').strip()

                    try:
                        import json as pyjson
                        ai_data = pyjson.loads(raw_text)
                        content = ai_data.get('html_content', '')
                        excerpt = ai_data.get('excerpt', topic + "...")
                        
                        used_model = model_name
                        break
                    except Exception as parse_error:
                        # Final fallback: if it's still JSON-like but failed to parse, 
                        # try to extract content field manually or just use text
                        print(f"JSON Parse Error: {parse_error}")
                        if '"html_content":' in response.text:
                            # Try simple extraction
                            match = pyre.search(r'"html_content":\s*"(.*?)",', response.text, pyre.DOTALL)
                            if match:
                                content = match.group(1).replace('\\n', '\n').replace('\\"', '"')
                            else:
                                content = response.text
                        else:
                            content = response.text
                        
                        excerpt = topic + "..."
                        used_model = model_name
                        break
            except Exception as e:
                detailed_errors.append(f"{model_path} Error: {str(e)}")
                continue

        if not content:
            return jsonify({'error': f"AI Failed. Available models were: {available_models}. Errors: {' | '.join(detailed_errors)}"}), 500
        
        # Basic cleanup if AI still includes markdown markers
        content = content.replace('```html', '').replace('```', '').strip()

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
            featured_image=None, 
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
