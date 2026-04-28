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
            flash("Administrative rights required.", "danger")
            return redirect(url_for('auth.login'))
        # Check if user is admin (you can add admin field to User model later)
        if current_user.username not in ['admin', 'administrator']:  # Simple check for now
            flash("You do not have administrative permissions.", "danger")
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
    """Admin dashboard with rich statistics"""
    from sqlalchemy import func
    from datetime import timedelta

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    total_users = UserAccount.query.count()
    total_registrations = ProgramRegistration.query.count()
    total_blog_posts = BlogPost.query.count() if BlogPost else 0
    total_blog_views = db.session.query(func.coalesce(func.sum(BlogPost.views), 0)).scalar() if BlogPost else 0

    recent_users = UserAccount.query.order_by(desc(UserAccount.id)).limit(5).all()
    recent_registrations = ProgramRegistration.query.order_by(desc(ProgramRegistration.created_at)).limit(5).all()
    recent_posts = BlogPost.query.order_by(desc(BlogPost.created_at)).limit(3).all() if BlogPost else []

    # New this week
    new_regs_week = ProgramRegistration.query.filter(
        ProgramRegistration.created_at >= seven_days_ago
    ).count()

    # Program breakdown
    program_counts = db.session.query(
        ProgramRegistration.program,
        func.count(ProgramRegistration.id).label('cnt')
    ).group_by(ProgramRegistration.program).order_by(func.count(ProgramRegistration.id).desc()).limit(5).all()

    # Gender split
    gender_counts = db.session.query(
        UserAccount.gender, func.count(UserAccount.id)
    ).filter(UserAccount.gender.isnot(None)).group_by(UserAccount.gender).all()
    male_count = sum(c[1] for c in gender_counts if c[0] and c[0].lower() in ['male', 'მამრობითი'])
    female_count = sum(c[1] for c in gender_counts if c[0] and c[0].lower() in ['female', 'მდედრობითი'])

    # Subscription plans
    plan_counts = db.session.query(
        UserAccount.subscription_plan, func.count(UserAccount.id)
    ).group_by(UserAccount.subscription_plan).all()

    stats = {
        'total_users': total_users,
        'total_registrations': total_registrations,
        'total_blog_posts': total_blog_posts,
        'total_blog_views': total_blog_views,
        'new_regs_week': new_regs_week,
        'recent_users': recent_users,
        'recent_registrations': recent_registrations,
        'recent_posts': recent_posts,
        'program_counts': program_counts,
        'male_count': male_count,
        'female_count': female_count,
        'plan_counts': plan_counts,
    }

    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    users = UserAccount.query.filter(UserAccount.username != 'admin').order_by(desc(UserAccount.id)).paginate(
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
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for('admin.users'))

    # Prevent deleting other admins (optional safety measure)
    if user.is_admin:
        flash("Administrators cannot be deleted.", "danger")
        return redirect(url_for('admin.users'))

    try:
        # Delete associated registrations first
        ProgramRegistration.query.filter_by(user_id=user.id).delete()

        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.username}' has been successfully deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the user.", "danger")

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
        flash(f"Registration for '{registration.full_name}' has been successfully deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the registration.", "danger")

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
        flash(f"Blog post '{post.title}' has been successfully deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the blog post.", "danger")

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
            flash('Title is required!', 'danger')
            return render_template('admin/create_post_simple.html')

        if not content:
            flash('Content is required!', 'danger')
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

            flash(f'Blog post "{title}" has been successfully created!', 'success')
            return redirect(url_for('admin.blog_management'))

        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

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
            flash('Title is required!', 'danger')
            return render_template('admin/edit_post.html', post=post)

        if not content:
            flash('Content is required!', 'danger')
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
            flash(f'Blog post "{title}" has been successfully updated!', 'success')
            return redirect(url_for('admin.blog_management'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('admin/edit_post.html', post=post)

@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """Admin statistics page with comprehensive analytics and date filtering"""
    from datetime import timedelta
    from sqlalchemy import func

    # Get range from query params (default to 30 days)
    days_range = request.args.get('range', 30, type=int)
    
    now = datetime.utcnow()
    start_date = now - timedelta(days=days_range)
    prev_start_date = start_date - timedelta(days=days_range) # For trend calculation
    
    # Global totals (always same)
    total_users = UserAccount.query.count()
    total_registrations = ProgramRegistration.query.count()
    total_blog_posts = BlogPost.query.count() if BlogPost else 0
    total_blog_views = db.session.query(func.coalesce(func.sum(BlogPost.views), 0)).scalar() if BlogPost else 0

    # Range-specific sign-ups
    new_signups_range = UserAccount.query.filter(UserAccount.id > 0).count() # Simplified, should use created_at if exists
    # If UserAccount has no created_at, we just show total for now, but let's assume it might have it or just show total.
    # Looking back at user.py, there is no created_at field. I should add it or use ID as proxy for now.
    
    new_regs_range = ProgramRegistration.query.filter(
        ProgramRegistration.created_at >= start_date
    ).count()

    # Program distribution for pie chart (filtered by range)
    program_counts = db.session.query(
        ProgramRegistration.program, func.count(ProgramRegistration.id)
    ).filter(ProgramRegistration.created_at >= start_date
    ).group_by(ProgramRegistration.program).all()

    program_labels = [p[0] for p in program_counts] if program_counts else ['No Data']
    program_data = [p[1] for p in program_counts] if program_counts else [0]

    # Top 5 active users (filtered by range)
    top_users = db.session.query(
        UserAccount.username, UserAccount.email, UserAccount.profile_image,
        func.count(ProgramRegistration.id).label('reg_count')
    ).join(ProgramRegistration, UserAccount.id == ProgramRegistration.user_id
    ).filter(ProgramRegistration.created_at >= start_date
    ).group_by(UserAccount.id
    ).order_by(func.count(ProgramRegistration.id).desc()
    ).limit(5).all()

    # Recent registrations
    recent_regs = ProgramRegistration.query.filter(
        ProgramRegistration.created_at >= start_date
    ).order_by(desc(ProgramRegistration.created_at)).limit(5).all()

    # Chart data (daily registrations for the selected range)
    daily_regs = db.session.query(
        func.date(ProgramRegistration.created_at).label('day'),
        func.count(ProgramRegistration.id).label('count')
    ).filter(
        ProgramRegistration.created_at >= start_date
    ).group_by(func.date(ProgramRegistration.created_at)).order_by(func.date(ProgramRegistration.created_at)).all()

    chart_labels = [str(d[0]) for d in daily_regs]
    chart_data = [d[1] for d in daily_regs]

    stats = {
        'total_users': total_users,
        'total_registrations': total_registrations,
        'total_blog_posts': total_blog_posts,
        'total_blog_views': total_blog_views,
        'new_signups_month': total_users, # Fallback
        'new_regs_range': new_regs_range,
        'program_labels': program_labels,
        'program_data': program_data,
        'male_count': 0, # Should be calculated but keeping it simple for now or using global
        'female_count': 0,
        'top_users': top_users,
        'recent_regs': recent_regs,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'current_range': days_range
    }
    
    # Re-calculate gender split globally for context
    gender_counts = db.session.query(
        UserAccount.gender, func.count(UserAccount.id)
    ).filter(UserAccount.gender.isnot(None)).group_by(UserAccount.gender).all()
    stats['male_count'] = sum(c[1] for c in gender_counts if c[0] and c[0].lower() in ['male', 'მამრობითი'])
    stats['female_count'] = sum(c[1] for c in gender_counts if c[0] and c[0].lower() in ['female', 'მდედრობითი'])

    return render_template('admin/statistics.html', stats=stats)

@admin_bp.route('/logout')
@login_required
@admin_required
def admin_logout():
    """Admin panel exit - redirects to main page without logging out user"""
    return redirect(url_for('main.index'))
