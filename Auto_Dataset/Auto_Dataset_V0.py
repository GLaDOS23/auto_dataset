import os
from pydub import AudioSegment
import speech_recognition as sr
import youtube_dl
import yt_dlp as youtube_dl

# Функция для скачивания аудио с YouTube
def download_audio_from_youtube(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return 'audio.wav'

# Функция для разбиения аудио на сегменты по 10 секунд
def split_audio(audio_file, segment_length_ms=10000):
    audio = AudioSegment.from_wav(audio_file)
    segments = [audio[i:i + segment_length_ms] for i in range(0, len(audio), segment_length_ms)]
    return segments

# Функция для преобразования речи в текст с помощью speech_recognition
def transcribe_audio(segment, recognizer):
    with sr.AudioFile(segment) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            #print(f"Transcribed text: {text}")
        except sr.UnknownValueError:
            #print("Google Speech Recognition could not understand audio")
            text = ""
        except sr.RequestError as e:
            #print(f"Could not request results from Google Speech Recognition service; {e}")
            text = f"Error: {e}"
    return text

# Основная программа
def main(video_url, nom):
    recognizer = sr.Recognizer()
    audio_file = download_audio_from_youtube(video_url)
    segments = split_audio(audio_file)
    os.remove(audio_file)

    txtf = "transcription" + str(nom) + ".txt"

    
    with open(txtf, "w", encoding='utf-8') as f:
        for i, segment in enumerate(segments):
            #print(f"Processing segment {i + 1} of {len(segments)}")
            segment.export("segment.wav", format="wav")
            text = transcribe_audio("segment.wav", recognizer)
            f.write(text + '\n')
            os.remove("segment.wav")
    
    #print("Transcription completed successfully.")



#получение ссылок
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
                #print("No videos found in the channel.")
                return []
        except Exception as e:
            #print(f"Error: {e}")
            return []

channel_url = 'https://www.youtube.com/c/@Name/videos'
video_links = get_channel_videos(channel_url)
# Пример использования
if __name__ == "__main__":

    nom = 0

    if video_links:
        for link in video_links:
            #print(link)
            #video_url = "https://www.youtube.com/watch?v=" + link
            main(link,nom)
            nom += 1
    else:
        print("No videos found or an error occurred.")
    

