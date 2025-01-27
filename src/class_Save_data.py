import logging
import sqlite3 as sql
# import traceback
# import sys , json 
# from utils import get_youtube_video_link

from class_create_Database import Database
from json_utils import json_print

class DataSaver:
    """Handles saving data to the database."""

    def __init__(self, db_manager):
        """
        Initializes the DataSaver with a Database instance.
        
        Parameters
        ----------
        db_manager : Database
            An instance of Database to interact with.
        """
        self.db_manager = db_manager
        self.last_processed_video_id = None
        self.logger = logging.getLogger(__name__)

    def save_channel_info(self, channel_data):
        """
        Saves channel information to the SQL database.
        
        This method extracts relevant channel details from the provided dictionary and 
        inserts them into the 'Channels' table of the connected database. It handles 
        potential exceptions during database operations, logging the success or any errors encountered.

        Parameters
        ----------
        channel_data : dict
            A dictionary containing channel information. The expected structure includes:
                - channel_id (str): The unique identifier for the YouTube channel.
                - title (str): The title of the channel.
                - description (str): The description of the channel.
                - published_at (str): The publication date of the channel.
                - video_count (int): Total number of videos on the channel.
                - subscribers_count (int): Number of subscribers for the channel.
                - view_count (int): Total number of views for the channel.
        
        Raises
        ------
        Exception
            Logs an error if an exception occurs during the database operation, detailing
            the channel title and the nature of the error.
        
        Examples
        --------
        >>> channel_data = {
        ...     "channel_id": "UC123456789",
        ...     "title": "Example Channel",
        ...     "description": "A sample channel for educational purposes.",
        ...     "published_at": "2022-01-01",
        ...     "video_count": 100,
        ...     "subscribers_count": 1000,
        ...     "view_count": 50000
        ... }
        >>> data_saver.save_channel_info(channel_data)
        """
        try:
            # Extract channel data
            channel_id = channel_data.get("channelId", "Unknown ID")
            title = channel_data.get("title", "No Title")
            description = channel_data.get("description", None)
            published_at = channel_data.get("published_at", None)
            video_count = int(channel_data.get("video_count", -1))
            subscribers_count = int(channel_data.get("subscribers_count", -1))
            view_count = int(channel_data.get("view_count", None))
            # Log extracted information
            self.logger.debug(f"Channel data to save: id='{channel_id}', title='{title}', "
                        f"videos={video_count}, subscribers={subscribers_count}, views={view_count}")
            # Insert channel data into the database
            insert_channel_query = '''
                INSERT OR IGNORE INTO Channels (
                    channel_id, title, description, published_at, 
                    video_count, subscribers_count, view_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            '''.strip()
            self.db_manager.cursor.execute(insert_channel_query, (
                channel_id, title, description, published_at,
                video_count, subscribers_count, view_count
            ))
            # Commit the transaction
            self.db_manager.conn.commit()
            self.logger.info(f"Channel '{title}' data successfully saved to the database.")
        
        except Exception as e:
            self.logger.error(f"An error occurred while saving channel data for '{title}': {e}", exc_info=True)
            print(e) 

    def save_playlists_data(self, playlists):
        """
        Saves a list of playlists to the database.

        Parameters
        ----------
        playlists : list of dict
            A list of dictionaries where each dictionary represents a playlist.
            Example structure:
            [
                {
                    "playlist_title": "Example Playlist",
                    "playlist_description": "Description here",
                    "playlist_length": 25,
                    "playlist_publish_date": "2022-10-20T13:37:11.515231Z",
                    "related_channel_id": "UC123456789",
                    "playlist_link": "https://www.youtube.com/playlist?list=PL123456789",
                    "playlist_youtube_id": "PL123456789"
                }
            ]
        
        Returns
        -------
        int
            The number of playlists successfully saved.
        """
        successful_inserts = 0
        result = self.db_manager.cursor.execute("SELECT MAX(relational_channel_id) FROM Channels").fetchone()
        related_channel_id = result[0] if result and result[0] is not None else None

        # SQL query to insert playlist data
        query = '''
            INSERT OR IGNORE INTO Playlists 
            (playlist_title, playlist_description, playlist_length, playlist_publish_date,
             relational_channel_id, playlist_url, playlist_youtube_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''.strip()

        for playlist in playlists:
            try:
                # Insert playlist data
                self.db_manager.cursor.execute(
                    query,
                    (
                        playlist.get("playlist_title"),
                        playlist.get("playlist_description"),
                        playlist.get("playlist_length"),
                        playlist.get("playlist_publish_date"),
                        related_channel_id,   
                        playlist.get("playlist_youtube_id"),
                        "https://www.youtube.com/playlist?list=" + playlist.get("playlist_youtube_id") 
                    )
                )
                successful_inserts += 1
                self.logger.info("Successfully inserted playlist: %s", playlist.get("playlist_title"))
            except Exception as e:
                self.logger.error("Failed to insert playlist: %s. Error: %s", playlist.get("playlist_title"), e)

        # Commit the transaction
        self.db_manager.conn.commit()
        self.logger.info("Inserted %d playlists into the database.", successful_inserts)
        return successful_inserts
    
    def save_video_data(self, video_stats, video_comments, playlist_youtube_id="Not in plylist"):
        """Saves video information and comments to the SQL database.

        This method extracts relevant video statistics and comments from the provided
        dictionary and inserts them into the 'Vids' table of the connected database.
        It handles potential exceptions that may arise during the database operations,
        logging both the success of the operation and any errors encountered.

        Parameters
        ----------
        video_data : dict
            A dictionary containing video information. The expected structure includes:
            - video_info (dict): A dictionary with video details, such as:
                - title (str): The title of the video.
                - statistics (dict): A dictionary containing video statistics, which may include:
                    - viewCount (int): The number of views.
                    - likeCount (int): The number of likes.
                    - favoriteCount (int): The number of times the video is marked as a favorite.
                    - commentCount (int): The number of comments on the video.
                - duration_seconds (int): The length of the video in seconds.
                - publish_date (str): The date when the video was published.
            - comments (list): A list of comments associated with the video.

        playlist_id : int, optional
            The ID of the playlist to which the video belongs. If not specified, defaults to None.

        Raises
        ------
        Exception
            Logs an error if an exception occurs during the database operation, detailing
            the video title and the nature of the error.

        Notes
        -----
        - It is assumed that the database connection and cursor have already been established
        and that the 'Vids' table exists with the appropriate schema.
        - The comments are concatenated into a single string separated by newline characters 
        before being stored in the database.

        Examples
        --------
        >>> video_data = {
        ...     "video_info": {
        ...         "title": "Example Video",
        ...         "statistics": {
        ...             "viewCount": 1000,
        ...             "likeCount": 100,
        ...             "favoriteCount": 10,
        ...             "commentCount": 5
        ...         },
        ...         "duration_seconds": 300,
        ...         "publish_date": "2023-01-01"
        ...     },
        ...     "comments": ["Great video!", "Very informative."]
        ... }
        >>> data_saver.save_video_data(video_data, playlist_id=1)
        """  

                        # Extract necessary data
        
        title = video_stats.get("title", "Unknown Title")

        video_youtube_id = video_stats.get("video_youtube_id", "")
        video_youtube_link = f"https://www.youtube.com/watch?v={video_youtube_id}" if video_youtube_id is not None else ""

        result = self.db_manager.cursor.execute("SELECT MAX(relational_channel_id) FROM Channels").fetchone()
        related_channel_id = result[0] if result and result[0] is not None else None

        def save_video_stats():
            try:
                view_count = video_stats["statistics"].get("viewCount", -1)
                like_count = video_stats["statistics"].get("likeCount", -1)
                favorite_count = video_stats["statistics"].get("favoriteCount", -1)
                comment_count = video_stats["statistics"].get("commentCount", -1)

                video_length = video_stats.get("duration_seconds", "")
                publish_date = video_stats.get("publish_date", "")


                self.last_processed_video_id = video_youtube_id # Here We could start building for a checkpoint system regarding to the api failure 

                # Log extracted information
                self.logger.debug(f"Extracted video data: title='{title}', viewCount={view_count}, "
                            f"likeCount={like_count}, favoriteCount={favorite_count}, "
                            f"commentCount={comment_count}, duration={video_length}, publishDate='{publish_date}'")
            except Exception as e:
                    # Log any exception encountered during database operations
                    self.logger.error(f"An database operations error occurred while saving video data for '{title}': {e}", exc_info=True)
            
            insert_data_query = '''
            INSERT INTO Vids (
                title, viewCount, video_length, likeCount, favoriteCount,
                commentCount, publish_date, video_youtube_id, video_youtube_link, related_channel_id, playlist_youtube_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''.strip()
            
            try: 
                # Execute the query with provided values
                self.logger.info(f"Inserting video '{title}' data into the database.")
                self.db_manager.cursor.execute(insert_data_query, (
                    title, view_count, video_length, like_count, favorite_count,
                    comment_count, publish_date, video_youtube_id, video_youtube_link, related_channel_id, playlist_youtube_id
                ))

                          
                self.db_manager.conn.commit()
                self.logger.info(f"Video '{title}' data successfully saved to the database.")

            except Exception as e:
                # Log any exception encountered during database operations
                self.logger.error(f"An database operations error occurred while saving video data for '{title}': {e}", exc_info=True)

        def save_video_commens():

            # try:

            comments = "\n".join(
                [
                    f"{comment['text']} ,Likes: {comment['likeCount']}, total_replies: {comment['total_replies']}, replies:{len(comment['replies'])}"
                    for comment in video_comments
                ]) 
            
            comment_like = sum(comment['likeCount'] for comment in video_comments)
            
            self.logger.debug(f"Extracted comments for video '{title}': {comments[:100]}...")
            self.logger.debug(f"Total likes for all comments: {comment_like}")


            # except Exception as e:
            #     self.logger.info(f"Comments disabled for video {title}")
            #     comments = None
            #     comment_like = None


            insert_comments_query = '''
            INSERT INTO Video_comments (
            related_channel_id, comments, video_sum_comment_likes, video_youtube_link
            ) VALUES (?, ?, ?, ?)
            '''.strip()


            self.logger.info(f"Inserting video '{title}' comments into the database.")
            self.db_manager.cursor.execute(insert_comments_query, (related_channel_id, comments, comment_like, video_youtube_link
            ))
            self.db_manager.conn.commit()
            self.logger.info(f"Video '{title}' comments successfully saved to the database.")

        save_video_stats()
        save_video_commens()

    


    def save_metadata(self, last_processed_video_id):
            """
            Saves the last processed video ID to the database.

            Parameters
            ----------
            last_processed_video_id : str
                The ID of the last processed video to save in the database.
            """ 
            self.logger.info(f"Saving metadata with last_video_id = {last_processed_video_id}")
            try:
                # Example SQL to insert or update the last processed video ID
                self.db_manager.cursor.execute(
                    "INSERT INTO metadata (last_processed_video_id) VALUES (?)".strip(), 
                    (last_processed_video_id,)
                )
                self.db_manager.conn.commit()
                self.db_manager.logger.info(f"Saved last processed video ID: {last_processed_video_id} to database.")
            except sql.Error as e:
                self.db_manager.logger.error(f"Failed to save metadata due to database error: {e}")
    

    # def get_last_ids(self):
    #         """
    #         Retrieves the last video_youtube_id from the Vids table and the last channel_id from the Channels table.

    #         Returns:
    #             dict: A dictionary containing 'last_video_youtube_id' and 'last_channel_id'.
    #         """
    #         try:
    #             # Fetch the last video_youtube_id from the Vids table
    #             self.db_manager.cursor.execute("SELECT video_youtube_id FROM Vids ORDER BY video_id DESC LIMIT 1")
    #             last_video = self.db_manager.cursor.fetchone()
    #             last_video_youtube_id = last_video[0] if last_video else None

    #             # Fetch the last channel_id from the Channels table
    #             self.db_manager.cursor.execute("SELECT channel_id FROM Channels ORDER BY related_channel_id DESC LIMIT 1")
    #             last_channel = self.db_manager.cursor.fetchone()
    #             last_channel_id = last_channel[0] if last_channel else None

    #             return last_video_youtube_id, last_channel_id
                
    #         except Exception as e:
    #             print(f"Error retrieving last IDs: {e}")
    #             return None

    # def save_checkpoint(self, input):
    #     """
    #     Saves the current state to resume after hitting the quota limit or encountering an error.
    #     """
    #     if input == "channel_id":
    #         return 
    #     else:
    #         channel_video_ids = input
        
    #     last_video_id, last_channel_id = self.get_last_ids()

    #     checkpoint = {
    #         "last_processed_video_id": last_video_id,
    #         "last_processed_channel_id": last_channel_id,
    #         "video_ids": channel_video_ids
    #     }
        
    #     try:
    #         with open('data/checkpoint.json', 'w') as f:
    #             json.dump(checkpoint, f, indent=4)  # Use indent for pretty printing
    #         self.logger.info(f"Checkpoint saved last processed video ID: {self.last_processed_video_id}.")
    #     except IOError as e:
    #         self.logger.error(f"Failed to save checkpoint due to I/O error: {e}")



