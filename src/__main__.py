from __init__ import *

def start_init():
    try:
        youtube_api_key, database_manager, yt_channel_ids = basic_config()
        print(f"Database Name: {database_manager.db_filename}\nYouTube Channel IDs: {yt_channel_ids}")

        data_saver = DataSaver(database_manager)
        yt_extractor = YouTubeAPIClient(youtube_api_key, db_manager=database_manager)
        yt_playlist_extractor = YouTubePlaylist(youtube_api_key)

        for channel_id in yt_channel_ids: 
            try:
                channel_info = yt_extractor.get_channel_info(channel_id)
                data_saver.save_channel_info(channel_info)

                playlist_data = yt_playlist_extractor.get_channel_playlists(channel_id)
                data_saver.save_playlists_data(playlist_data)

            except Exception as e:
                logging.error(f"Error fetching channel info: {e}")
                continue  # Continue processing next channels instead of breaking

            channel_videoIds, _ = yt_extractor.get_all_video_ids_from_channel(channel_id)

            if channel_videoIds:
                for videoId in channel_videoIds:
                    try:
                        video_stats = yt_extractor.get_video_stats(videoId)
                        video_comments = yt_extractor.get_all_video_comments(videoId)
                        data_saver.save_video_data(video_stats, video_comments)

                    except Exception as e:
                        logging.error(f"Error fetching video data for {videoId}: {e}")
                        with open("checkpoint.json", "w") as f:
                            json.dump({"last_index": videoId, "video_ids_list": channel_videoIds}, f)

            else:
                print(f"No video IDs found for channel {channel_id}.")

        logging.info("Data collection completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_init()
