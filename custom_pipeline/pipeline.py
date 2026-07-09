# custom_pipeline/pipeline.py
import os
import sys
import logging
import traceback
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
        
        # Kirim notifikasi mulai
        self.telegram.send_message("🚀 <b>Pipeline Started!</b>\n\nMemproses produk pending...")
        
        try:
            products = self.spreadsheet.get_pending_products()
            logger.info(f"📊 Found {len(products)} pending products")
            
            if not products:
                logger.warning("⚠️ No pending products found")
                self.telegram.send_message("⚠️ <b>Tidak ada produk pending</b>\n\nSemua produk sudah diproses.")
                return
            
            success_count = 0
            fail_count = 0
            
            for idx, product in enumerate(products):
                product_name = product.get('product_name', 'Unknown')
                logger.info(f"📝 Processing: {product_name} ({idx+1}/{len(products)})")
                
                # Kirim notifikasi per produk
                self.telegram.send_message(f"📦 <b>Processing</b>: {product_name} ({idx+1}/{len(products)})")
                
                # 1. Generate Storytelling
                logger.info("📝 Generating storytelling...")
                try:
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
                        error_msg = f"❌ Storytelling failed: {story_result.get('error')}"
                        logger.error(error_msg)
                        self.telegram.send_message(error_msg)
                        fail_count += 1
                        continue  # Skip ke produk berikutnya
                        
                except Exception as e:
                    error_msg = f"❌ Storytelling error: {str(e)}\n{traceback.format_exc()[:200]}"
                    logger.error(error_msg)
                    self.telegram.send_message(error_msg)
                    fail_count += 1
                    continue
                
                # 2. Generate Infographic
                logger.info("🎨 Generating infographic...")
                try:
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
                        
                        # Update status di spreadsheet
                        try:
                            # Cari row index produk
                            all_products = self.spreadsheet.get_products()
                            for i, p in enumerate(all_products):
                                if p.get('product_name') == product_name:
                                    self.spreadsheet.update_status(i, 'Done')
                                    break
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to update status: {e}")
                        
                        success_count += 1
                        
                    else:
                        error_msg = f"❌ Infographic failed: {info_result.get('error')}"
                        logger.error(error_msg)
                        self.telegram.send_message(error_msg)
                        fail_count += 1
                        
                except Exception as e:
                    error_msg = f"❌ Infographic error: {str(e)}\n{traceback.format_exc()[:200]}"
                    logger.error(error_msg)
                    self.telegram.send_message(error_msg)
                    fail_count += 1
                
                logger.info(f"✅ Completed: {product_name}")
            
            # Kirim notifikasi selesai
            summary = f"""
✅ <b>Pipeline Completed!</b>

📊 Total produk: {len(products)}
✅ Sukses: {success_count}
❌ Gagal: {fail_count}
            """
            self.telegram.send_message(summary)
            logger.info(summary)
            
        except Exception as e:
            error_msg = f"❌ <b>Pipeline CRASHED!</b>\n\n{str(e)}\n\n{traceback.format_exc()[:500]}"
            logger.error(error_msg)
            self.telegram.send_message(error_msg)
            raise
        
        logger.info("✅ Pipeline completed!")

if __name__ == "__main__":
    pipeline = ContentPipeline()
    pipeline.run()
