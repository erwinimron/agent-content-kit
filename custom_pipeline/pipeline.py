# custom_pipeline/pipeline.py (VERSI DENGAN INFOGRAPHIC)
import os
import sys
import logging
from dotenv import load_dotenv
from custom_pipeline.spreadsheet_manager import SpreadsheetManager
from custom_pipeline.content_generators import StorytellingGenerator, InfographicGenerator
from custom_pipeline.drive_uploader import DriveUploader

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
        self.drive = DriveUploader()  # 🔥 TAMBAHKAN INI!
    
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
                
                # 🔥 TAMBAHKAN INI: Buat folder output terlebih dahulu
                output_dir = f"output/{product_name.replace(' ', '_')}"
                os.makedirs(output_dir, exist_ok=True)
                
                # 🔥 TAMBAHKAN INI: Simpan gambar ke file (dari hasil generator)
                for i, img_data in enumerate(info_result.get('images', [])):
                    file_path = os.path.join(output_dir, f"infographic_{i+1}.png")
                    with open(file_path, 'wb') as f:
                        f.write(img_data)
                    logger.info(f"💾 Saved: {file_path}")
                
                # Upload ke Drive
                folder_id = os.getenv("DRIVE_FOLDER_ID")
                uploaded = self.drive.upload_folder(
                    folder_path=output_dir,
                    parent_folder_id=folder_id
                )
                logger.info(f"📤 Uploaded {len(uploaded)} files to Drive")
            else:
                logger.error(f"❌ Infographic failed: {info_result.get('error')}")    
                
            logger.info(f"✅ Completed: {product_name}")
        
        logger.info("✅ Pipeline completed!")

if __name__ == "__main__":
    pipeline = ContentPipeline()
    pipeline.run()
