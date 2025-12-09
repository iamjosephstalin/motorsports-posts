import os
import json
import logging
from instagrapi import Client
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Publisher")

class Publisher:
    def __init__(self):
        self.ig_client = Client()
        self.ig_session_file = "settings.json"
        
        # YouTube Setup
        self.youtube_scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.youtube_service = None

    def login_instagram(self, username, password):
        """
        Logins to Instagram with session management.
        """
        if os.path.exists(self.ig_session_file):
            logger.info("Loading Instagram session from settings.json")
            self.ig_client.load_settings(self.ig_session_file)
            
        try:
            # Check if session is valid by making a light request? 
            # Or just try login. login() in instagrapi handles re-login if session invalid usually.
            self.ig_client.login(username, password)
            self.ig_client.dump_settings(self.ig_session_file)
            logger.info("Instagram login successful.")
            return True
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            return False

    def upload_instagram_photo(self, image_path, caption):
        """
        Uploads a photo to Instagram.
        """
        logger.info(f"Uploading photo to Instagram: {image_path}")
        try:
            self.ig_client.photo_upload(image_path, caption=caption)
            logger.info("Photo uploaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to upload photo to Instagram: {e}")
            return False

    def upload_instagram_reel(self, video_path, caption):
        """
        Uploads a reel to Instagram.
        """
        logger.info(f"Uploading reel to Instagram: {video_path}")
        try:
            self.ig_client.clip_upload(video_path, caption=caption)
            logger.info("Reel uploaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to upload reel to Instagram: {e}")
            return False

    def authenticate_youtube(self):
        """
        Authenticates with YouTube API.
        """
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.youtube_scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists("client_secret.json"):
                     flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", self.youtube_scopes)
                     creds = flow.run_local_server(port=0)
                else:
                    logger.error("client_secret.json not found for YouTube.")
                    return False
            
            with open("token.json", "w") as token:
                token.write(creds.to_json())
                
        self.youtube_service = build("youtube", "v3", credentials=creds)
        logger.info("YouTube authentication successful.")
        return True

    def upload_youtube_short(self, video_path, title, description=""):
        """
        Uploads a Short to YouTube.
        """
        if not self.youtube_service:
            if not self.authenticate_youtube():
                return False

        logger.info(f"Uploading Short to YouTube: {video_path}")
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["F1", "MotoGP", "RacingTamizhan", "Shorts"],
                    "categoryId": "17" # Sports
                },
                "status": {
                    "privacyStatus": "private", # Default to private for safety
                    "selfDeclaredMadeForKids": False,
                }
            }
            
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = self.youtube_service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Uploaded {int(status.progress() * 100)}%")
            
            logger.info("YouTube upload complete.")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to YouTube: {e}")
            return False
