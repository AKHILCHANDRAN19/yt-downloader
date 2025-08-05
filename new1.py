import os
from yt_dlp import YoutubeDL
from tqdm import tqdm
import logging

# Optional: Suppress yt-dlp's own logging for a cleaner interface
logging.getLogger("yt_dlp").setLevel(logging.ERROR)

def download_video_cpu_friendly(url, output_path):
    """
    Downloads a YouTube video in a CPU-friendly way by seeking
    pre-merged formats, using a 'tqdm' progress bar.
    This version correctly handles the progress bar updates.
    """

    # This hook is called by yt-dlp. We use a dictionary to maintain state.
    progress_state = {}

    def progress_hook(d):
        if d['status'] == 'downloading':
            # Initialize the tqdm bar on the first 'downloading' status
            if 'pbar' not in progress_state and d.get('total_bytes'):
                progress_state['pbar'] = tqdm(
                    total=d['total_bytes'],
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=os.path.basename(d.get('filename', 'downloading...')),
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'
                )

            # Update the progress bar
            if 'pbar' in progress_state:
                pbar = progress_state['pbar']
                # Calculate the increment since the last call
                increment = d.get('downloaded_bytes', 0) - pbar.n
                # Update the tqdm bar instance
                pbar.update(increment)

        elif d['status'] == 'finished':
            # Close the progress bar and clean up
            if 'pbar' in progress_state:
                progress_state['pbar'].close()
                del progress_state['pbar']
            
            print(f"\n✅ Download complete: {os.path.basename(d.get('info_dict', {}).get('filename'))}")

    # --- CPU-Friendly yt-dlp Options ---
    ydl_opts = {
        'format': 'best[height<=720][vcodec!=none][acodec!=none]/best[height<=720]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,  # Important: disable yt-dlp's built-in progress bar
    }

    print("⬇️  Preparing to download (CPU-Friendly Mode)...")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        # Ensure the progress bar is closed on error
        if 'pbar' in progress_state:
            progress_state['pbar'].close()

        if "format best[height<=720][vcodec!=none][acodec!=none] not available" in str(e):
            print("\n❌ A pre-merged 720p format is not available for this video.")
            print("   This can happen with very new videos or certain live streams.")
        else:
            print(f"\n❌ An error occurred: {e}")


if __name__ == "__main__":
    # Standard path to the user's Videos folder on Android
    videos_folder = '/storage/emulated/0/Videos'

    # Ensure the target directory exists
    if not os.path.exists(videos_folder):
        print(f"Creating directory: {videos_folder}")
        os.makedirs(videos_folder)

    try:
        # Get URL from user
        full_url = input("Enter the YouTube video URL: ")
        
        # A simple way to clean up URLs that might include extra parameters
        if '?' in full_url:
            full_url = full_url.split('?')[0]
        
        if full_url:
            download_video_cpu_friendly(full_url, videos_folder)
        else:
            print("No URL entered. Exiting.")
            
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled by user. Exiting.")
