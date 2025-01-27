from __init__ import basic_config
from logging_config import logging_configuration
from utils import *
from class_YoutubeApiClient import YouTubeAPIClient
from class_YouTubePlaylist import YouTubePlaylist
from class_Save_data import DataSaver
import sys, logging 


def statntart_init():
    try:
        youtube_api_key, database_manager, yt_channel_ids = basic_config() 
        print(database_manager) 
        print(f"Database Name: {database_manager.db_filename}\n YouTube Channel IDs: {yt_channel_ids}")

        data_saver = DataSaver(database_manager)
        

        yt_extractor = YouTubeAPIClient(youtube_api_key, db_manager=database_manager)
        yt_playlist_extractor = YouTubePlaylist(youtube_api_key)

        # Iterate over each channel
        for i, channel_id in enumerate(yt_channel_ids): 

            try:
                # Get channelrelated_channel_id = result[0] if result and result[0] is not None else None info and save them 
                channel_info = yt_extractor.get_channel_info(channel_id)
                data_saver.save_channel_info(channel_info)

                # Get playlist data and store them 
                playlist_data = yt_playlist_extractor.get_channel_playlists(channel_id)
                data_saver.save_playlists_data(playlist_data)

            except Exception as e:
                logging.error(f"Error fetching channel info: {e}")
                break

            # Retrieve all video IDs from the channel
            channel_videoIds, status = yt_extractor.get_all_video_ids_from_channel(channel_id)

            # Iterate over each video and save data
            if channel_videoIds:
                for videoId in channel_videoIds:
                    try:
                        video_stats = yt_extractor.get_video_stats(videoId)
                        video_comments = yt_extractor.get_all_video_comments(videoId)

                        data_saver.save_video_data(video_stats, video_comments)

                    except Exception as e:
                        logging.error(f"Error fetching video data for {videoId}: {e}")
            else:
                print("No video ids found for this channel. ")                            
            
        logging.info("Data collection completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)



if __name__ == "__main__":
    # Set up logging at the start of your application
    logging_configuration()
    logger = logging.getLogger(__name__)
    
    statntart_init()  