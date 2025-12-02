from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from functools import wraps
from . import blog_bp
from ...models.blog import BlogPost
from ...extensions import db

@blog_bp.route('/')
def index():
    """Blog index page with all published posts"""
    page = request.args.get('page', 1, type=int)

    # First page shows 9 posts, subsequent pages show 6
    per_page = 9 if page == 1 else 6
    offset = 0 if page == 1 else 9 + (page - 2) * 6

    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).offset(offset).limit(per_page).all()

    # Check if there are more posts
    total_posts = BlogPost.query.filter_by(published=True).count()
    has_more = offset + per_page < total_posts

    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        posts_data = []
        for post in posts:
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'excerpt': post.excerpt or (post.content[:150] + '...' if len(post.content) > 150 else post.content),
                'slug': post.slug,
                'featured_image': post.featured_image,
                'author_name': post.author.name if post.author else 'Admin',
                'created_at': post.created_at.strftime('%d.%m.%Y'),
                'views': post.views or 0
            })

        return jsonify({
            'posts': posts_data,
            'has_more': has_more,
            'next_page': page + 1 if has_more else None
        })

    return render_template('blog/index.html', posts=posts, has_more=has_more, current_page=page)

@blog_bp.route('/post/<slug>')
def post_detail(slug):
    """Individual blog post page"""
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    post.increment_views()

    # Get related posts (excluding current post)
    related_posts = BlogPost.query.filter(
        BlogPost.published == True,
        BlogPost.id != post.id
    ).order_by(BlogPost.created_at.desc()).limit(5).all()

    return render_template('blog/post_detail.html', post=post, related_posts=related_posts)
