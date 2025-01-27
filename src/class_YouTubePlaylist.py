import requests
from utils import * 
from json_utils import json_print
import time

class YouTubePlaylist:
    def __init__(self, api_key, base_url="https://www.googleapis.com/youtube/v3"):
        """
        Constructor for YouTubePlaylist.

        :param api_key: Your YouTube Data API key.
        """
        self.api_key = api_key
        self.api_call_count = 0
        self.base_url = base_url
        self.base_playlist_url = "https://www.googleapis.com/youtube/v3/playlists"
        self.base_playlist_items_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        self.base_video_url = "https://www.googleapis.com/youtube/v3/videos"
        self.base_comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"

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
            self.api_call_count += 1
            try:
                response = requests.get(url, params=params)  # Pass params here
                response.raise_for_status()
                logger.info("Successfully completed API call for: %s", action_description)
                return response.json(), None  # Success, return data and None status

            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 403 and "quotaExceeded" in response.text:
                    logger.critical("Quota exceeded. Pausing or retrying later.")
                    
                    # self.data_saver.save_metadata(last_video_id)
                    return None, 403 
                else:
                    logger.error("HTTPError: %s for %s", http_err, action_description)
                    return None, response.status_code  # Other HTTP error

            except requests.exceptions.RequestException as e:
                logger.error("RequestException: Network error during %s: %s", action_description, e, exc_info=True)
                return None, 500  # Indicate a generic error

    def get_playlist_details(self, playlist_id):
        """
        Retrieves detailed information about a specified YouTube playlist.

        Args:
            playlist_id (str): The ID of the YouTube playlist to retrieve details for.

        Returns:
            dict or None: A dictionary containing details of the playlist if found, 
                        including information such as title, description, and thumbnail.
                        Returns None if the playlist is not found or an error occurs.
                        
        Raises:
            requests.exceptions.RequestException: If an error occurs during the HTTP request.

        """
        print("__get_playlist_details__")
        url = f"{self.base_playlist_url}?part=snippet&id={playlist_id}&key={self.api_key}"
        self.playlist_url = "https://www.youtube.com/playlist?list={playlist_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses

            data = response.json()

            if 'items' in data and data['items']:
                return data['items'][0]
            else:
                print(f"Error: Playlist with ID {playlist_id} not found.")
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_playlist_items(self, playlist_id):
        """
        Retrieves all video IDs from a specified YouTube playlist.

        Args:
            playlist_id (str): The ID of the YouTube playlist to retrieve video IDs from.

        Returns:
            list: A list of video IDs (str) contained in the playlist. Returns an empty list if no videos are found
                or if an error occurs during data retrieval.

        Raises:
            requests.exceptions.RequestException: If an error occurs during the HTTP request.
        """
        print("__get_playlist_items__")
        url = f"{self.base_playlist_items_url}?part=contentDetails&playlistId={playlist_id}&key={self.api_key}"
        video_ids = []

        try:
            while url:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                video_ids.extend(item['contentDetails']['videoId'] for item in data.get('items', []))

                # Pagination logic
                page_token = data.get('nextPageToken')
                if page_token:
                    url = f"{self.base_playlist_items_url}?part=contentDetails&playlistId={playlist_id}&maxResults=50&pageToken={page_token}&key={self.api_key}"
                else:
                    url = None
            
            return video_ids

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_channel_playlists(self, channel_id):
        """
        Retrieve all playlists for a given YouTube channel, formatted for database insertion.

        Parameters:
        -----------
        channel_id : str
            The unique identifier of the YouTube channel.

        Returns:
        --------
        list
            A list of dictionaries, each containing playlist metadata that matches the Playlists table schema.
            Returns an empty list if no playlists are found or if an error occurs.
        """
        logger = logging.getLogger(__name__)
        playlists = []
        next_page_token = None

        logger.info("Starting to retrieve playlists for channel_id: %s", channel_id)

        while True:
            url = (
                f"{self.base_url}/playlists?part=snippet,contentDetails&channelId={channel_id}"
                f"&maxResults=50&key={self.api_key}"
            )
            if next_page_token:
                url += f"&pageToken={next_page_token}"

            data, status = self.make_api_call(url, logger, "Fetching playlists")

            if status != None:
                return status 
            
            if data is None:
                logger.warning("Failed to retrieve playlists or quota exceeded.")
                break

            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                content_details = item.get("contentDetails", {})

                playlists.append({
                    "playlist_title": snippet.get("title", "Untitled"),
                    "playlist_description": snippet.get("description", "No description"),
                    "playlist_length": content_details.get("itemCount", 0),
                    "playlist_publish_date": snippet.get("publishedAt", None), 
                    "channel_id": channel_id,
                    "playlist_youtube_id": item.get("id"),
                })

            logger.debug("Fetched %d playlists in current batch", len(data.get("items", [])))

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                logger.info("All playlists retrieved for channel_id: %s", channel_id)
                break

        return playlists

    

# if __name__ == "__main__":
#     diem = "UCnMk-6Brd8rVEKWSWkwsWUg"
#     api_key = "AIzaSyBeR-oaAWgXzWp41q-hcRWKBRc3byYNHWk"  
#     yt_inst = YouTubePlaylist(api_key) 
#     res = yt_inst.get_channel_playlists(diem)  
#     print(res[0] ) 


    


