import os
import pickle
import asyncio
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self, config):
        self.config = config
        self.credentials = None
        self.youtube_oauth = None
        self.youtube_api = None
        self.api_key = config.get('apis.youtube.api_key')
    
    def _load_and_refresh_credentials(self):
        """Load credentials from token.pickle and refresh if needed"""
        if not os.path.exists('token.pickle'):
            logger.warning("token.pickle not found - OAuth not available")
            return None

        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                logger.info(f"Loaded credentials from token.pickle (valid: {creds.valid}, expired: {creds.expired})")

            # Refresh if expired
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    logger.info("Token expired, refreshing...")
                    creds.refresh(Request())
                    logger.info("✅ Token refreshed successfully")

                    # Save refreshed credentials
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
                    logger.info("Saved refreshed token to token.pickle")
                else:
                    logger.error("Token invalid and cannot be refreshed")
                    return None

            return creds

        except Exception as e:
            logger.error(f"Error loading/refreshing credentials: {e}")
            return None
    
    def is_authenticated(self):
        """Check if YouTube OAuth is authenticated, load and refresh if needed"""
        # Try to load credentials if we don't have them yet
        if not self.credentials:
            logger.info("No credentials loaded yet, attempting to load from token.pickle...")
            self.credentials = self._load_and_refresh_credentials()

            if self.credentials:
                # Build YouTube service with loaded credentials
                self.youtube_oauth = build(
                    self.config.get('youtube.service_name'),
                    self.config.get('youtube.version'),
                    credentials=self.credentials
                )
                logger.info("✅ YouTube OAuth service initialized")

        # If we have credentials, check if they're still valid
        if self.credentials:
            if not self.credentials.valid:
                logger.info("Credentials invalid, attempting refresh...")
                self.credentials = self._load_and_refresh_credentials()

                if self.credentials:
                    # Rebuild service with refreshed credentials
                    self.youtube_oauth = build(
                        self.config.get('youtube.service_name'),
                        self.config.get('youtube.version'),
                        credentials=self.credentials
                    )
                    logger.info("✅ YouTube OAuth service rebuilt with refreshed token")
                    return True
                else:
                    logger.error("❌ Failed to refresh credentials")
                    return False

            logger.info("YouTube authentication: ✅ Valid")
            return True

        logger.warning("YouTube authentication: ❌ Not authenticated")
        return False
    
    def initialize_api_key(self):
        """Initialize YouTube API with API key for read operations"""
        if self.api_key and not self.youtube_api:
            self.youtube_api = build(
                self.config.get('youtube.service_name'),
                self.config.get('youtube.version'),
                developerKey=self.api_key
            )
            logger.info("YouTube API key authentication initialized")
        return self.youtube_api
    
    def add_video_to_playlist(self, video_id, playlist_id=None):
        """Add a video to the specified playlist (requires OAuth)"""
        if not playlist_id:
            playlist_id = self.config.playlist_id
        
        # Check and refresh authentication if needed
        if not self.is_authenticated():
            raise Exception("YouTube OAuth not authenticated")
        
        try:
            logger.info(f"Adding video {video_id} to playlist {playlist_id}...")
            request = self.youtube_oauth.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )

            response = request.execute()
            logger.info(f"✅ Video {video_id} added to playlist")
            return response

        except Exception as e:
            logger.error(f"❌ Failed to add video {video_id}: {e}")
            raise
    
    def get_video_title(self, video_id):
        """Get video title from video ID (uses API key)"""
        # Try API key first
        if not self.youtube_api:
            self.initialize_api_key()
            
        if self.youtube_api:
            try:
                request = self.youtube_api.videos().list(
                    part="snippet",
                    id=video_id
                )
                response = request.execute()
                
                if response['items']:
                    return response['items'][0]['snippet']['title']

            except Exception as e:
                logger.warning(f"Failed to get video title via API for {video_id}: {e}")
        
        # Fallback to web scraping
        return self._get_video_title_fallback(video_id)
    
    def _get_video_title_fallback(self, video_id):
        """Fallback method to get video title via web scraping"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, features="lxml")
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.split(" - YouTube")[0]
                return title
        except Exception as e:
            logger.error(f"Error getting video title via fallback: {e}")

        return "Unknown Title"