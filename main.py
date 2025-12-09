import os
import json
import logging
from scout import Scout
from studio import Studio
from publisher import Publisher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

def main():
    logger.info("Starting Racing Tamizhan Auto System...")

    # Initialize Agents
    scout = Scout()
    studio = Studio()
    publisher = Publisher()

    # 1. Scout: Fetch Content
    logger.info("Agent Alpha (Scout) working...")
    news_items = scout.fetch_news()
    if not news_items:
        logger.info("No new items found.")
        return

    # 2. Studio: Generate Assets
    logger.info(f"Agent Beta (Studio) processing {len(news_items)} items...")
    generated_assets = []
    
    for item in news_items:
        # Generate Image
        image_path = studio.generate_image(item)
        if image_path:
            generated_assets.append({
                "type": "image",
                "path": image_path,
                "data": item
            })
            
    # Generate Video (Reel) if enough items
    if len(news_items) >= 3:
        video_path = studio.generate_video(news_items)
        if video_path:
             generated_assets.append({
                "type": "video",
                "path": video_path,
                "data": {"headline_en": "Top Stories", "id": "reel"} # Generic data for reel
            })

    # 3. Human-in-the-Loop Review
    logger.info("Human Review Required.")
    logger.info(f"Assets generated in: {studio.output_path}")
    
    approved_assets = []
    for asset in generated_assets:
        print(f"\nReview Asset: {asset['type']} - {asset['path']}")
        if asset['type'] == 'image':
            print(f"Headline: {asset['data']['headline_en']}")
        
        choice = input("Approve for upload? (y/n): ").lower()
        if choice == 'y':
            approved_assets.append(asset)
    
    if not approved_assets:
        logger.info("No assets approved for upload.")
        return

    # 4. Publisher: Deploy
    logger.info(f"Agent Gamma (Publisher) uploading {len(approved_assets)} assets...")
    
    # Login check
    ig_user = os.getenv("IG_USERNAME")
    ig_pass = os.getenv("IG_PASSWORD")
    if ig_user and ig_pass:
        publisher.login_instagram(ig_user, ig_pass)
    else:
        logger.warning("Instagram credentials not set in .env")

    for asset in approved_assets:
        if asset['type'] == 'image':
            # Instagram Photo
            caption = f"Breaking News! 🏎️💨\n\n{asset['data']['headline_en']}\n\n#RacingTamizhan #F1 #MotoGP"
            # publisher.upload_instagram_photo(asset['path'], caption) # Uncomment to enable
            logger.info(f"(Dry Run) Uploading Photo: {asset['path']}")
            
        elif asset['type'] == 'video':
            # Instagram Reel
            caption = "Top Racing Stories! 🏎️🔥 #RacingTamizhan #Reels"
            # publisher.upload_instagram_reel(asset['path'], caption) # Uncomment to enable
            logger.info(f"(Dry Run) Uploading Reel: {asset['path']}")
            
            # YouTube Short
            title = "Latest Racing News | Racing Tamizhan"
            # publisher.upload_youtube_short(asset['path'], title) # Uncomment to enable
            logger.info(f"(Dry Run) Uploading Short: {asset['path']}")

    logger.info("Mission Complete.")

if __name__ == "__main__":
    main()
