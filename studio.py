import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import numpy as np
import logging
import asyncio
import edge_tts
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip
from datetime import datetime
import random

# MONKEYPATCH: Fix MoviePy compatibility with Pillow 10+
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Studio")

class Studio:
    def __init__(self):
        self.branding_path = "assets/branding/"
        self.audio_path = "assets/audio/"
        self.output_path = "output/review_queue/"
        
        # Fonts
        self.font_bold_path = os.path.join(self.branding_path, "font_bold.ttf")
        self.font_reg_path = os.path.join(self.branding_path, "font_regular.ttf")
        self.logo_path = os.path.join(self.branding_path, "logo.png")
        
        # Team Colors (Primary, Accent)
        self.team_colors = {
            "Red Bull": ((6, 29, 66), (255, 0, 0)),        # Navy / Red
            "Verstappen": ((6, 29, 66), (255, 0, 0)),
            "Perez": ((6, 29, 66), (255, 0, 0)),
            "Ferrari": ((200, 0, 0), (255, 242, 0)),      # Red / Yellow
            "Leclerc": ((200, 0, 0), (255, 242, 0)),
            "Sainz": ((200, 0, 0), (255, 242, 0)),
            "Mercedes": ((0, 0, 0), (0, 161, 155)),       # Black / Teal
            "Hamilton": ((0, 0, 0), (0, 161, 155)),
            "Russell": ((0, 0, 0), (0, 161, 155)),
            "McLaren": ((255, 128, 0), (71, 199, 252)),   # Papaya / Blue
            "Norris": ((255, 128, 0), (71, 199, 252)),
            "Piastri": ((255, 128, 0), (71, 199, 252)),
            "Aston Martin": ((0, 111, 98), (206, 220, 0)), # Green / Lime
            "Alonso": ((0, 111, 98), (206, 220, 0)),
            # Defaults
            "Default": ((15, 20, 35), (255, 0, 50))
        }

        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.branding_path, exist_ok=True)

    def download_image(self, url, filename):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(filename, 'wb') as out_file:
                out_file.write(response.content)
            return filename
        except Exception:
            return None

    def get_team_colors(self, text):
        """Detect team colors from text."""
        for key, colors in self.team_colors.items():
            if key.lower() in text.lower():
                return colors
        return self.team_colors["Default"]

    def create_gradient(self, width, height, color1, color2):
        """Create a vertical gradient."""
        base = Image.new('RGB', (width, height), color1)
        top = Image.new('RGB', (width, height), color2)
        mask = Image.linear_gradient('L')
        # Rotating mask for vertical gradient
        mask = mask.resize((width, height))
        return Image.composite(base, top, mask)

    def generate_image(self, news_item):
        logger.info(f"Generating PRO image for: {news_item['id']}")
        
        WIDTH, HEIGHT = 1080, 1350
        SPLIT_Y = 850  # Image ends at 850
        CARD_H = HEIGHT - SPLIT_Y
        
        headline = news_item.get('headline_en', '')
        primary_color, accent_color = self.get_team_colors(headline)
        
        # 1. Base Canvas
        canvas = Image.new('RGB', (WIDTH, HEIGHT), primary_color)
        
        # 2. Main Image
        temp_img_path = os.path.join(self.output_path, f"temp_{news_item['id']}.jpg")
        if self.download_image(news_item['image_url'], temp_img_path):
            img = Image.open(temp_img_path)
            # Enhance
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)            
            
            img = self._resize_and_crop(img, WIDTH, SPLIT_Y + 150) # Bleed into card
            
            # Fade bottom of image
            mask = Image.new('L', (WIDTH, img.height), 255)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rectangle([(0, img.height - 200), (WIDTH, img.height)], fill=0)
            # Blur/Gradient mask manually or just paste
             
            canvas.paste(img, (0, 0))
            if os.path.exists(temp_img_path): os.remove(temp_img_path)

        # 3. Info Card Background (Gradient)
        # Create a gradient from Darker Primary to Lighter Primary
        card_bg = self.create_gradient(WIDTH, CARD_H, (5,5,10), primary_color)
        canvas.paste(card_bg, (0, SPLIT_Y))
        
        # 4. Separator Line & Accents
        draw = ImageDraw.Draw(canvas)
        
        # Glow Line
        draw.line([(0, SPLIT_Y), (WIDTH, SPLIT_Y)], fill=accent_color, width=4)
        
        # "Audio Wave" Visualizer
        # Center X
        wave_x_start = WIDTH // 2 - 150
        wave_y = SPLIT_Y 
        for i in range(30):
            h = random.randint(20, 80)
            x = wave_x_start + (i * 10)
            # Draw vertical bars centered on the split line
            draw.line([(x, wave_y - h/2), (x, wave_y + h/2)], fill=accent_color, width=4)

        # 5. Typography
        try:
            # Scaled fonts
            font_title = ImageFont.truetype(self.font_bold_path, 80)
            font_quote = ImageFont.truetype(self.font_bold_path, 50) # Use Bold for quote too to match ref
            font_tag = ImageFont.truetype(self.font_bold_path, 25)
        except:
             font_title = ImageFont.load_default()
             font_quote = ImageFont.load_default()
             font_tag = ImageFont.load_default()

        # Tag (Team Name or Category)
        # Draw skewed box
        tag_text = "RACING TAMIZHAN"
        tag_w = 300
        tag_h = 40
        tag_x = WIDTH - tag_w - 50
        tag_y = SPLIT_Y - 20 # Overlap split
        
        # Box background
        draw.polygon([
            (tag_x, tag_y), 
            (tag_x + tag_w, tag_y), 
            (tag_x + tag_w - 20, tag_y + tag_h), 
            (tag_x - 20, tag_y + tag_h)
        ], fill=accent_color)
        
        draw.text((tag_x + 30, tag_y + 5), tag_text, font=font_tag, fill=(0,0,0))

        # Text Content - Headline
        # UPPERCASE everything for impact
        text_to_draw = headline.upper()
        
        # Dynamic Font Scaling
        # Available height: HEIGHT (1350) - StartY (SPLIT_Y + 100 = 950) - Bottom Padding (50) = 400px
        # We start at 80 and go down.
        
        max_text_height = HEIGHT - (SPLIT_Y + 100) - 50
        current_font_size = 80
        min_font_size = 40
        
        # Iteratively optimize font size
        font_title = None
        while current_font_size >= min_font_size:
            try:
                font_title = ImageFont.truetype(self.font_bold_path, current_font_size)
            except:
                font_title = ImageFont.load_default()
                break
            
            # Check height
            _, text_h = self._get_text_size(text_to_draw, font_title, WIDTH - 100)
            if text_h <= max_text_height:
                break # It fits!
            
            current_font_size -= 5
            
        self._draw_text_wrapped(draw, text_to_draw, font_title, (255, 255, 255), WIDTH - 100, SPLIT_Y + 100, align="center")

        # 6. Logo
        if os.path.exists(self.logo_path):
            logo = Image.open(self.logo_path).convert("RGBA")
            logo.thumbnail((120, 120))
            canvas.paste(logo, (50, SPLIT_Y + 50), logo)

        cover_filename = os.path.join(self.output_path, f"slide1_{news_item['id']}.png")
        canvas.save(cover_filename)
        logger.info(f"Generated Cover: {cover_filename}")
        
        # CLEANUP: User requested NO second slide. 
        # Just return the single image.
        
        if os.path.exists(temp_img_path): os.remove(temp_img_path)

        return cover_filename

    def _resize_and_crop(self, img, target_w, target_h):
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h
        if target_ratio > img_ratio:
            new_w = target_w
            new_h = int(target_w / img_ratio)
        else:
            new_h = target_h
            new_w = int(target_h * img_ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (img.width - target_w) / 2
        top = (img.height - target_h) / 2
        right = (img.width + target_w) / 2
        bottom = (img.height + target_h) / 2
        return img.crop((left, top, right, bottom))

    def _get_text_size(self, text, font, max_width):
        """Calculates the width and height of wrapped text."""
        lines = []
        words = text.split()
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line) 
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
            
        total_h = 0
        max_w = 0
        for line in lines:
            bbox = font.getbbox(line)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            max_w = max(max_w, w)
            total_h += h + 15 # Line spacing
            
        return max_w, total_h

    def _draw_text_wrapped(self, draw, text, font, color, max_width, start_y, align="center"):
        lines = []
        words = text.split()
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line) 
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
            
        y = start_y
        for line in lines:
            bbox = font.getbbox(line)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if align == "center":
                x = (1080 - w) // 2
            else:
                x = 50
            draw.text((x, y), line, font=font, fill=color)
            y += h + 15

    async def _generate_tts(self, text, output_file, voice="en-GB-SoniaNeural"):
        """Async helper to generate TTS."""
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

    def _run_tts_sync(self, text, output_file):
        """Run async TTS in sync context, handling existing loops."""
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running (e.g. Streamlit), use task or run_coroutine_threadsafe?
                    # But we need result synchronously.
                    # Best hack for script usage: Create a new thread?
                    # Or check if nest_asyncio logic is needed.
                    # Simpler fallback: If loop running, just try scheduling it? 
                    # No, let's verify if get_event_loop works.
                    
                    # If we are in a running loop, asyncio.get_event_loop() returns it.
                    # .run_until_complete() will fail if it's running.
                    
                    # Use a new loop in a safe generic way
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(asyncio.run, self._generate_tts(text, output_file))
                        future.result()
                    return True
            except RuntimeError:
                # No loop running, standard run
                asyncio.run(self._generate_tts(text, output_file))
                return True
        except Exception as e:
            logger.error(f"TTS Generation failed: {e}")
            return False

    def _apply_ken_burns(self, clip, zoom_factor=1.1):
        """
        Apply a slow zoom effect (Ken Burns).
        Zoom from 1.0 to zoom_factor over clip duration.
        """
        def zoom(t):
            return 1 + (zoom_factor - 1) * t / clip.duration
        
        return clip.resize(zoom)

    def generate_video(self, news_items):
        """
        Generates a dynamic vertical video digest (Reel/Short) from news items.
        Features: AI Voiceover, Ken Burns Effect, Background Music.
        """
        logger.info(f"Generating advanced video digest for {len(news_items)} items...")
        
        clips = []
        
        # Background Audio (Music) - Load once
        bg_music = None
        if os.path.exists(self.audio_path):
            files = [f for f in os.listdir(self.audio_path) if f.endswith(".mp3")]
            if files:
                bg_music_path = os.path.join(self.audio_path, files[0])
                try:
                    bg_music = AudioFileClip(bg_music_path)
                except:
                    pass

        temp_files = [] # Track for cleanup

        for item in news_items:
            # 1. Get Image
            img_path = self.generate_image(item) # This returns a single path now (Cover)
            if not img_path: continue
            
            # 2. Generate Voiceover
            # Use summary or headline
            text_to_read = item.get('headline_en', '') + ". " + item.get('summary', '')
            # Clean text lightly
            text_to_read = text_to_read.replace("#", "").replace("\n", " ")
            
            audio_path = os.path.join(self.output_path, f"tts_{item['id']}.mp3")
            
            # Check if we should re-generate or reuse? Regenerate for now.
            if self._run_tts_sync(text_to_read, audio_path):
                temp_files.append(audio_path)
            else:
                audio_path = None # Fallback to silence/duration?

            try:
                # 3. Create Audio Clip
                if audio_path and os.path.exists(audio_path):
                    voice_clip = AudioFileClip(audio_path)
                    duration = voice_clip.duration + 0.5 # Add small pause
                else:
                    voice_clip = None
                    duration = 3.0 # Default fallback
                
                # 4. Create Image Clip
                # Enforce resolution? Images are 1080x1350 (4:5). 
                # YouTube Shorts is 1080x1920 (9:16).
                # To fill 9:16 with 4:5, we can center it on black.
                
                img_clip = ImageClip(img_path).set_duration(duration)
                
                # 5. Apply Ken Burns (Zoom)
                # Zoom from 1.0 to 1.15
                img_clip = self._apply_ken_burns(img_clip, zoom_factor=1.15)
                
                # Center on 1080x1920 black background
                # CompositeVideoClip allows layering
                # Create background
                # bg_clip = ColorClip(size=(1080, 1920), color=(0,0,0), duration=duration) # Need ColorClip import
                # Simpler: Just rely on players handling 4:5 or set pos
                
                img_clip = img_clip.set_position("center")
                
                # Combine Audio (Voice)
                if voice_clip:
                    img_clip = img_clip.set_audio(voice_clip)
                
                clips.append(img_clip)

            except Exception as e:
                logger.error(f"Error creating clip for {item['id']}: {e}")

        if not clips:
            return None

        # Concatenate
        logger.info("Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose") # Compose handles resizing better
        
        # Mix Background Music
        if bg_music:
            # Loop music to fit video length
            if bg_music.duration < final_video.duration:
                 # Loop it simple logic, or just let it cut out if short. 
                 # moviepy `afx.audio_loop` needed for proper loop.
                 # Let's just subclip if it's long enough, else repeat manually?
                 pass
            
            # Subclip to duration
            bg_music = bg_music.subclip(0, final_video.duration)
            
            # Lower volume
            bg_music = bg_music.volumex(0.15) 
            
            # Mix with Voice
            if final_video.audio:
                final_audio = CompositeAudioClip([final_video.audio, bg_music])
                final_video = final_video.set_audio(final_audio)
            else:
                final_video = final_video.set_audio(bg_music)

        output_filename = os.path.join(self.output_path, f"reel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        
        # Write file
        # fps=30 for smooth motion
        try:
             final_video.write_videofile(output_filename, fps=30, codec="libx264", audio_codec="aac")
             logger.info(f"Video generated: {output_filename}")
             
             # Cleanup
             for f in temp_files:
                 if os.path.exists(f): os.remove(f)
                 
             return output_filename
        except Exception as e:
             logger.error(f"Video export failed: {e}")
             return None
