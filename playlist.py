from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

# Define your API key and the necessary parameters
API_KEY = 'YOUR_API_KEY'  # Replace with your actual API key
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
PLAYLIST_ID = 'PLl58uFKfuzLU-HfruEVohMJOC4Ag1DThy'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def add_video_to_playlist(credentials, video_id, playlist_id):
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Add video to playlist
    request = youtube.playlistItems().insert(
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
    print(f'Video {video_id} added to playlist {playlist_id}.')

def get_authenticated_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            try:
                creds = pickle.load(token)
            except EOFError:
                pass
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def main():
    # Authenticate and create the YouTube service
    credentials = get_authenticated_service()

    # Example video ID and playlist ID (replace with your own)
    video_id = 'PWirijQkH4M'
    #playlist_id = 'PLl58uFKfuzLU-HfruEVohMJOC4Ag1DThy'

    # Add video to the playlist
    add_video_to_playlist(credentials, video_id, PLAYLIST_ID)

if __name__ == '__main__':
    main()

