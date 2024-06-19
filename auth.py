from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

BEG_GREEN = '\33[32m'
END_GREEN = '\33[0m'

# Define your API key and the necessary parameters
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
#PLAYLIST_ID = 'PLSLlIlXQSsqmKbKSstCSoS4RLoSo2awoX'
PLAYLIST_ID = 'PLl58uFKfuzLU-HfruEVohMJOC4Ag1DThy'

def add_video_to_playlist(credentials, video_id):
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Add video to playlist
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": PLAYLIST_ID,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )

    response = request.execute()
    print(BEG_GREEN + f'Video {video_id} added to playlist {PLAYLIST_ID}' + END_GREEN)

def get_authenticated_service():
	print("start auth")
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
	print("finished auth")

	return creds
