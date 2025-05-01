import requests
import re
import time
import json

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

# ➡️ Search and collect results
youtube_links = []
print("\n🔗 Searching YouTube for extracted tracks...")
for i, track in enumerate(tracks, 1):
    yt_link = search_youtube(track)
    print(f"{i:02d}. {track['artist']} - {track['title']}")
    if yt_link:
        print(f"    🎥 {yt_link}")
        youtube_links.append({**track, 'youtube': yt_link})
    else:
        print(f"    ❌ No link found")
    time.sleep(1.5)  # delay to avoid rate limiting

# ➡️ Save links
with open("tracks_with_youtube.json", "w") as f:
    json.dump(youtube_links, f, indent=2)

print(f"\n✅ Saved {len(youtube_links)} tracks with YouTube links to tracks_with_youtube.json")
