# custom_pipeline/pipeline.py
import os
import sys
import logging
from dotenv import load_dotenv
from custom_pipeline.spreadsheet_manager import SpreadsheetManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContentPipeline:
    def __init__(self):
        self.spreadsheet = SpreadsheetManager()
        
    def run(self):
        """Main pipeline execution"""
        logger.info("🚀 Starting Content Pipeline")
        
        # 1. Ambil produk dari spreadsheet
        products = self.spreadsheet.get_pending_products()
        logger.info(f"📊 Found {len(products)} pending products")
        
        for product in products:
            product_name = product.get('product_name', 'Unknown')
            logger.info(f"📝 Processing: {product_name}")
            
            # TODO: Generate 8 konten di sini
            # 1. Infographic
            # 2. Model Photo
            # 3. Walking Video
            # 4. Before After
            # 5. Mix Match
            # 6. Product Detail
            # 7. Outfit Ideas
            # 8. Storytelling
            
            # Update status setelah selesai
            # self.spreadsheet.update_status(product, 'Done')
        
        logger.info("✅ Pipeline completed!")

if __name__ == "__main__":
    pipeline = ContentPipeline()
    pipeline.run()
