# custom_pipeline/content_generators/storytelling.py
import os
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class StorytellingGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found")
        self.client = genai.Client(api_key=api_key)
    
    def generate(self, product_data: dict) -> dict:
        """Generate storytelling content using Auth Key"""
        product_name = product_data.get('product_name', 'Product')
        description = product_data.get('description', '')
        price = product_data.get('price', '')
        
        prompt = f"""
        Buat script storytelling pendek (30-45 detik) untuk produk fashion berikut:
        
        Produk: {product_name}
        Harga: {price}
        Deskripsi: {description}
        
        Gaya: Santai, relatable, dan informatif. Target: wanita muda urban.
        Format: 3-4 paragraf pendek untuk voiceover video.
        """
        
        try:
            # Panggil Gemini API dengan cara baru
            response = self.client.interactions.create(
                model="gemini-2.5-flash",  # atau "gemini-2.0-flash-exp"
                input=prompt
            )
            script = response.output_text
            
            # Generate caption
            caption_prompt = f"""
            Buat caption Instagram/Facebook untuk produk {product_name}.
            Include 5-10 hashtag yang relevan.
            Gaya: engaging, casual, dan stylish.
            """
            caption_response = self.client.interactions.create(
                model="gemini-2.5-flash",
                input=caption_prompt
            )
            caption = caption_response.output_text
            
            return {
                "status": "success",
                "script": script,
                "caption": caption,
                "type": "storytelling"
            }
            
        except Exception as e:
            logger.error(f"❌ Storytelling generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
