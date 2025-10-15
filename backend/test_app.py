import base64
import pytest
import os # <--- import os is here
import tempfile # <---- import temp file is here
from flask_sqlalchemy import SQLAlchemy
from app import app, db as _db, Anime
from file_service import save_uploaded_file, allowed_file
from unittest import mock

AUTH_HEADER = 'Basic ' + base64.b64encode(b'admin:secret').decode('ascii')
AUTH_HEADERS = {'Authorization': AUTH_HEADER}

# test_app.py

from app import app, db as _db # Assuming you import 'db' as '_db' in your test file

# test_app.py

# test_app.py

# ... (Existing imports, ensure create_app and db are imported)
from app import create_app, db as _db, Anime 
# ...

@pytest.fixture(scope='function')
def app():
    """Creates a fresh application and configures it for testing."""
    # 1. Create a FRESH application instance
    _app = create_app() 
    
    # 2. Configure it for testing, OVERRIDING the production config
    temp_dir = tempfile.mkdtemp()
    _app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', # Override DB to SQLite
        'UPLOAD_FOLDER': temp_dir,
        'SQLALCHEMY_BINDS': {}, # The fix you just implemented
    })
    
    # db.init_app is already run inside create_app
    
    with _app.app_context():
        _db.create_all() # Create tables in the in-memory SQLite DB

    yield _app

    # Teardown: Clean up database and temp directory
    with _app.app_context():
        _db.drop_all()
        
    shutil.rmtree(temp_dir)


@pytest.fixture(scope='function')
def client(app): # Takes the clean app instance
    """Provides the test client."""
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def db(app): # Takes the clean app instance
    """Provides the database instance within the app context."""
    with app.app_context():
        yield _db

def test_anime_model_creation(db, headers = AUTH_HEADERS):
	"""
	Test the creation, persistence, and integrity of the Anime model.

	args:
		db: object

	returns:
		None
	"""	
	with app.app_context():
		# 1. Creation: Create an instance of the Anime model
		test_anime = Anime(
			anime_title="Test Title",
			anime_file_path="/test/path/file.mp4",
			anime_description="A test description"
		)

		# 2. Persistence: Add and commit the new object to the database
		db.session.add(test_anime)
		db.session.commit()

		# 3. Integrity: Query the database and verify the data
		retrieved_anime = db.session.get(Anime, 1) # Assumes the first ID is 1

		assert retrieved_anime is not None
		assert retrieved_anime.anime_title == "Test Title"
		assert retrieved_anime.anime_file_path == "/test/path/file.mp4"
		assert retrieved_anime.anime_description == "A test description"

def test_anime_list(db, client, headers = AUTH_HEADERS):
	"""
	This function tests the get_anime_list endpoint.

	args:
		db: database
		client: string

	returns:
		None
	"""
	# removed (none-existent): auth_header = 'Basic ' + base64.b64encode(b'admin:secret').decode('ascii')
	with app.app_context():
		# Set up test data with unique information
		test_anime_1 = Anime(
			anime_title="Attack on Titan",
			anime_file_path="/uploads/aot.mp4",
			anime_description="A gripping fantasy about humanity's fight for survival."
		)
		test_anime_2 = Anime(
			anime_title="My Hero Academia",
			anime_file_path="/uploads/mha.mkv",
			anime_description="A story about a superhero society and a boy with no powers."
		)

		# adding anime objects 1 and 2 
		db.session.add_all([test_anime_1, test_anime_2])

		# finalizing transactions.
		db.session.commit()

		# Make the request to the API
		response = client.get('/api/anime')

		# Check the status code
		assert response.status_code == 200

		# Verify the returned data
		data = response.get_json() 
		assert len(data) == 2

		# Verify the content of the first item
		assert data[0]['anime_title'] == "Attack on Titan"
		assert data[0]['anime_file_path'] == "/uploads/aot.mp4"

		# Verify the content of the second item
		assert data[1]['anime_title'] == "My Hero Academia"
		assert data[1]['anime_file_path'] == "/uploads/mha.mkv"
		
def test_upload_anime(db, client, headers = AUTH_HEADERS):
	"""
	This function tests the core functionalities of the upload anime function.

	args:
		db: object
		client: object

	returns:
		None
	"""
	
	mock_file = mock.MagicMock(filename='test.mp4')

	with mock.patch('app.save_uploaded_file', return_value='/uploads/test.mp4'):
		response = client.post(
			'/api/upload',
			data={'file': mock_file, 'anime_title': 'Test Anime', 'anime_description': 'A test anime description.'},
			headers={'Authorization': auth_header}
		)

	assert response.status_code == 201

	data = response.get_json()

	assert data['title'] == 'Test Anime'
	assert data['filepath'] == '/uploads/test.mp4'

	with app.app_context():
		new_anime = db.session.get(Anime, 1)
		assert new_anime.anime_title == 'Test Anime'

def test_missing_file(client, headers = AUTH_HEADERS):
	"""
	This function tests for a missing file function.

	args:
		client: object
		auth: object

	returns:
		None
	"""
	
	response = client.post(
		'/api/upload',
		data={'anime_title': 'Test File', 'anime_description': 'A test anime description.'},
		headers={'Authorization': auth_header}
	)
	assert response.status_code == 400
	assert response.get_json() == {'error': 'No file part in the request'}

def test_invalid_file_type_error(client, headers = AUTH_HEADERS):
	"""
	This function test for file type error

	args:
		client: object
		auth: object

	returns:
		None
	"""
	
	mock_file = mock.MagicMock(filename='image.jpg')
	response = client.post(
		'/api/upload',
		data={'file': mock_file, 'anime_title': 'Test File', 'anime_description': 'a test anime description.'},
		headers={'Authorization': auth_header}
	)
	assert response.status_code == 400
	assert response.get_json() == {'error': 'Invalid file. Only .mp4, .mkv, .mov, and .avi files are allowed.'}

def test_for_missing_title(client, headers = AUTH_HEADERS):
	"""
	This function tests for if an anime has a misssing title.

	args:
		client: object
		auth: object

	returns:
		None
	"""
	
	mock_file = mock.MagicMock(filename='video.mp4')
	with mock.patch('app.save_uploaded_file', return_value='/uploads/video.mp4'):
		response = client.post(
			'/api/upload',
			data={'file': mock_file, 'anime_description': 'test anime description.'},
			headers={'Authorization': auth_header}
		)
	assert response.status_code == 400
	assert response.get_json() == {'error': 'Anime title is required'}
