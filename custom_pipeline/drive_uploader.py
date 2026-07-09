# custom_pipeline/drive_uploader.py
import os
import json
import logging
import mimetypes
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

class DriveUploader:
    def __init__(self):
        """Initialize Google Drive uploader with Service Account"""
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if not creds_json:
            raise ValueError("❌ GOOGLE_SHEETS_CREDENTIALS not set")
        
        try:
            creds_dict = json.loads(creds_json)
            self.creds = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("✅ Google Drive uploader initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Drive uploader: {e}")
            raise
    
    def upload_file(self, file_path: str, folder_id: str = None, mime_type: str = None):
        """
        Upload file to Google Drive
        
        Args:
            file_path: Path to file to upload
            folder_id: Optional folder ID to upload to. If None, uploads to root.
            mime_type: Optional MIME type. If None, auto-detects.
        
        Returns:
            tuple: (file_id, file_url)
        """
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return None, None
        
        file_name = os.path.basename(file_path)
        
        # Auto-detect MIME type if not provided
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
        
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        try:
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, name'
            ).execute()
            
            file_id = file.get('id')
            file_url = f"https://drive.google.com/file/d/{file_id}/view"
            
            logger.info(f"✅ Uploaded: {file_name} (ID: {file_id})")
            return file_id, file_url
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return None, None
    
    def upload_folder(self, folder_path: str, parent_folder_id: str = None):
        """
        Upload all files in a folder to Google Drive
        
        Args:
            folder_path: Local folder path
            parent_folder_id: Optional parent folder ID in Drive
        
        Returns:
            list: List of uploaded file info
        """
        uploaded = []
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_id, file_url = self.upload_file(file_path, parent_folder_id)
                if file_id:
                    uploaded.append({
                        'name': file_name,
                        'id': file_id,
                        'url': file_url
                    })
        return uploaded
