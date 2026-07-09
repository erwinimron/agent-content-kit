from custom_pipeline.telegram_sender import TelegramSender

class ContentPipeline:
    def __init__(self):
        self.spreadsheet = SpreadsheetManager()
        self.storytelling = StorytellingGenerator()
        self.infographic = InfographicGenerator()
        self.telegram = TelegramSender()  # ← Tambahkan ini
    
    def run(self):
        # ... kode yang sudah ada ...
        
        # Setelah storytelling selesai
        if story_result.get('status') == 'success':
            self.telegram.send_message(
                f"📝 <b>Storytelling</b>\n\n{story_result['script'][:500]}..."
            )
        
        # Setelah infographic selesai
        if info_result.get('status') == 'success':
            # Kirim 6 gambar infographic
            image_paths = []
            for i in range(1, 7):
                path = os.path.join(output_dir, f"infographic_{i}.png")
                if os.path.exists(path):
                    image_paths.append(path)
            
            if image_paths:
                self.telegram.send_album(
                    image_paths,
                    caption=f"🎨 <b>Infographic</b>\nProduct: {product_name}"
                )
