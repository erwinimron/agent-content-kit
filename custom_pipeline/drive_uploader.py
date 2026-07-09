# custom_pipeline/drive_uploader.py
import os
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

class DriveUploader:
    def __init__(self):
        # Pake credentials yang sama dari GOOGLE_SHEETS_CREDENTIALS
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        self.creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def upload_file(self, file_path: str, folder_id: str = None, mime_type: str = None):
        """Upload file ke Google Drive, return file ID & link"""
        file_name = os.path.basename(file_path)
        file_metadata = {'name': file_name}
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        link = file.get('webViewLink')
        logger.info(f"✅ Uploaded: {file_name} (ID: {file_id})")
        return file_id, link
