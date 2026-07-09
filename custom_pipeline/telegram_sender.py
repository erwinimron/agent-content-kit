# custom_pipeline/telegram_sender.py
import os
import logging
import requests

logger = logging.getLogger(__name__)

class TelegramSender:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.token or not self.chat_id:
            logger.warning("⚠️ Telegram credentials not set. Messages will not be sent.")
            self.enabled = False
        else:
            self.enabled = True
            self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, text: str):
        """Send text message to Telegram"""
        if not self.enabled:
            return
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Message sent to Telegram")
            else:
                logger.error(f"❌ Failed to send message: {response.text}")
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
    
    def send_photo(self, photo_path: str, caption: str = ""):
        """Send photo to Telegram"""
        if not self.enabled:
            return
        
        url = f"{self.base_url}/sendPhoto"
        try:
            with open(photo_path, 'rb') as f:
                files = {'photo': f}
                data = {'chat_id': self.chat_id, 'caption': caption}
                response = requests.post(url, files=files, data=data, timeout=30)
                if response.status_code == 200:
                    logger.info(f"✅ Photo sent: {photo_path}")
                else:
                    logger.error(f"❌ Failed to send photo: {response.text}")
        except Exception as e:
            logger.error(f"❌ Error sending photo: {e}")
    
    def send_album(self, photo_paths: list, caption: str = ""):
        """Send multiple photos as album (max 10)"""
        if not self.enabled:
            return
        
        # Telegram only allows 10 photos per album
        for i in range(0, len(photo_paths), 10):
            batch = photo_paths[i:i+10]
            self._send_album_batch(batch, caption if i == 0 else "")
    
    def _send_album_batch(self, photo_paths: list, caption: str = ""):
        """Send a batch of photos as album (max 10)"""
        url = f"{self.base_url}/sendMediaGroup"
        media = []
        for path in photo_paths:
            media.append({
                "type": "photo",
                "media": f"attach://{os.path.basename(path)}",
            })
        # ... (kode untuk upload multiple files)
