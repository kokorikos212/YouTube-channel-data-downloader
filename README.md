# YouTube Channel Data Downloader App

## Description:

This app leverages the **YouTube Data API v3** to download detailed information about YouTube channels, playlists, and videos. The data is then stored in a structured **SQL database**, making it easy to analyze and query for insights.

## Key Features:

- **YouTube Channel Data**: Downloads and stores critical channel information, including:
  - Channel ID
  - Title
  - Description
  - Publish date
  - Video count
  - Subscribers count
  - View count

- **Playlist Data**: Retrieves and stores detailed information about the playlists associated with the channel:
  - Playlist title
  - Playlist description
  - Playlist length (number of videos)
  - Playlist publish date
  - Playlist URL

- **Video Data**: Extracts information about individual videos in the channel, including:
  - Video title
  - View count
  - Video length
  - Like count
  - Comment count
  - Favorite count
  - Publish date
  - Video URL

- **Comments Data**: Gathers information about comments on the videos, including:
  - Comment text
  - Comment likes
  - Link to the video

## How It Works:

1. **API Key**: To start using the app, users must first create an API key via the [YouTube Data API v3](https://console.developers.google.com/). The API key is required to authenticate and make requests to the YouTube API.

2. **SQL Database**: The app downloads the data and stores it in an SQL database with the following tables:
   - **Channels**: Holds the channel's metadata.
   - **Playlists**: Holds data related to the playlists of the channel.
   - **Vids**: Stores data about individual videos.
   - **Video Comments**: Collects comments for each video, along with the like count.

## Tables in the Database:

- **Channels**: Information about each channel, including title, description, and engagement metrics.
- **Playlists**: Metadata for the channel’s playlists, including the playlist length and publish date.
- **Vids**: Details about each video in the channel, including likes, views, and comments.
- **Video Comments**: All comments for each video, along with likes on those comments.

## Setup Instructions:

1. **Generate an API Key**: 
   - Visit the [YouTube Data API v3 page](https://console.developers.google.com/).
   - Follow the instructions to create a new project and generate an API key.
   - Save your API key for use in the app.

2. **Run the App**:
   - Enter your API key into the app’s configuration file.
   - Run the script to start downloading the data.

3. **Explore the Data**:
   - Once the data is downloaded, you can query the SQL database to explore various insights about the YouTube channel, playlists, and videos.

## Prerequisites:

- **API Key** from the YouTube Data API v3.
- **Python 3.x** (recommended).
- A running **SQL database** (e.g., SQLite, MySQL, or PostgreSQL).

## Configuration (`StandartInput.json`)

To run the application, you must configure the `StandartInput.json` file located in the `data` folder. This file contains your YouTube API key, the database path, and the YouTube channel IDs to track.

### Example `StandartInput.json`:

json:
{
  "api_key": "YOUR_YOUTUBE_API_KEY",      
  "database_path": "../db/SQL/test.db",
  "yt_channel_ids": ["CHANNEL_ID_1", "CHANNEL_ID_2"]
}

## Additional Features (Future Updates):

- Ability to download data for multiple channels simultaneously.
- More detailed insights into individual video performance, like trends over time.
- Support for downloading comments for specific videos on demand.

---

## Version Notes:

- **v1.0.0**: Initial release – allows users to download and store YouTube channel data, playlists, videos, and comments into a structured SQL database.
