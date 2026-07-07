# custom_pipeline/spreadsheet_manager.py
import os
import json
import logging
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

class SpreadsheetManager:
    def __init__(self):
        self.creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        
        if not self.creds_json:
            raise ValueError("❌ GOOGLE_SHEETS_CREDENTIALS not set")
        if not self.spreadsheet_id:
            raise ValueError("❌ SPREADSHEET_ID not set")
        
        # Connect to Google Sheets
        creds_dict = json.loads(self.creds_json)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        self.client = gspread.authorize(creds)
        logger.info("✅ Connected to Google Sheets")
    
    def get_products(self):
        """Get all products from spreadsheet"""
        sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
        records = sheet.get_all_records()
        return records
    
    def get_pending_products(self):
        """Get products with status != Done"""
        products = self.get_products()
        pending = [p for p in products if p.get('status', 'Pending') != 'Done']
        return pending
    
    def update_status(self, row_index, status):
        """Update status at specific row"""
        sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
        sheet.update_cell(row_index + 2, 9, status)  # Kolom I (status)
        logger.info(f"✅ Updated row {row_index + 2} to {status}")
