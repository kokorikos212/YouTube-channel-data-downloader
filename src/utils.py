import csv ,json 
import sys, os
from class_create_Database import Database
import logging
from dotenv import load_dotenv



def get_youtube_playlist_link(playlist_id):
    """
    Generate a YouTube link for a given playlist ID.

    Parameters:
    -----------
    playlist_id : str
        The unique identifier of the YouTube playlist.

    Returns:
    --------
    str
        The URL for the YouTube playlist.
    """
    base_url = "https://www.youtube.com/playlist?list="
    return f"{base_url}{playlist_id}"

# id = "UU6zqgjyGaf_b6nd3rqR7MUA"
# print( get_youtube_playlist_link(id)) 

def get_youtube_video_link(video_id: str) -> str:
    """
    Constructs the YouTube video URL from the given video ID.

    Args:
        video_id (str): The YouTube video ID.

    Returns:
        str: The URL of the YouTube video.
    """
    return f"https://www.youtube.com/watch?v={video_id}"

# video_id = "8iV9S6q6aRs"
# res = get_youtube_video_link(video_id)
# print(res) 

def checpoint_initiation(yt_video_ids):
    with open('data/checkpoint.json', 'r') as checpoint_file:
        checkpoint_dict = json.load(checpoint_file)
    last_processed_video_id = checkpoint_dict["last_processed_video_id"]
    last_processed_channel_id = checkpoint_dict["last_processed_channel_id"]

    def remaining_channels_and_video_ids():
        yt_channel_ids = os.getenv("YT_CHANNEL_IDS")

        position_of_last_processed_video_id = yt_video_ids.index(last_processed_video_id)
        print(yt_channel_ids)
        sys.exit() 
        position_of_last_processed_channel_id = yt_channel_ids.index(last_processed_channel_id) 

        remaining_videos = yt_channel_ids[position_of_last_processed_video_id + 1:]
        remaining_channels = yt_channel_ids[position_of_last_processed_channel_id + 1:] 

        return remaining_videos, remaining_channels 
    
    remaining_video_ids, remaining_channel_ids = remaining_channels_and_video_ids()
    yt_api_key = os.getenv("API_KEY")

    database_path = os.getenv("DATABASE_PATH")
    database_manager = Database(database_path)

    return yt_api_key, database_manager, remaining_channel_ids, remaining_video_ids 



# diem = "UCnMk-6Brd8rVEKWSWkwsWUg"
# api_key = "AIzaSyBeR-oaAWgXzWp41q-hcRWKBRc3byYNHWk"  
# yt_inst = YouTubeAPIClient(api_key) 
# res = yt_inst.get_channel_playlists(diem)  
# json_utils(res) 



