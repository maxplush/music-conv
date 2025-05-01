# Playlist Ripper 🎵

This project scrapes a SoundCloud playlist and downloads matching audio tracks from YouTube. The output is saved as `.mp3` files.

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/music-conv.git
cd music-conv
```

### 2. Create a `.env` File

Create a `.env` file in the root directory and add your SoundCloud `client_id`:

```
CLIENT_ID=your_client_id_here
```

> 💡 **How to get a `client_id`**:
>
> - Go to any of your SoundCloud playlists in your browser.
> - Right-click > Inspect > Network tab.
> - Refresh the page and look for network requests that contain `client_id=...`.
> - Copy and paste the value into your `.env` file.

### 3. Install Dependencies

First, create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

Then install the required Python packages:

```bash
pip install -r requirements.txt
```

Also, install `ffmpeg` for audio conversion:

```bash
brew install ffmpeg
```

## 🚀 Running the Project

Run the main script:

```bash
python main.py
```

This will:
- Scrape track metadata from the provided SoundCloud playlist.
- Save the data to `tracks.json`.
- Search YouTube for matching audio.
- Download and convert up to 5 audio tracks to `.mp3`.

The downloaded `.mp3` files will be saved in a `downloads/` directory.

## Output

- `tracks.json`: Raw track metadata from SoundCloud.
- `downloads/`: Folder containing downloaded `.mp3` audio.
- `tracks_with_youtube.json`: Tracks with matching YouTube links.

## ⚠️ Disclaimer

This project is intended **for educational and personal use only**. Downloading copyrighted content without permission may violate YouTube or SoundCloud's Terms of Service and/or copyright laws in your jurisdiction.  

**The author does not condone or encourage piracy in any form.** Use responsibly.
