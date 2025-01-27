import requests 
import isodate 
import sys ,json  
import logging 
from class_create_Database import Database 
from class_Save_data import DataSaver 

class YouTubeAPIClient:
    def __init__(self, api_key, base_url="https://www.googleapis.com/youtube/v3", db_manager=None):
        """
        Initializes the YouTubeAPIClient with necessary configurations and retrieves the last processed video ID.
        
        Parameters:
        ----------
        api_key : str
            The API key for authenticating with the YouTube API.
        base_url : str, optional
            The base URL for the YouTube API (default is the v3 API).
        db_filename : str, optional
            The name of the SQLite database file (default is 'youtube_channels.db').
        """
        # self.data_saver = DataSaver(db_manager)

        self.api_key = api_key
        self.base_url = base_url
        # self.api_call_count = 0
        # self.api_quota_limit = 10000  
        self.logger = logging.getLogger(__name__)


    def make_api_call(self, url, logger, action_description, params=None):
        """
        Makes an API call to a given URL, logging and handling errors consistently.

        Parameters:
        ----------
        url : str
            The API endpoint URL for the request.
        logger : logging.Logger
            The logger instance to use for logging events.
        action_description : str
            A short description of the API action for logging purposes.
        params : dict, optional
            A dictionary of query parameters to include in the API request.

        Returns:
        -------
        dict or None
            Parsed JSON data from the response if successful, None if an error occurs.
        """
        try:
            response = requests.get(url, params=params)  # Pass params here
            response.raise_for_status()
            self.logger.info("Successfully completed API call for: %s", action_description)
            return response.json(), None  # Success, return data and None status

        except requests.exceptions.HTTPError as http_err:
            # Handle specific 403 error for missing comments
            if response.status_code == 403:
                if "quotaExceeded" in response.text:
                    self.logger.info("Missing comments.")
                    return None, 403
                else:
                    logger.info("HTTP 403 Forbidden: %s for %s. Likely due to missing comments.", http_err, action_description)
                    return None, 403  # Log as INFO and return status

            # Log other HTTP errors
            logger.error("HTTPError: %s for %s", http_err, action_description)
            return None, response.status_code

        except requests.exceptions.RequestException as e:
            logger.error("RequestException: Network error during %s: %s", action_description, e, exc_info=True)
            return None, 500  # Indicate a generic error

    def get_channel_info(self, channel_id):
        """
        Retrieves information about a YouTube channel, including basic details and optional statistics.

        Parameters:
        ----------
        channel_id : str
            The unique identifier for the YouTube channel to retrieve information for.

        Returns:
        -------
        dict or None
            A dictionary containing channel information. Returns `None` if an error occurs.

        Notes:
        ------
        - This function first tries to retrieve channel statistics (e.g., subscriber count, view count).
        If the statistics are not present, it falls back to the content details for required fields.
        - Any missing fields in 'statistics' are replaced by "N/A" in the returned dictionary.
        - `self.api_key` is required as an API key to authenticate requests to the YouTube API.

        Raises:
        ------
        KeyError
            If any critical fields such as 'title' or 'published_at' are missing in the API response.
        """
        logger = logging.getLogger(__name__)
        url = f"{self.base_url}/channels?part=snippet,contentDetails,statistics&id={channel_id}&key={self.api_key}"

        logger.info("Fetching channel information for channel_id: %s", channel_id)

        # Centralized API call using the helper function to track and handle errors consistently.
        data, status = self.make_api_call(url, logger, "Fetching channel information")
        
        if data is None:
            logger.warning("API call failed or quota exceeded. Returning None.")
            return None

        # Process the response if valid data is returned
        if 'items' in data and data['items']:
            channel_info = data['items'][0]
            try:
                title = channel_info['snippet']['title']
                description = channel_info['snippet']['description']
                published_at = channel_info['snippet']['publishedAt']
                statistics = channel_info.get('statistics', {})

                logger.info("Successfully retrieved channel information for %s", title)
                return {
                    'channelId': channel_id,
                    'title': title,
                    'description': description,
                    'published_at': published_at,
                    'video_count': statistics.get('videoCount', -1),
                    'subscribers_count': statistics.get('subscriberCount', -1),
                    'view_count': statistics.get('viewCount', -1),
                }

            except KeyError as e:
                logger.error("KeyError: Missing expected field in channel_info: %s", e, exc_info=True)
                return None
            except Exception as e:
                logger.error("Unexpected error while processing channel information: %s", e, exc_info=True)
                return None
        else:
            logger.warning("Channel not found or invalid ID for channel_id: %s", channel_id)
            return None


    def get_playlist_video_count(self, playlist_id):
        """
        Fetch the number of videos in a playlist using the YouTube API.

        Parameters:
        -----------
        playlist_id : str
            The unique identifier of the playlist.

        Returns:
        --------
        int
            The number of videos in the playlist. Returns 0 if an error occurs.
        """
        logger = logging.getLogger(__name__)
        url = f"{self.base_url}/playlists?part=contentDetails&id={playlist_id}&key={self.api_key}"

        # Using make_api_call to handle API request and error handling
        data = self.make_api_call(url, logger, "Fetching playlist video count")

        if data is None or 'items' not in data or not data['items']:
            logger.warning("Failed to retrieve video count for playlist_id: %s", playlist_id)
            return 0

        video_count = data['items'][0]['contentDetails']['itemCount']
        logger.info("Video count for playlist %s: %d", playlist_id, video_count)
        return video_count

   
    def get_video_ids_from_playlist(self, playlist_id):
        """
        Retrieves all video IDs contained within a specified YouTube playlist.

        Parameters
        ----------
        playlist_id : str
            The ID of the playlist from which to retrieve video IDs.

        Returns
        -------
        list
            A list of video IDs in the specified playlist.

        Raises
        ------
        YouTubeAPIException
            If there is an error with the API request or response.
        """
        logger = logging.getLogger(__name__)
        base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        video_ids = []
        next_page_token = None

        try:
            while True:
                # Prepare the request URL with necessary parameters
                url = f"{base_url}?part=snippet&playlistId={playlist_id}&maxResults=50&key={self.api_key}"
                if next_page_token:
                    url += f"&pageToken={next_page_token}"
                
                logger.debug(f"Requesting URL: {url}")
                
                # Make the request
                response = requests.get(url)
                response.raise_for_status()  # Raise an error for bad HTTP status

                # Parse the JSON response
                data = response.json()
                logger.debug(f"Response received: {data}")

                # Extract video IDs
                if 'items' in data:
                    for item in data['items']:
                        video_id = item['snippet']['resourceId'].get('videoId')
                        if video_id:
                            video_ids.append(video_id)

                # Check if there is another page
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while fetching playlist '{playlist_id}': {e}")
            raise RuntimeError(f"Failed to retrieve video IDs from playlist '{playlist_id}'") from e
        except KeyError as e:
            logger.error(f"Key error in API response while processing playlist '{playlist_id}': {e}")
            raise RuntimeError(f"Unexpected response structure for playlist '{playlist_id}'") from e

        logger.info(f"Retrieved {len(video_ids)} video IDs from playlist '{playlist_id}'")
        return video_ids


    def get_all_video_ids_from_channel(self, channel_id):
        """
        Retrieves all video IDs directly from a given YouTube channel without relying on playlists.

        Parameters:
        ----------
        channel_id : str
            The unique identifier for the YouTube channel from which to extract video IDs.

        Returns:
        -------
        list of str
            A list containing all video IDs uploaded to the specified channel.
        """
        video_ids = []
        next_page_token = None
        self.logger.info(f"Starting to retrieve video IDs for channel ID: {channel_id}")

        while True:
            url = f"{self.base_url}/search"
            params = {
                'part': 'id',
                'channelId': channel_id,
                'maxResults': 50,
                'type': 'video',
                'key': self.api_key
            }
            if next_page_token:
                params['pageToken'] = next_page_token

            data, status = self.make_api_call(url, self.logger, "Retrieve video IDs", params=params)

            if data is None and status == 403:
                return None, 403

            # Extract video IDs from the response
            if 'items' in data:
                for item in data['items']:
                    if item['id']['kind'] == 'youtube#video':
                        video_ids.append(item['id']['videoId'])
                        self.logger.debug(f"Extracted video ID: {item['id']['videoId']}")

            # Check for pagination
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break  # No more pages

        return video_ids, status 


    def extract_channel_data(self, channel_id):
        """
        Extracts and formats data for a given YouTube channel, including channel details, playlists, 
        and uploaded videos.

        Parameters:
        ----------
        channel_id : str
            The unique identifier for the YouTube channel.

        Returns:
        -------
        dict
            A dictionary containing structured data for the channel, with the following keys:
            - 'channel_info': dict
                Basic information about the channel, retrieved by `get_channel_info`.
            - 'playlist': list
                A list of playlists associated with the channel, retrieved by `get_channel_playlists`.
            - 'video_ids': list
                A list of uploaded video IDs from the channel's primary upload playlist.
        """
        channel_info = self.get_channel_info(channel_id)
        if channel_info is None:
            return None  # Return None if channel info cannot be fetched

        playlists = self.get_channel_playlists(channel_id)
        video_ids = self.get_all_video_ids_from_channel(channel_id)

        resulting_dict = {
            'channel_info': channel_info,
            'playlist': playlists,
            'video_ids': video_ids
        }
        
        return resulting_dict


    def get_video_stats(self, video_id):
        """
        Fetches statistical information, duration, and publish date for a given video ID.

        Args:
            video_id (str): The ID of the video.

        Returns:
            dict: A dictionary containing video statistics, duration, and publish date.
        """
        # Get video statistics, duration, and publish date
        stats_url = f"{self.base_url}/videos"
        stats_params = {
            'part': 'statistics,snippet,contentDetails',
            'id': video_id,
            'key': self.api_key
        }
        
        stats_data, status = self.make_api_call(stats_url, self.logger, "Fetch video stats", params=stats_params)
        if status == 403:
            return 403
        else:
            try:
                if stats_data is None or not stats_data.get('items'):
                    return {"error": "Video not found or not accessible."}
            except:
                return "Quota exceded"

            video_item = stats_data["items"][0]

            # Extract and convert video duration
            duration_iso = video_item["contentDetails"]["duration"]
            duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())

            video_stats = {
                "video_youtube_id": video_id,
                "title": video_item["snippet"]["title"],
                "description": video_item["snippet"]["description"],
                "publish_date": video_item["snippet"]["publishedAt"],
                "duration_seconds": duration_seconds,
                "video_youtube_id": video_id,
                "statistics": video_item["statistics"]
            }
            
            return video_stats

    def get_all_video_comments(self, video_id):
        """
        Fetches all top-level comments for a video, along with their replies.

        Parameters:
        ----------
        video_id : str
            The ID of the video to fetch comments for.

        Returns:
        -------
        list
            A list of comments, each represented as a dictionary, including replies.
        """
        self.logger.info(f"Fetching comments for video ID: {video_id}")
        comments = []
        page_token = None

        while True:
            url = f"{self.base_url}/commentThreads"
            params = {
                "part": "snippet",
                "videoId": video_id,
                "pageToken": page_token,
                "maxResults": 100,
                "key": self.api_key,  # Include the API key here
            }
            action_description = f"Fetching top-level comments for video ID: {video_id}"

            response, status_code = self.make_api_call(url, self.logger, action_description, params)
            if response is None:
                break

            for item in response.get("items", []):
                comment_data = item["snippet"]["topLevelComment"]["snippet"]
                comment_id = item["snippet"]["topLevelComment"]["id"]

                # Fetch replies using the instance method
                replies = self.get_comment_replies(comment_id)

                # Add comment and its replies
                comment = {
                    "text": comment_data["textDisplay"],
                    "likeCount": comment_data.get("likeCount", 0),
                    "total_replies": len(replies),
                    "replies": replies,
                }
                comments.append(comment)

            # Break if there is no next page
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return comments

    def get_comment_replies(self, comment_id):
            """
            Fetches replies for a specific comment.

            Parameters:
            ----------
            comment_id : str
                The ID of the comment to fetch replies for.

            Returns:
            -------
            list
                A list of replies, each represented as a dictionary.
            """
            self.logger.debug(f"Fetching replies for comment ID: {comment_id}")
            url = f"{self.base_url}/comments"
            params = {
                "part": "snippet",
                "parentId": comment_id,
                "maxResults": 100,
                "key": self.api_key,  # Include the API key here
            }
            action_description = f"Fetching replies for comment ID: {comment_id}"

            response, status_code = self.make_api_call(url, self.logger, action_description, params)
            if response is None:
                return []

            replies = [
                {
                    "text": reply["snippet"]["textDisplay"],
                }
                for reply in response.get("items", [])
            ]
            return replies



# from json_utils import save_dict_to_json
# from json_utils import json_print
# # from data_utils import *  
# api_key = "AIzaSyBeR-oaAWgXzWp41q-hcRWKBRc3byYNHWk"
# mistId = "UCC5GG5tZf0APYlBbzup9J9A"
# diem = "UCnMk-6Brd8rVEKWSWkwsWUg"
# yt_inst = YouTubeAPIClient(api_key) 
# res = yt_inst.get_all_video_comments("a-2x58i1P8c")   
# json_print(res) 

# # # # res = yt_inst.get_video_stats_and_comments("Y0FHU9qGeI0")
# json_print(res) 

# res = yt_inst.extract_channel_data(mistId) 
# json_print(res) 
        