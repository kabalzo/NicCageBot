import os
import pickle
import asyncio
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
from bs4 import BeautifulSoup

class YouTubeService:
    def __init__(self, config):
        self.config = config
        self.credentials = None
        self.youtube_oauth = None
        self.youtube_api = None
        self.api_key = config.get('apis.youtube.api_key')
        
    async def authenticate_oauth_headless(self):
        """Authenticate with YouTube API using headless OAuth for servers"""
        print("Starting headless YouTube OAuth authentication...")
        creds = None
        
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                try:
                    creds = pickle.load(token)
                    print("Loaded existing credentials from token.pickle")
                    print(f"Token valid: {creds.valid}")
                    print(f"Token expired: {creds.expired}")
                    print(f"Has refresh token: {bool(creds.refresh_token)}")
                except EOFError:
                    print("Token file exists but is empty/corrupted")
                    creds = None
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired credentials...")
                try:
                    creds.refresh(Request())
                    print("✅ Successfully refreshed token")
                except Exception as refresh_error:
                    print(f"❌ Failed to refresh token: {refresh_error}")
                    print("Getting new credentials...")
                    creds = await self._get_new_credentials()
            else:
                print("No valid credentials found. Getting new credentials...")
                creds = await self._get_new_credentials()
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            print("Credentials saved to token.pickle")
        
        self.credentials = creds
        self.youtube_oauth = build(
            self.config.get('youtube.service_name'),
            self.config.get('youtube.version'),
            credentials=creds
        )
        
        print("YouTube OAuth authentication completed successfully")
        return creds
    
    async def _get_new_credentials(self):
        """Get new OAuth credentials with offline access"""
        if not os.path.exists('credentials.json'):
            raise Exception("credentials.json not found")
            
        print("Getting new OAuth credentials...")
        
        # Use offline access to get a refresh token
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', 
            self.config.get('youtube.scopes'),
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # For out-of-band flow
        )
        
        # For headless servers, we need manual authentication
        return await self._create_manual_auth_instructions()
    
    async def _create_manual_auth_instructions(self):
        """Provide instructions for manual authentication with offline access"""
        print("\n" + "="*60)
        print("MANUAL YOUTUBE AUTHENTICATION REQUIRED")
        print("="*60)
        print("Since this is a headless server, you need to:")
        print("1. On your local machine with a browser, run this command:")
        print()
        print("python3 -c \"")
        print("from google_auth_oauthlib.flow import InstalledAppFlow")
        print("flow = InstalledAppFlow.from_client_secrets_file(")
        print("    'credentials.json',")
        print("    scopes=['https://www.googleapis.com/auth/youtube.force-ssl'],")
        print("    redirect_uri='urn:ietf:wg:oauth:2.0:oob'")
        print(")")
        print("auth_url, _ = flow.authorization_url(prompt='consent')")
        print("print('Please visit this URL and authorize the app:')")
        print("print(auth_url)")
        print("print()")
        print("print('Then enter the authorization code:')")
        print("code = input().strip()")
        print("flow.fetch_token(code=code)")
        print("creds = flow.credentials")
        print("import pickle")
        print("with open('token.pickle', 'wb') as token:")
        print("    pickle.dump(creds, token)")
        print("print('✅ Authentication successful! token.pickle created.')")
        print("\"")
        print()
        print("2. Copy the generated 'token.pickle' file to this server")
        print("3. Restart the bot")
        print("="*60)
        
        # Wait for manual intervention
        print("Waiting for manual authentication...")
        while not os.path.exists('token.pickle'):
            await asyncio.sleep(10)
            print("Still waiting for token.pickle...")
        
        # Load the manually provided token
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            print(f"✅ Loaded new credentials with refresh token: {bool(creds.refresh_token)}")
            return creds
    
    def is_authenticated(self):
        """Check if YouTube OAuth is authenticated"""
        authenticated = self.youtube_oauth is not None and self.credentials is not None
        print(f"YouTube authentication status: {authenticated}")
        return authenticated
    
    def initialize_api_key(self):
        """Initialize YouTube API with API key for read operations"""
        if self.api_key and not self.youtube_api:
            self.youtube_api = build(
                self.config.get('youtube.service_name'),
                self.config.get('youtube.version'),
                developerKey=self.api_key
            )
            print("YouTube API key authentication initialized")
        return self.youtube_api
    
    def add_video_to_playlist(self, video_id, playlist_id=None):
        """Add a video to the specified playlist (requires OAuth)"""
        if not playlist_id:
            playlist_id = self.config.playlist_id
            
        if not self.is_authenticated():
            raise Exception("YouTube OAuth not authenticated")
        
        try:
            print(f"Making YouTube API call to add {video_id} to playlist {playlist_id}")
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
            print(f"✅ Video {video_id} successfully added to playlist {playlist_id}")
            return response
            
        except Exception as e:
            print(f"❌ Failed to add video {video_id} to playlist {playlist_id}: {e}")
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
                print(f"Failed to get video title via API for {video_id}: {e}")
        
        # Fallback to web scraping if API key fails or isn't available
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
            print(f"Error getting video title via fallback: {e}")
            
        return "Unknown Title"