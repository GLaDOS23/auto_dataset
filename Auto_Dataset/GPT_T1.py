import pyperclip
import pyautogui
import time

# Функция для чтения файла
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

# Функция для записи результата в файл
def write_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

# Функция для разбиения текста на фрагменты
def split_text(text, max_len=3000):
    sentences = text.split(' ')
    current_chunk = ""
    chunks = []
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 > max_len:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ' '
        else:
            current_chunk += sentence + ' '
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# Функция для создания запроса в GPT
def create_gpt_request(text_chunk):
    prompt = f"Redo the following text into a sequential dialogue with replicas without information from you or the quotes separated by a symbol \\n:\n\n{text_chunk}"
    pyperclip.copy(prompt)  # Копируем текст в буфер обмена
    time.sleep(0.3)
    # Наводим мышь на указанную часть экрана
    pyautogui.moveTo(847, 983, duration=0.5)
    
    # Эмулируем нажатие левой клавиши мыши
    pyautogui.click()
    time.sleep(0.4)
    pyautogui.hotkey('ctrl', 'v')  # Вставляем текст
    time.sleep(0.6)
    pyautogui.press('enter')  # Нажимаем Enter
    # Наводим мышь на указанную часть экрана
    time.sleep(0.1)
    pyautogui.moveTo(756, 890, duration=0.2)
    
    # Эмулируем нажатие левой клавиши мыши
    pyautogui.mouseDown(button='left')
    time.sleep(30)
    pyautogui.moveTo(1494, 983, duration=0.2)
    time.sleep(120)
    pyautogui.mouseUp(button='left')
    pyautogui.hotkey('ctrl', 'c')  # Копируем выделенное
    time.sleep(1)
    return pyperclip.paste()

# Основная функция
def process_conversation(input_filename, output_filename, max_chunk_len=3000):
    # Чтение файла
    raw_text = read_file(input_filename)
    
    # Разбиваем текст на фрагменты
    text_chunks = split_text(raw_text, max_chunk_len)
    
    # Проходимся по каждому фрагменту и преобразуем его в диалог
    all_responses = []
    for chunk in text_chunks:
        response = create_gpt_request(chunk)
        all_responses.append(response)
    
    # Объединяем все ответы и записываем их в файл
    formatted_dialogue = "\n\n".join(all_responses)
    write_file(output_filename, formatted_dialogue)

# Пример использования
input_file = "нейро.txt"  # исходный файл
output_file = "formatted_dialogue.txt"    # файл с результатом
process_conversation(input_file, output_file)
