import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

# Define the directory where uploaded files will be saved
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure allowed file extensions for video uploads
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'mov', 'avi'}

def allowed_file(filename):
    """
    Checks if a file has an allowed video extension.
    
    Args:
        filename (str): The name of the file to check.
        
    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """
    Secures and saves an uploaded file to the server with a unique filename.
    
    Args:
        file (werkzeug.datastructures.FileStorage): The file to save.
        
    Returns:
        str: The new, unique file path on the server.
    """
    if file and allowed_file(file.filename):
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Generate a unique filename to prevent conflicts
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Construct the full file path
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file to the server
        file.save(filepath)
        
        return filepath
        
    return None
