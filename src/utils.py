from flask import flash
import os
import secrets
from PIL import Image
from flask import current_app

def flash_errors(form):
    """Display form validation errors as flash messages"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')


def save_picture(form_picture):

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)

    # We reduce the size of the image.
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_blog_picture(form_picture):
    """Save blog featured image with larger size"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    # Create blog images directory if it doesn't exist
    blog_images_dir = os.path.join(current_app.root_path, 'static', 'images', 'blog')
    if not os.path.exists(blog_images_dir):
        os.makedirs(blog_images_dir)

    picture_path = os.path.join(blog_images_dir, picture_fn)

    # Larger size for blog featured images
    output_size = (800, 600)
    i = Image.open(form_picture)

    # Keep aspect ratio and resize
    i.thumbnail(output_size, Image.Resampling.LANCZOS)

    # Save with good quality
    if i.mode in ("RGBA", "P"):
        i = i.convert("RGB")

    i.save(picture_path, quality=85, optimize=True)

    return picture_fn
