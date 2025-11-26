#This file must be run from a machine with a browser to authenticate
#After the initial authentication, the bot should be able to refresh the token by itself
#The credentials.json file should be in the same folder as this script
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

def main():
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print("Please visit this URL and authorize the app:")
    print(auth_url)
    print()
    print("Then enter the authorization code:")
    code = input().strip()
    
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"✅ Authentication successful!")
    print(f"   Has refresh token: {bool(creds.refresh_token)}")
    print(f"   Token expiry: {creds.expiry}")

if __name__ == '__main__':
    main()