# custom_pipeline/content_generators/infographic.py
import os
import logging
from google import genai
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

class InfographicGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found")
        self.client = genai.Client(api_key=api_key)
        
    def generate(self, product_data: dict) -> dict:
        """Generate 6-slide infographic for product"""
        product_name = product_data.get('product_name', 'Product')
        price = product_data.get('price', '')
        
        # List slides
        slides = [
            {
                "title": "WAJIB PUNYA!",
                "subtitle": product_name,
                "price": price
            },
            {
                "title": "✅ High Waist",
                "subtitle": "Siluet lebih proporsional"
            },
            {
                "title": "✅ Flare Fit",
                "subtitle": "Kesan kaki lebih jenjang"
            },
            {
                "title": "✅ Premium Fabric",
                "subtitle": "Nyaman seharian"
            },
            {
                "title": "✅ Office & Casual",
                "subtitle": "Multi-occasion outfit"
            },
            {
                "title": "CTA",
                "subtitle": "Klik Keranjang Kuning 🤍",
                "is_cta": True
            }
        ]
        
        images = []
        
        for i, slide in enumerate(slides):
            logger.info(f"📸 Generating slide {i+1}/{len(slides)}: {slide.get('title')}")
            
            # Generate image for this slide
            image_data = self._generate_slide_image(
                slide, 
                product_name, 
                price
            )
            
            images.append(image_data)
        
        return {
            "status": "success",
            "images": images,
            "type": "infographic",
            "total_slides": len(slides)
        }
    
    def _generate_slide_image(self, slide_data: dict, product_name: str, price: str):
        """Generate individual slide image using Gemini"""
        
        # Build prompt for Gemini
        prompt = f"""
        Create a premium minimalist fashion infographic slide for a product.
        
        Product: {product_name}
        Price: {price}
        Main Text: {slide_data.get('title')}
        Subtitle: {slide_data.get('subtitle', '')}
        
        Style Requirements:
        - Color palette: Beige and white (cream, off-white, warm beige)
        - Typography: Modern, elegant, minimalist
        - Layout: Clean, premium fashion catalog style
        - Orientation: Vertical 9:16 (1080x1920)
        - Add subtle icons or elegant geometric elements
        - Premium lifestyle branding feel
        
        Make it look like a luxury ecommerce/fashion brand.
        """
        
        try:
            response = self.client.interactions.create(
                model="gemini-2.0-flash-exp-image-generation",
                input=prompt,
                config={
                    "response_modalities": ["IMAGE"],
                    "image_size": "1080x1920"
                }
            )
            
            # Extract image from response
            if response.images and len(response.images) > 0:
                image_data = response.images[0].image_data
                return image_data
            else:
                logger.warning("No image generated, creating fallback")
                return self._create_fallback_image(slide_data)
                
        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            return self._create_fallback_image(slide_data)
    
    def _create_fallback_image(self, slide_data: dict):
        """Fallback: create simple image with text if Gemini image gen fails"""
        # Create blank image
        img = Image.new('RGB', (1080, 1920), color=(245, 240, 235))
        draw = ImageDraw.Draw(img)
        
        # Simple text
        try:
            font_title = ImageFont.truetype("Arial.ttf", 80)
            font_sub = ImageFont.truetype("Arial.ttf", 40)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
        
        # Draw text
        draw.text((540, 800), slide_data.get('title', ''), 
                  fill=(50, 50, 50), anchor="mm", font=font_title)
        draw.text((540, 1000), slide_data.get('subtitle', ''), 
                  fill=(100, 100, 100), anchor="mm", font=font_sub)
        
        # Convert to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
