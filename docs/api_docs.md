Backend API Documentation

This API is designed to manage a database of anime, allowing users to upload new entries, browse a list of titles, search for specific entries, and retrieve the latest anime news. It is built using Python with the Flask framework and SQLAlchemy for database interaction.
API Endpoints
/api/upload

    HTTP Method: POST

    Description: This endpoint handles the upload of new anime files and saves their metadata to the database.

    Required Parameters:

        anime_title (form data): The title of the anime.

        anime_description (form data): A description of the anime.

        file (file upload): The video file to be uploaded.

    Expected Response: A JSON object confirming the successful upload and providing metadata about the new anime entry.

{
    "message": "File uploaded and metadata saved successfully",
    "anime_id": 1,
    "title": "My New Anime",
    "filepath": "uploads/my_new_anime.mp4"
}

/api/anime

    HTTP Method: GET

    Description: This endpoint retrieves a list of all anime entries from the database.

    Required Parameters: None

    Expected Response: A JSON array containing a list of anime entries.

[
  {
    "anime_id": 1,
    "anime_title": "My New Anime",
    "anime_file_path": "uploads/my_new_anime.mp4",
    "anime_description": "A great anime to watch."
  },
  {
    "anime_id": 2,
    "anime_title": "Another Anime",
    "anime_file_path": "uploads/another_anime.mkv",
    "anime_description": "A different great anime."
  }
]

/api/search

    HTTP Method: GET

    Description: This endpoint searches the database for anime entries by title or description.

    Required Parameters: q (query parameter): The search term.

    Expected Response: A JSON array containing a list of anime entries that match the search term. If no matches are found, an empty array is returned.

[
  {
    "anime_id": 1,
    "anime_title": "My New Anime",
    "anime_file_path": "uploads/my_new_anime.mp4",
    "anime_description": "A great anime to watch."
  }
]

/api/news

    HTTP Method: GET

    Description: retrieves the latest anime news from an external API and returns it to the client.

    Required Parameters: None

    Expected Response:
    
{
  "pagination": {
    "last_visible_page": 1,
    "has_next_page": false
  },
  "data": [
    {
      "mal_id": 123456,
      "title": "New 'One Piece' Film Announced",
      "url": "https://myanimelist.net/news/67890/new-one-piece-film-announced",
      "images": {
        "jpg": {
          "image_url": "https://cdn.myanimelist.net/images/news/5/67890.jpg"
        },
        "webp": {
          "image_url": "https://cdn.myanimelist.net/images/news/5/67890.webp"
        }
      },
      "date": "2023-10-27T17:00:00+00:00",
      "author_username": "MAL_News",
      "comments": 25,
      "excerpt": "A new One Piece movie has been officially announced for a 2024 release. The film will be a direct sequel to the recent 'One Piece Film: Red' and will feature...",
      "reactions": {
        "nice": 50,
        "love": 30,
        "confused": 5
      }
    },
    {
      "mal_id": 123457,
      "title": "Solo Leveling Anime Gets a Second Season",
      "url": "https://myanimelist.net/news/12345/solo-leveling-anime-gets-a-second-season",
      "images": {
        "jpg": {
          "image_url": "https://cdn.myanimelist.net/images/news/5/12345.jpg"
        },
        "webp": {
          "image_url": "https://cdn.myanimelist.net/images/news/5/12345.webp"
        }
      },
      "date": "2023-10-26T10:30:00+00:00",
      "author_username": "Anime_Fan",
      "comments": 150,
      "excerpt": "It has been confirmed that the popular anime series 'Solo Leveling' will be returning for a second season. The announcement was made on the official...",
      "reactions": {
        "nice": 120,
        "love": 200,
        "confused": 10
      }
    }
  ]
}
