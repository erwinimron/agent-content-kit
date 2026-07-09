# custom_pipeline/pipeline.py (VERSI DENGAN INFOGRAPHIC)
import os
import sys
import logging
from dotenv import load_dotenv
from custom_pipeline.spreadsheet_manager import SpreadsheetManager
from custom_pipeline.content_generators import StorytellingGenerator, InfographicGenerator

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
        self.infographic = InfographicGenerator()
    
    def run(self):
        """Run full pipeline: storytelling + infographic"""
        logger.info("🚀 Starting FULL Pipeline (Storytelling + Infographic)")
        
        products = self.spreadsheet.get_pending_products()
        logger.info(f"📊 Found {len(products)} pending products")
        
        if not products:
            logger.warning("⚠️ No pending products found")
            return
        
        for product in products:
            product_name = product.get('product_name', 'Unknown')
            logger.info(f"📝 Processing: {product_name}")
            
            # 1. Generate Storytelling
            logger.info("📝 Generating storytelling...")
            story_result = self.storytelling.generate(product)
            
            if story_result.get('status') == 'success':
                logger.info(f"✅ Storytelling: {story_result['script'][:100]}...")
            else:
                logger.error(f"❌ Storytelling failed: {story_result.get('error')}")
            
            # 2. Generate Infographic
            logger.info("🎨 Generating infographic...")
            info_result = self.infographic.generate(product)
            
            if info_result.get('status') == 'success':
                logger.info(f"✅ Infographic: {info_result['total_slides']} slides generated")
            else:
                logger.error(f"❌ Infographic failed: {info_result.get('error')}")
            
            logger.info(f"✅ Completed: {product_name}")
        
        logger.info("✅ Pipeline completed!")

if __name__ == "__main__":
    pipeline = ContentPipeline()
    pipeline.run()
