import os
from pydub import AudioSegment
import speech_recognition as sr

# Функция для получения списка WAV файлов из папки
def get_wav_files_from_folder(folder_path):
    wav_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.wav'):
            wav_files.append(os.path.join(folder_path, file))
    return sorted(wav_files)  # Сортируем для предсказуемости порядка

# Функция для преобразования речи в текст с помощью speech_recognition
def transcribe_audio(audio_file_path, recognizer):
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='en-US')  # ru-RU
                return text
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                return f"Error: {e}"
    except Exception as e:
        return f"File Error: {e}"

# Основная программа
def main(input_folder, output_file):
    recognizer = sr.Recognizer()
    wav_files = get_wav_files_from_folder(input_folder)
    
    if not wav_files:
        print(f"No WAV files found in folder: {input_folder}")
        return
    
    print(f"Found {len(wav_files)} WAV files to process")
    
    with open(output_file, "w", encoding='utf-8') as f:
        for i, wav_file in enumerate(wav_files):
            print(f"Processing file {i + 1} of {len(wav_files)}: {os.path.basename(wav_file)}")
            
            text = transcribe_audio(wav_file, recognizer)
            f.write(text + '\n')
            f.flush()  # Обеспечиваем запись после каждого файла
    
    print(f"Transcription completed successfully. Results saved to: {output_file}")

# Пример использования
if __name__ == "__main__":
    # Укажите путь к папке с WAV файлами
    input_folder = "D:/Хз2"  # Замените на реальный путь
    
    # Укажите путь к выходному TXT файлу
    output_file = "transcription_results.txt"
    
    main(input_folder, output_file)
