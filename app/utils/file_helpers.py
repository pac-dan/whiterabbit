"""
File upload security utilities
"""
import os
import imghdr
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """
    Check if a file has an allowed extension
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if file extension is allowed
    """
    if not filename or '.' not in filename:
        return False
    
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
    return filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_image(file_stream):
    """
    Validate that uploaded file is actually an image (MIME type check)
    
    Args:
        file_stream: File stream to validate
        
    Returns:
        str: Image format if valid, None otherwise
    """
    header = file_stream.read(512)
    file_stream.seek(0)  # Reset stream position
    format = imghdr.what(None, header)
    
    if not format:
        return None
    
    # Only allow specific image formats
    allowed_formats = ['jpeg', 'jpg', 'png', 'gif', 'webp']
    return format if format.lower() in allowed_formats else None


def save_uploaded_file(file, subfolder='', validate_image_type=True):
    """
    Securely save an uploaded file with validation
    
    Args:
        file: FileStorage object from request.files
        subfolder: Optional subfolder within UPLOAD_FOLDER
        validate_image_type: If True, validate image files are actually images
        
    Returns:
        str: Relative path to saved file, or None if save failed
        
    Raises:
        ValueError: If file type not allowed or filename invalid
    """
    if not file or not file.filename:
        raise ValueError("No file provided")
    
    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed types: {current_app.config.get('ALLOWED_EXTENSIONS')}")
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Validate image files to prevent malicious uploads
    if validate_image_type:
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            if not validate_image(file.stream):
                raise ValueError("File is not a valid image or format not supported")
    
    if not filename:
        raise ValueError("Invalid filename after security check")
    
    # Create upload directory if it doesn't exist
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    if subfolder:
        upload_folder = os.path.join(upload_folder, subfolder)
    
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate unique filename if file exists
    base, ext = os.path.splitext(filename)
    counter = 1
    final_filename = filename
    
    while os.path.exists(os.path.join(upload_folder, final_filename)):
        final_filename = f"{base}_{counter}{ext}"
        counter += 1
    
    # Save file
    filepath = os.path.join(upload_folder, final_filename)
    file.save(filepath)
    
    # Return relative path for storage in database
    if subfolder:
        return os.path.join(subfolder, final_filename).replace('\\', '/')
    return final_filename


def delete_file(filepath):
    """
    Safely delete an uploaded file
    
    Args:
        filepath: Relative path to file (from database)
        
    Returns:
        bool: True if file was deleted, False otherwise
    """
    if not filepath:
        return False
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    full_path = os.path.join(upload_folder, filepath)
    
    # Prevent directory traversal
    if not os.path.abspath(full_path).startswith(os.path.abspath(upload_folder)):
        current_app.logger.warning(f"Attempted directory traversal: {filepath}")
        return False
    
    try:
        if os.path.exists(full_path) and os.path.isfile(full_path):
            os.remove(full_path)
            return True
    except Exception as e:
        current_app.logger.error(f"Error deleting file {filepath}: {str(e)}")
    
    return False

