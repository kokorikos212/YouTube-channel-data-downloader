import sqlite3 as sql
import os
import logging 

class Database:
    """
    Manages SQLite database creation and structure for storing YouTube channel details.

    This class provides functionality to connect to an SQLite database and initialize tables
    for storing information about YouTube channels, playlists, and videos. The database structure
    supports storing channels with their respective playlists and videos, facilitating organization
    and retrieval of YouTube-related data.

    Attributes
    ----------
    db_filename : str
        The name of the SQLite database file. Defaults to 'youtube_channels.db' if not provided.
    conn : sqlite3.Connection
        The connection object for the SQLite database.
    cursor : sqlite3.Cursor
        The cursor object used to execute SQL queries on the database.
    logger : logging.Logger
        The logger instance to log events and errors.

    Methods
    -------
    create_tables():
        Creates the necessary tables for storing channel, playlist, and video data if they do not exist.
        
    """
    def __init__(self, db_filename="youtube_channels.db"):
        self.db_filename = db_filename 
        self.conn = sql.connect(self.db_filename)
        self.cursor = self.conn.cursor()
        
        # Set up logger
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)  # Configure logging level
        self.logger.info("Database connection established.")

        # Ensure the Channels table exists
        self.create_tables()

    def create_tables(self):
        """Creates or connects to the database and initializes tables."""
        logger = logging.getLogger(__name__)
        
        try:
            conn = sql.connect(self.db_filename)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Channels (
                    relational_channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT UNIQUE NOT NULL,      
                    title TEXT,                          
                    description TEXT,                    
                    published_at TEXT,                    
                    video_count INTEGER DEFAULT 0,        
                    subscribers_count INTEGER DEFAULT 0,  
                    view_count INTEGER DEFAULT 0            
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Playlists (
                    playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_title TEXT,
                    playlist_description TEXT,
                    playlist_length INTEGER,
                    playlist_publish_date TEXT,
                    relational_channel_id INTEGER,
                    playlist_url TEXT,
                    playlist_youtube_id TEXT,
                    FOREIGN KEY (relational_channel_id) REFERENCES Channels (relational_channel_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Vids (
                    video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    viewCount INTEGER,
                    video_length INTEGER,
                    likeCount INTEGER,
                    favoriteCount INTEGER,
                    commentCount INTEGER,
                    publish_date DATE,
                    video_youtube_id TEXT NULL,     
                    playlist_youtube_id TEXT NULL,
                    related_channel_id INTEGER,
                    video_youtube_link TEXT NULL,
                    FOREIGN KEY (related_channel_id) REFERENCES Channels (relational_channel_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS video_comments (
                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    related_channel_id INTEGER,
                    comments TEXT NULL,
                    video_sum_comment_likes INTEGER NULL,
                    video_youtube_link TEXT NULL,

                    FOREIGN KEY (related_channel_id) REFERENCES Vids (relational_channel_id)
                )
            ''')


            conn.commit()
            logger.info(f"Database '{self.db_filename}' and tables have been created successfully.")


        except sql.OperationalError as e:
            logger.error(f"Database operational error: {e}")
        except sql.IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during database setup: {e}")
        finally:
            conn.close()

    def get_last_processed_video_id(self):
        """
        Retrieves the last processed video ID from the metadata table.

        Returns:
        -------
        str or None
            The last processed video ID if it exists, otherwise None.
        """
        self.cursor.execute("SELECT last_processed_video_id FROM Metadata ORDER BY timestamp DESC LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            return result[0]  # Return the first column value (the last_processed_video_id)
        return None
    
# database_inst = Database("db/new.db")