import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json
import re
import time
import os

load_dotenv()

# ➡️ Your SoundCloud client_id

client_id = os.getenv("SOUNDCLOUD_CLIENT_ID")
if not client_id:
    raise EnvironmentError("❌ SOUNDCLOUD_CLIENT_ID is not set in the environment")

# ➡️ Helper to fetch full track info by track ID
def fetch_full_track(track_id, client_id):
    url = f"https://api-v2.soundcloud.com/tracks/{track_id}?client_id={client_id}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            return {
                'artist': data.get('user', {}).get('username', 'Unknown Artist'),
                'title': data.get('title')
            }
        else:
            print(f"❌ Failed to fetch track {track_id} - {res.status_code}")
            return None
    except requests.RequestException as e:
        print(f"❌ Error while fetching track {track_id}: {e}")
        return None

def extract_tracks_from_playlist(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch page: {res.status_code}")

    soup = BeautifulSoup(res.text, 'html.parser')

    # Look for embedded JSON in <script> tag
    scripts = soup.find_all('script')
    hydration_script = next(
        (s.text for s in scripts if 'window.__sc_hydration' in s.text), None)

    if not hydration_script:
        raise Exception("Hydration script not found")

    # Extract the JSON string
    match = re.search(r'window\.__sc_hydration = (.*?);\s*</script>', hydration_script + '</script>')
    if not match:
        raise Exception("Could not parse hydration JSON")

    raw_json = match.group(1)
    try:
        json_data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise Exception("JSON decode error") from e

    # Find playlist and track data
    playlist_obj = next(
        (entry['data'] for entry in json_data if entry.get('hydratable') == 'playlist'), None)

    if not playlist_obj:
        raise Exception("Playlist data not found in hydration JSON")

    tracks = playlist_obj.get('tracks', [])
    if not tracks:
        print("No tracks found in playlist.")
        return []

    # Now properly build the full track list
    track_list = []
    for t in tracks:
        user = t.get('user')
        title = t.get('title')

        if user and title:
            track_list.append({
                'artist': user.get('username', 'Unknown Artist'),
                'title': title
            })
        else:
            print(f"⚠️ Missing data for track ID {t.get('id')}, fetching full metadata...")
            fallback = fetch_full_track(t['id'], client_id)
            if fallback:
                track_list.append(fallback)
            else:
                print(f"⚠️ Could not enrich track ID {t.get('id')}")

        # Respectful delay
        time.sleep(1)  # Slight increase in delay to handle rate limiting better

    return track_list

# # ➡️ Test run on your playlist
# playlist_url = "https://soundcloud.com/plushseconds/sets/cs_35"
# tracks = extract_tracks_from_playlist(playlist_url)


# # Save extracted tracks to a file
# with open("tracks.json", "w") as f:
#     json.dump(tracks, f, indent=2)

# print(f"\n✅ Extracted and saved {len(tracks)} tracks to tracks.json")

def main():
    playlist_url = "https://soundcloud.com/plushseconds/sets/cs_35"
    tracks = extract_tracks_from_playlist(playlist_url)
    with open("tracks.json", "w") as f:
        json.dump(tracks, f, indent=2)
    print(f"\n✅ Extracted and saved {len(tracks)} tracks to tracks.json")

if __name__ == "__main__":
    main()

