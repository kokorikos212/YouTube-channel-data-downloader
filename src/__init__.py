import os, sys, json
import logging
from class_create_Database import Database

from dotenv import load_dotenv
load_dotenv()

def basic_config(standart_input_path="../data/StandartInput.json"):
    """Loads configuration from a JSON file and sets up logging.

    Returns:
        tuple: A tuple containing the YouTube API key, database name,
               proxy file path, and YouTube channel IDs.
    """
    print("__basic_config__")
    print() 
    youtube_api_key = []
    database_manager = None  
    proxy_file_path = None
 
    try:
        # Load environment variables from .env file
        # youtube_api_key = os.getenv("API_KEY", "").split("," )
        # database_path = os.getenv("DATABASE_PATH")
        # yt_channel_ids = os.getenv("YT_CHANNEL_IDS", "").split(",")

        file_path = os.path.join(os.path.dirname(__file__), standart_input_path)
        with open(file_path, 'r') as file:
            config = json.load(file)
            youtube_api_key = config["api_key"]
            database_path = config["database_path"]
            yt_channel_ids = config["yt_channel_ids"]
        

        # Print the extracted configuration values
        print(f"API Key: {youtube_api_key}\nDatabase Name: {database_path}\nProxy File Path: {proxy_file_path}\nYouTube Channel IDs: {yt_channel_ids}")

        # Check essential values
        if not youtube_api_key:
            logging.warning("YouTube API key is missing in environment variables.")
        if not database_path:
            logging.warning("Database path is missing in environment variables.")
        if not yt_channel_ids or yt_channel_ids == ['']:  # Check for empty list
            logging.warning("YouTube channel IDs are missing in environment variables.")
        
        # Log the loaded configuration values
        logging.info("Loaded configuration data from environment variables.")

        # Initialize database
        if database_path:
            database_manager = Database(database_path)

            logging.info(f"Database '{database_path}' created successfully.")

        # Return the loaded configuration values
        return youtube_api_key, database_manager, yt_channel_ids

    except Exception as e:
        logging.error(f"An error occurred during configuration: {e}")
        sys.exit(1)  

# youtube_api_key, database_manager, yt_channel_ids = basic_config()  
# print(youtube_api_key, database_manager, yt_channel_ids) 
