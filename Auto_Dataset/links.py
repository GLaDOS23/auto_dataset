import youtube_dl

def get_channel_videos(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(channel_url, download=False)
            if 'entries' in result:
                video_links = [entry['url'] for entry in result['entries']]
                return video_links
            else:
                print("No videos found in the channel.")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []


channel_url = 'https://www.youtube.com/c/@Obsidian Time/videos'
video_links = get_channel_videos(channel_url)

if video_links:
    for link in video_links:
        print(link)
else:
    print("No videos found or an error occurred.")



