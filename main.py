import os
from tqdm import tqdm
import yt_dlp as ytdl

# Define the download folder
DOWNLOAD_FOLDER = '/storage/emulated/0/Download'

def download_progress_hook(d):
    if d['status'] == 'downloading':
        pbar.update(d['downloaded_bytes'] - pbar.n)

def get_video_info(url):
    ydl_opts = {'quiet': True, 'noplaylist': True}
    with ytdl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

def download_video(url, format_code):
    global pbar
    info = get_video_info(url)
    title = info['title']

    # Prepare options for yt-dlp
    ydl_opts = {
        'format': format_code,
        'progress_hooks': [download_progress_hook],
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
    }

    # Download video
    with ytdl.YoutubeDL(ydl_opts) as ydl:
        pbar = tqdm(total=0, unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading")
        ydl.download([url])
        pbar.close()

    print(f"Downloaded: {title}")

def main():
    print("Enter the URL of the YouTube video or shorts:")
    url = input().strip()

    print("\nSelect quality:")
    print("1. 144p")
    print("2. 360p")
    print("3. 480p")
    print("4. 720p")
    print("5. 1080p")
    print("6. 1440p")
    print("7. 2160p")
    quality_option = int(input("Enter your choice (1-7): "))

    # Map user input to YouTube format codes for each quality
    quality_map = {
        1: '18',   # 144p or lower (usually 360p but capped at lower resolutions)
        2: '18',   # 360p (combined audio and video in mp4)
        3: '135+140',  # 480p video + audio
        4: '136+140',  # 720p video + audio
        5: '137+140',  # 1080p video + audio
        6: '271+140',  # 1440p video + audio
        7: '313+140',  # 2160p video + audio
    }

    format_code = quality_map.get(quality_option, 'best')

    print("\nSelect download type:")
    print("1. Download audio only")
    print("2. Download video only")
    print("3. Download both audio and video")
    download_option = int(input("Enter your choice (1-3): "))

    if download_option == 1:
        format_code = 'bestaudio'
    elif download_option == 2:
        format_code = format_code.split('+')[0]  # Just download the video
    elif download_option == 3:
        pass  # Keep video + audio

    if not (1 <= download_option <= 3):
        print("Invalid option. Exiting.")
        return

    download_video(url, format_code)

if __name__ == "__main__":
    main()
