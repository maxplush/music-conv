import requests
import re
import time
import json
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import ffmpeg

# ➡️ YouTube search helper
def search_youtube(track):
    query = f"{track['artist']} - {track['title']}".replace(' ', '+')
    url = f"https://www.youtube.com/results?search_query={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"❌ YouTube search failed for {query}")
            return None

        video_ids = re.findall(r"watch\?v=(\S{11})", res.text)
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
        else:
            print(f"🔍 No results for {query}")
            return None
    except Exception as e:
        print(f"❌ Error searching YouTube for {query}: {e}")
        return None

# ➡️ Download audio using pytubefix
def download_audio(yt_url, track):
    try:
        yt = YouTube(yt_url, on_progress_callback=on_progress)

        def get_best_audio():
            max_audio = 0
            audio_value = 0
            for audio_stream in yt.streams.filter(only_audio=True):
                abr = int(audio_stream.abr.replace('kbps', ''))
                if abr > max_audio:
                    max_audio = abr
                    audio_value = audio_stream.itag
            return audio_value

        audio_itag = get_best_audio()
        output_path = "./downloads"
        os.makedirs(output_path, exist_ok=True)
        filename = f"{track['artist']} - {track['title']}_audio.webm"
        file_path = os.path.join(output_path, filename)

        yt.streams.get_by_itag(audio_itag).download(output_path=output_path, filename=filename)
        print(f"✅ Downloaded audio for {track['artist']} - {track['title']}")
        convert_webm_to_mp3(file_path)

    except Exception as e:
        print(f"❌ Failed to download audio for {track['artist']} - {track['title']}: {e}")

# ➡️ Convert to MP3
def convert_webm_to_mp3(input_file_path):
    output_file_path = input_file_path.replace('.webm', '.mp3')

    try:
        ffmpeg.input(input_file_path).output(output_file_path, acodec='libmp3lame').run()
        print(f"✅ Converted {input_file_path} to {output_file_path}")
        os.remove(input_file_path)
        print(f"🗑️ Deleted {input_file_path}")
    except ffmpeg.Error as e:
        print(f"❌ Failed to convert {input_file_path} to MP3: {e}")

# ➡️ Main logic: load tracks and run search/download
def main():
    if not os.path.exists("tracks.json"):
        raise FileNotFoundError("❌ 'tracks.json' not found. Please run the scraper first.")

    with open("tracks.json", "r") as f:
        tracks = json.load(f)

    print("\n🔗 Searching YouTube for extracted tracks (first 5)...")
    youtube_links = []

    for i, track in enumerate(tracks[:5], 1):  # limit to 5 for testing
        yt_link = search_youtube(track)
        print(f"{i:02d}. {track['artist']} - {track['title']}")
        if yt_link:
            print(f"    🎥 {yt_link}")
            youtube_links.append({**track, 'youtube': yt_link})
            download_audio(yt_link, track)
        else:
            print("    ❌ No link found")
        time.sleep(1.5)

    # Save links (optional)
    with open("tracks_with_youtube.json", "w") as f:
        json.dump(youtube_links, f, indent=2)

    print(f"\n✅ Saved YouTube links to 'tracks_with_youtube.json'")
    print(f"✅ Downloaded and converted {len(youtube_links)} tracks")

if __name__ == "__main__":
    main()