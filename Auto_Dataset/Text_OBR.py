#!pip install deepmultilingualpunctuation

import re
from deepmultilingualpunctuation import PunctuationModel
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

from google.colab import drive

drive.mount('/content/drive', force_remount=True)

# Загрузим модель пунктуации
model = PunctuationModel()

# Функция для очистки текста от лишних слов
def clean_text(text):
    filler_words = ["oh", "my", "gosh", "thank you", "so much", "just", "consistently", "play"]
    for word in filler_words:
        text = re.sub(r"\b" + re.escape(word) + r"\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Функция для определения говорящего
def determine_speaker(sentence, is_user_turn):
    if is_user_turn:
        return "User:"
    else:
        return "Bot:"

# Основная функция обработки текста
def process_dialogue_without_labels(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Очистим текст
    #cleaned_text = clean_text(text)
    
    # Добавим пунктуацию ко всему тексту
    punctuated_text = model.restore_punctuation(text)
    
    # Разделим текст на предложения
    sentences = sent_tokenize(punctuated_text)
    
    # Определим говорящего для каждого предложения
    processed_dialogue = []
    is_user_turn = True  # Начинаем с предположения, что первым говорит пользователь

    for sentence in sentences:
        speaker = determine_speaker(sentence, is_user_turn)
        processed_dialogue.append(f"{speaker} {sentence}")
        
        # Меняем говорящего на следующий раз
        is_user_turn = not is_user_turn

    # Запишем результат в выходной файл
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in processed_dialogue:
            file.write(line + "\n\n")  # Каждую реплику на новой строке

# Пример использования
input_file = "/content/drive/My Drive/Sam_combined2.txt"    # Файл с исходным текстом
output_file = "/content/drive/My Drive/Sam_combinedTT.txt"  # Файл для сохранения результата

process_dialogue_without_labels(input_file, output_file)
