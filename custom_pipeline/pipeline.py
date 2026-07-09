# custom_pipeline/pipeline.py
import os
import sys
import logging
from dotenv import load_dotenv
from custom_pipeline.spreadsheet_manager import SpreadsheetManager
from custom_pipeline.content_generators import StorytellingGenerator, InfographicGenerator
from custom_pipeline.telegram_sender import TelegramSender

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
        self.telegram = TelegramSender()
    
    def run(self):
        """Run full pipeline: storytelling + infographic, send to Telegram"""
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
                script = story_result['script']
                caption = story_result.get('caption', '')
                logger.info(f"✅ Storytelling: {script[:100]}...")
                
                # Kirim storytelling ke Telegram
                self.telegram.send_message(
                    f"📝 <b>Storytelling</b>\n\n{script[:500]}...\n\n📌 {caption[:200]}..."
                )
            else:
                logger.error(f"❌ Storytelling failed: {story_result.get('error')}")
            
            # 2. Generate Infographic
            logger.info("🎨 Generating infographic...")
            info_result = self.infographic.generate(product)
            
            if info_result.get('status') == 'success':
                logger.info(f"✅ Infographic: {info_result['total_slides']} slides generated")
                
                # Buat folder output
                output_dir = f"output/{product_name.replace(' ', '_')}"
                os.makedirs(output_dir, exist_ok=True)
                
                # Simpan semua gambar ke file
                image_paths = []
                for i, img_data in enumerate(info_result.get('images', [])):
                    file_path = os.path.join(output_dir, f"infographic_{i+1}.png")
                    with open(file_path, 'wb') as f:
                        f.write(img_data)
                    image_paths.append(file_path)
                    logger.info(f"💾 Saved: {file_path}")
                
                # Kirim infographic ke Telegram (maks 10 foto per album)
                if image_paths:
                    self.telegram.send_album(
                        image_paths,
                        caption=f"🎨 <b>Infographic</b>\nProduct: {product_name}"
                    )
                
                logger.info(f"📤 Sent {len(image_paths)} images to Telegram")
                
            else:
                logger.error(f"❌ Infographic failed: {info_result.get('error')}")
            
            logger.info(f"✅ Completed: {product_name}")
        
        logger.info("✅ Pipeline completed!")

if __name__ == "__main__":
    pipeline = ContentPipeline()
    pipeline.run()
