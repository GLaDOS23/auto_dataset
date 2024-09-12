import pyperclip
import pyautogui
import time
import requests
from bs4 import BeautifulSoup

# Настройки
input_file = 'input.txt'  # Входной файл
output_file = 'output.txt'  # Выходной файл
chunk_size = 100  # Максимальный размер текста в одной части
search_delay = 2  # Задержка перед выполнением поиска (в секундах)
browser_name = 'Google Chrome'  # Название браузера

# Функция для чтения и разбивки текста на части
def split_text_into_chunks(file_path, max_size):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    words = text.split()
    chunks = []
    chunk = ''
    for word in words:
        if len(chunk) + len(word) + 1 > max_size:
            chunks.append(chunk.strip())
            chunk = word
        else:
            chunk += ' ' + word
    if chunk:
        chunks.append(chunk.strip())
    return chunks

# Функция для выполнения поиска
def perform_search(text):
    pyperclip.copy(text)  # Копируем текст в буфер обмена
    pyautogui.hotkey('ctrl', 't')  # Открываем новую вкладку
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'l')  # Переходим в строку адреса
    pyautogui.hotkey('ctrl', 'v')  # Вставляем текст
    pyautogui.press('enter')  # Нажимаем Enter
    time.sleep(search_delay)  # Задержка для загрузки результатов

    # Эмуляция копирования содержимого страницы (может не работать корректно с сайтами)
    pyautogui.hotkey('ctrl', 'a')  # Выделяем все
    pyautogui.hotkey('ctrl', 'c')  # Копируем выделенное
    time.sleep(1)
    return pyperclip.paste()

# Основной код
chunks = split_text_into_chunks(input_file, chunk_size)

with open(output_file, 'w', encoding='utf-8') as out_file:
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}")
        result = perform_search(chunk)  # Выполняем поиск и получаем результат
        out_file.write(result + '\n\n')  # Записываем результат в выходной файл

print("Процесс завершён.")
