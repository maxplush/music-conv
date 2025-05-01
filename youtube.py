import requests
import re
import time
import json
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import ffmpeg  # Import ffmpeg-python to handle conversions

# ➡️ Load previously scraped tracks
with open("tracks.json", "r") as f:
    tracks = json.load(f)

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

# ➡️ Download only YouTube audio using pytubefix
def download_audio(yt_url, track):
    try:
        yt = YouTube(yt_url, on_progress_callback=on_progress)

        # Helper function to get the best audio stream
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

        # Download the audio stream as a .webm file (common for YouTube audio)
        yt.streams.get_by_itag(audio_itag).download(output_path="./downloads", filename=f"{track['artist']} - {track['title']}_audio.webm")

        print(f"✅ Downloaded audio for {track['artist']} - {track['title']}")

        # Convert the downloaded .webm file to .mp3
        convert_webm_to_mp3(f"./downloads/{track['artist']} - {track['title']}_audio.webm")

    except Exception as e:
        print(f"❌ Failed to download audio for {track['artist']} - {track['title']}: {e}")

# ➡️ Convert .webm file to .mp3 using ffmpeg-python
def convert_webm_to_mp3(input_file_path):
    # Set output file path with .mp3 extension
    output_file_path = input_file_path.replace('.webm', '.mp3')

    try:
        # Run the conversion using ffmpeg-python
        ffmpeg.input(input_file_path).output(output_file_path, acodec='libmp3lame').run()
        print(f"✅ Converted {input_file_path} to {output_file_path}")

        # Remove the original .webm file to save space
        os.remove(input_file_path)
        print(f"🗑️ Deleted {input_file_path}")
    except ffmpeg.Error as e:
        print(f"❌ Failed to convert {input_file_path} to MP3: {e}")

# ➡️ Search and collect results for first 5 tracks
youtube_links = []
print("\n🔗 Searching YouTube for extracted tracks (first 5)...")
for i, track in enumerate(tracks[:5], 1):  # Limit to first 5 tracks for testing
    yt_link = search_youtube(track)
    print(f"{i:02d}. {track['artist']} - {track['title']}")
    if yt_link:
        print(f"    🎥 {yt_link}")
        youtube_links.append({**track, 'youtube': yt_link})

        # Download only audio
        download_audio(yt_link, track)

    else:
        print(f"    ❌ No link found")
    time.sleep(1.5)  # delay to avoid rate limiting

# ➡️ Save links
with open("tracks_with_youtube.json", "w") as f:
    json.dump(youtube_links, f, indent=2)

print(f"\n✅ Saved 5 tracks with YouTube links to tracks_with_youtube.json")
