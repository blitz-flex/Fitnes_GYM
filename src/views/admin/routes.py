from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import desc
from datetime import datetime
import os
import uuid
from slugify import slugify
from . import admin_bp
from ...models.user import UserAccount
from ...models.registration import ProgramRegistration
from ...models.blog import BlogPost
from ...extensions import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("ადმინისტრაციული უფლებები საჭიროა.", "danger")
            return redirect(url_for('auth.login'))
        # Check if user is admin (you can add admin field to User model later)
        if current_user.username not in ['admin', 'administrator']:  # Simple check for now
            flash("ადმინისტრაციული უფლებები არ გაქვთ.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    total_users = UserAccount.query.count()
    total_registrations = ProgramRegistration.query.count()
    total_blog_posts = BlogPost.query.count() if BlogPost else 0
    recent_users = UserAccount.query.order_by(desc(UserAccount.id)).limit(3).all()
    recent_registrations = ProgramRegistration.query.order_by(desc(ProgramRegistration.created_at)).limit(3).all()

    stats = {
        'total_users': total_users,
        'total_registrations': total_registrations,
        'total_blog_posts': total_blog_posts,
        'recent_users': recent_users,
        'recent_registrations': recent_registrations
    }

    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    users = UserAccount.query.paginate(
        page=page, per_page=10, error_out=False)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = UserAccount.query.get_or_404(user_id)

    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash("საკუთარი ანგარიშის წაშლა შეუძლებელია.", "danger")
        return redirect(url_for('admin.users'))

    # Prevent deleting other admins (optional safety measure)
    if user.is_admin:
        flash("ადმინისტრატორის წაშლა შეუძლებელია.", "danger")
        return redirect(url_for('admin.users'))

    try:
        # Delete associated registrations first
        ProgramRegistration.query.filter_by(user_id=user.id).delete()

        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f"მომხმარებელი '{user.username}' წარმატებით წაიშალა.", "success")
    except Exception as e:
        db.session.rollback()
        flash("მომხმარებლის წაშლისას შეცდომა მოხდა.", "danger")

    return redirect(url_for('admin.users'))

@admin_bp.route('/registrations')
@login_required
@admin_required
def registrations():
    """Manage registrations"""
    page = request.args.get('page', 1, type=int)
    registrations = ProgramRegistration.query.order_by(desc(ProgramRegistration.created_at)).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('admin/registrations.html', registrations=registrations)

@admin_bp.route('/registrations/delete/<int:reg_id>', methods=['POST'])
@login_required
@admin_required
def delete_registration(reg_id):
    """Delete a registration"""
    registration = ProgramRegistration.query.get_or_404(reg_id)

    try:
        db.session.delete(registration)
        db.session.commit()
        flash(f"რეგისტრაცია '{registration.full_name}' წარმატებით წაიშალა.", "success")
    except Exception as e:
        db.session.rollback()
        flash("რეგისტრაციის წაშლისას შეცდომა მოხდა.", "danger")

    return redirect(url_for('admin.registrations'))

@admin_bp.route('/blog')
@login_required
@admin_required
def blog_management():
    """Manage blog posts"""
    try:
        posts = BlogPost.query.order_by(desc(BlogPost.created_at)).all()
    except:
        posts = []
    return render_template('admin/blog_management.html', posts=posts)

@admin_bp.route('/blog/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_post(id):
    """Delete a blog post"""
    try:
        post = BlogPost.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        flash(f"ბლოგ პოსტი '{post.title}' წარმატებით წაიშალა.", "success")
    except Exception as e:
        db.session.rollback()
        flash("ბლოგ პოსტის წაშლისას შეცდომა მოხდა.", "danger")

    return redirect(url_for('admin.blog_management'))

@admin_bp.route('/blog/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_post():
    """Create new blog post - simplified version"""
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        published = 'published' in request.form

        print(f"=== DEBUG CREATE POST ===")
        print(f"Title: '{title}'")
        print(f"Content length: {len(content)}")
        print(f"Published: {published}")
        print(f"Form keys: {list(request.form.keys())}")
        print(f"Current user ID: {current_user.id}")

        # Simple validation
        if not title:
            flash('სათაური აუცილებელია!', 'danger')
            return render_template('admin/create_post_simple.html')

        if not content:
            flash('შიგთავსი აუცილებელია!', 'danger')
            return render_template('admin/create_post_simple.html')

        try:
            # Handle image upload
            featured_image = None
            if 'featured_image' in request.files:
                file = request.files['featured_image']
                if file and file.filename and allowed_file(file.filename):
                    # Generate unique filename
                    filename = str(uuid.uuid4().hex) + '.' + file.filename.rsplit('.', 1)[1].lower()

                    # Ensure upload directory exists
                    upload_path = os.path.join('src', 'static', 'images', 'blog')
                    os.makedirs(upload_path, exist_ok=True)

                    # Save file
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    featured_image = filename
                    print(f"Image saved: {filename}")

            # Generate simple slug
            import time
            timestamp = int(time.time())
            slug = f"{slugify(title) or 'post'}-{timestamp}"

            print(f"Generated slug: {slug}")

            # Create post object
            post = BlogPost(
                title=title,
                content=content,
                excerpt=excerpt or content[:200] + '...' if len(content) > 200 else content,
                slug=slug,
                featured_image=featured_image,
                published=published,
                author_id=current_user.id
            )

            print(f"Created post object: {post}")

            # Save to database
            db.session.add(post)
            db.session.commit()

            print(f"Post saved successfully with ID: {post.id}")

            flash(f'ბლოგ პოსტი "{title}" წარმატებით შეიქმნა!', 'success')
            return redirect(url_for('admin.blog_management'))

        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            flash(f'შეცდომა: {str(e)}', 'danger')

    return render_template('admin/create_post_simple.html')

@admin_bp.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(post_id):
    """Edit existing blog post"""
    post = BlogPost.query.get_or_404(post_id)

    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        published = 'published' in request.form

        # Simple validation
        if not title:
            flash('სათაური აუცილებელია!', 'danger')
            return render_template('admin/edit_post.html', post=post)

        if not content:
            flash('შიგთავსი აუცილებელია!', 'danger')
            return render_template('admin/edit_post.html', post=post)

        try:
            # Handle image upload
            if 'featured_image' in request.files:
                file = request.files['featured_image']
                if file and file.filename and allowed_file(file.filename):
                    # Delete old image if exists
                    if post.featured_image:
                        old_image_path = os.path.join('src', 'static', 'images', 'blog', post.featured_image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)

                    # Generate unique filename
                    filename = str(uuid.uuid4().hex) + '.' + file.filename.rsplit('.', 1)[1].lower()

                    # Ensure upload directory exists
                    upload_path = os.path.join('src', 'static', 'images', 'blog')
                    os.makedirs(upload_path, exist_ok=True)

                    # Save file
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    post.featured_image = filename

            # Update post
            post.title = title
            post.content = content
            post.excerpt = excerpt or content[:200] + '...' if len(content) > 200 else content
            post.published = published

            # Update slug if title changed
            import time
            timestamp = int(time.time())
            post.slug = f"{slugify(title) or 'post'}-{timestamp}"

            db.session.commit()
            flash(f'ბლოგ პოსტი "{title}" წარმატებით განახლდა!', 'success')
            return redirect(url_for('admin.blog_management'))

        except Exception as e:
            db.session.rollback()
            flash(f'შეცდომა: {str(e)}', 'danger')

    return render_template('admin/edit_post.html', post=post)

@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """Admin statistics page"""
    stats = {
        'total_users': UserAccount.query.count(),
        'total_registrations': ProgramRegistration.query.count(),
        'total_blog_posts': BlogPost.query.count() if BlogPost else 0,
    }
    return render_template('admin/statistics.html', stats=stats)

@admin_bp.route('/logout')
@login_required
@admin_required
def admin_logout():
    """Admin panel exit - redirects to main page without logging out user"""
    return redirect(url_for('main.index'))
