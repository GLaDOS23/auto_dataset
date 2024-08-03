import os
from pydub import AudioSegment
import speech_recognition as sr
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
            print(f"Transcribed text: {text}")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            text = ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            text = f"Error: {e}"
    return text

# Основная программа
def main(video_url):
    recognizer = sr.Recognizer()
    audio_file = download_audio_from_youtube(video_url)
    segments = split_audio(audio_file)
    os.remove(audio_file)
    
    with open("transcription.txt", "w", encoding='utf-8') as f:
        for i, segment in enumerate(segments):
            print(f"Processing segment {i + 1} of {len(segments)}")
            segment.export("segment.wav", format="wav")
            text = transcribe_audio("segment.wav", recognizer)
            f.write(text + '\n')
            os.remove("segment.wav")
    
    print("Transcription completed successfully.")

# Пример использования
if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v="
    main(video_url)
