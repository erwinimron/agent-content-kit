# custom_pipeline/pipeline.py (VERSI TEST)
import os
import sys
import logging
from dotenv import load_dotenv
from custom_pipeline.spreadsheet_manager import SpreadsheetManager
from custom_pipeline.content_generators import StorytellingGenerator

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContentPipeline:
    def __init__(self):
        self.spreadsheet = SpreadsheetManager()
        self.storytelling = StorytellingGenerator()
    
    def run(self):
        """Test pipeline: cuma jalankan storytelling untuk 1 produk"""
        logger.info("🚀 Starting TEST Pipeline (Storytelling only)")
        
        products = self.spreadsheet.get_pending_products()
        logger.info(f"📊 Found {len(products)} pending products")
        
        if not products:
            logger.warning("⚠️ No pending products found. Make sure status is not 'Done'")
            return
        
        # Ambil produk pertama untuk test
        product = products[0]
        product_name = product.get('product_name', 'Unknown')
        logger.info(f"📝 Testing with product: {product_name}")
        
        # Generate storytelling
        result = self.storytelling.generate(product)
        
        if result.get('status') == 'success':
            logger.info(f"✅ Storytelling generated successfully!")
            logger.info(f"📝 Script preview: {result['script'][:200]}...")
            logger.info(f"📝 Caption preview: {result['caption'][:200]}...")
            
            # Update status di spreadsheet (opsional)
            # self.spreadsheet.update_status(0, 'Storytelling Done')
        else:
            logger.error(f"❌ Failed: {result.get('error')}")
        
        logger.info("✅ Test pipeline completed!")

if __name__ == "__main__":
    pipeline = ContentPipeline()
    pipeline.run()
