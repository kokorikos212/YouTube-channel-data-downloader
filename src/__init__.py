import os
import sys
import json
import logging
from dotenv import load_dotenv

# necessary classes and functions
from class_create_Database import Database
from class_YoutubeApiClient import YouTubeAPIClient
from class_YouTubePlaylist import YouTubePlaylist
from class_Save_data import DataSaver
from logging_config import logging_configuration
from utils import *

# Load environment variables
load_dotenv()

# Initialize logging
logging_configuration()

def basic_config(standart_input_path="../data/StandartInput.json"):
    """Loads configuration from a JSON file and initializes the database.

    Returns:
        tuple: A tuple containing the YouTube API key list, database manager instance,
               and YouTube channel IDs.
    """
    print("__basic_config__\n")

    youtube_api_key = []
    database_manager = None  

    try:
        # Construct the file path
        file_path = os.path.join(os.path.dirname(__file__), standart_input_path)

        # Load the JSON config file
        with open(file_path, 'r') as file:
            config = json.load(file)
            youtube_api_key = config.get("api_key", [])
            database_path = config.get("database_path", "")
            yt_channel_ids = config.get("yt_channel_ids", [])

        # Print extracted config values
        print(f"API Key: {youtube_api_key}\nDatabase Name: {database_path}\nYouTube Channel IDs: {yt_channel_ids}")

        # Validate critical configurations
        if not youtube_api_key:
            logging.warning("YouTube API key is missing in configuration.")
        if not database_path:
            logging.warning("Database path is missing in configuration.")
        if not yt_channel_ids:
            logging.warning("YouTube channel IDs are missing in configuration.")

        # Initialize database
        if database_path:
            database_manager = Database(database_path)
            logging.info(f"Database '{database_path}' initialized successfully.")

        return youtube_api_key, database_manager, yt_channel_ids

    except Exception as e:
        logging.error(f"An error occurred during configuration: {e}")
        sys.exit(1)

# Expose important elements when importing `__init__`
__all__ = [
    "basic_config",
    "YouTubeAPIClient",
    "YouTubePlaylist",
    "DataSaver",
    "Database",
    "logging_configuration",
    "sys",
    "logging",
    "json",
]
