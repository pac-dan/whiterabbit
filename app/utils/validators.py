"""
Input validation utilities for forms
"""
import re
from flask import flash


def validate_required(value, field_name):
    """Validate that a field is not empty"""
    if not value or (isinstance(value, str) and not value.strip()):
        flash(f'{field_name} is required.', 'danger')
        return False
    return True


def validate_price(price, min_value=0, max_value=100000):
    """Validate price is a positive number within range"""
    try:
        price_float = float(price)
        if price_float < min_value:
            flash(f'Price must be at least ${min_value}.', 'danger')
            return False
        if price_float > max_value:
            flash(f'Price cannot exceed ${max_value}.', 'danger')
            return False
        return True
    except (TypeError, ValueError):
        flash('Price must be a valid number.', 'danger')
        return False


def validate_integer(value, field_name, min_value=0, max_value=None):
    """Validate that value is an integer within range"""
    try:
        int_value = int(value)
        if int_value < min_value:
            flash(f'{field_name} must be at least {min_value}.', 'danger')
            return False
        if max_value and int_value > max_value:
            flash(f'{field_name} cannot exceed {max_value}.', 'danger')
            return False
        return True
    except (TypeError, ValueError):
        flash(f'{field_name} must be a valid number.', 'danger')
        return False


def validate_youtube_id(youtube_id):
    """Validate YouTube ID format"""
    if not youtube_id:
        return True  # Optional field
    
    # YouTube IDs are 11 characters (alphanumeric, dash, underscore)
    pattern = r'^[a-zA-Z0-9_-]{11}$'
    if not re.match(pattern, youtube_id):
        flash('Invalid YouTube ID format. Should be 11 characters.', 'danger')
        return False
    return True


def validate_url(url, field_name):
    """Validate URL format"""
    if not url:
        return True  # Optional field
    
    url_pattern = r'^https?://.+'
    if not re.match(url_pattern, url):
        flash(f'{field_name} must be a valid URL starting with http:// or https://', 'danger')
        return False
    return True


def validate_rating(rating):
    """Validate rating is 1-5"""
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            flash('Rating must be between 1 and 5 stars.', 'danger')
            return False
        return True
    except (TypeError, ValueError):
        flash('Rating must be a valid number.', 'danger')
        return False


def validate_text_length(text, field_name, min_length=None, max_length=None):
    """Validate text length"""
    if not text:
        return True  # Optional field or handled by validate_required
    
    text_length = len(text.strip())
    
    if min_length and text_length < min_length:
        flash(f'{field_name} must be at least {min_length} characters.', 'danger')
        return False
    
    if max_length and text_length > max_length:
        flash(f'{field_name} cannot exceed {max_length} characters.', 'danger')
        return False
    
    return True


def sanitize_string(value):
    """Sanitize string input by stripping whitespace"""
    if isinstance(value, str):
        return value.strip()
    return value

