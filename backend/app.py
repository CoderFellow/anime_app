import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import or_
import requests
from file_service import save_uploaded_file, allowed_file

# Initialize the Flask application
app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anime_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure the directory where uploaded files will be saved
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure the maximum file size (in bytes). Example: 500 MB
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# Initialize the SQLAlchemy extension
db = SQLAlchemy(app)

# Initialize Flask-HTTPAuth
auth = HTTPBasicAuth()

# Hardcoded user credentials for demonstration purposes
USERS = {
    "admin": "secret"
}

# Define a function to verify the username and password
@auth.verify_password
def verify_password(username, password):
    if username in USERS and USERS[username] == password:
        return username
    return None

# Define a model (database table: Anime)
class Anime(db.Model):
    anime_id = db.Column(db.Integer, primary_key=True)
    anime_title = db.Column(db.String(80), unique=True, nullable=False)
    anime_file_path = db.Column(db.String(140), unique=True, nullable=False)
    anime_description = db.Column(db.String(150), unique=False, nullable=True)

    def __repr__(self):
        return f'<Anime {self.anime_title}>'

# Create the database and tables within the application context
with app.app_context():
    db.create_all()

# New function to add anime to the database
def add_anime_to_db(anime_title, anime_file_path, anime_description):
    new_anime = Anime(
        anime_title=anime_title,
        anime_file_path=anime_file_path,
        anime_description=anime_description
    )
    db.session.add(new_anime)
    db.session.commit()
    return new_anime

# New function to search the database
def search_anime_db(search_term):
    result = Anime.query.filter(or_(
        Anime.anime_title.ilike(f"%{search_term}%"),
        Anime.anime_description.ilike(f"%{search_term}%")
    )).all()
    return result

# START: Modified upload endpoint for file validation and database function call
@app.route('/api/upload', methods=['POST'])
@auth.login_required
def upload_anime():
    """
    This function handles the process of uploading anime files and saving
    their metadata to the database.
    """
    # Check if the title was provided in the form data
    anime_title = request.form.get('anime_title')
    anime_description = request.form.get('anime_description')
    if not anime_title:
        return jsonify({"error": "Anime title is required"}), 400

    # Check if a file was uploaded in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if the filename is empty or has an invalid extension
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file. Only .mp4, .mkv, .mov, and .avi files are allowed."}), 400

    try:
        # Use the new service to save the file
        filepath = save_uploaded_file(file)

        if filepath:
            # Add the new anime to the database using the returned filepath
            new_anime = add_anime_to_db(anime_title, filepath, anime_description)
            
            return jsonify({
                "message": "File uploaded and metadata saved successfully",
                "anime_id": new_anime.anime_id,
                "title": new_anime.anime_title,
                "filepath": new_anime.anime_file_path
            }), 201
        else:
            return jsonify({"error": "Failed to save file. Check file type."}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Add a handler for the file size limit error
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File size exceeds the 500 MB limit."}), 413

# END: Modified upload endpoint for file validation and database function call

# New route to get a list of all anime from the database
@app.route('/api/anime', methods=['GET'])
def get_anime_list():
    """
    This function retrieves a list of all anime entries from the database
    and returns them as a JSON response.
    """
    try:
        # Query the database for all Anime records
        anime_list = Anime.query.all()
        
        # Serialize the list of objects into a list of dictionaries
        anime_data = [{
            "anime_id": anime.anime_id,
            "anime_title": anime.anime_title,
            "anime_file_path": anime.anime_file_path,
            "anime_description": anime.anime_description
        } for anime in anime_list]
        
        return jsonify(anime_data), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
        
# START: New search endpoint
@app.route('/api/search', methods=['GET'])
def search_anime():
    """
    This function handles searching for anime by title or description.
    """
    search_term = request.args.get('q')

    if not search_term:
        return jsonify({"error": "Bad Request: Search term is missing."}), 400

    search_results = search_anime_db(search_term)

    if not search_results:
        return jsonify({"message": "No matching anime found."}), 200

    # Serialize the search results into a list of dictionaries
    results_list = []
    for anime in search_results:
        results_list.append({
            "anime_id": anime.anime_id,
            "anime_title": anime.anime_title,
            "anime_file_path": anime.anime_file_path,
            "anime_description": anime.anime_description
        })

    return jsonify(results_list), 200
# END: New search endpoint

# START: New news endpoint
@app.route('/api/news', methods=['GET'])
def get_anime_news():
    """
    This function retrieves the latest anime news from an external API
    and returns it to the client.
    """
    try:
        response = requests.get("https://api.jikan.moe/v4/news")
        response.raise_for_status() # Raises an HTTPError if the status code is bad

        # Get the JSON data from the response
        news_data = response.json()
        
        # Return the data as a JSON response
        return jsonify(news_data), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to retrieve news: {str(e)}"}), 500
# END: New news endpoint

if __name__ == '__main__':
    """
    Main function that activates the app.py file.
    """
    app.run(debug=True)
