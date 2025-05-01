from scraper import main as scrape_main
from youtube import main as youtube_main

def main():
    print("🚀 Starting SoundCloud playlist scrape...")
    scrape_main()
    
    print("\n🎧 Now downloading tracks from YouTube...")
    youtube_main()

if __name__ == "__main__":
    main()
