

import re
import pyautogui
import pyperclip
import time
import os

def get_text_from_screen(x2, y2):
    #x2 = 624
    #y2 = 861    
    pyautogui.moveTo(x2, y2, duration=0.5)
        
    # Эмулируем нажатие левой клавиши мыши
    pyautogui.doubleClick()
    pyautogui.click()
    time.sleep(0.2)  
    pyautogui.hotkey('ctrl', 'c')
    # Извлечение текста из буфера обмена
    copied_text = pyperclip.paste()
    return copied_text




#вставить текст
def paste_text_at(text, x2, y2):

    #x1 = 23
    #y1 = 1011
    #x2 = 705
    #y2 = 968
    # Копируем текст в буфер обмена
    pyperclip.copy(text)
    
    # Наводим мышь на указанную часть экрана
    #pyautogui.moveTo(x1, y1, duration=0.5)
    
    # Эмулируем нажатие левой клавиши мыши
    #pyautogui.click()
    #time.sleep(1)
    # Наводим мышь на указанную часть экрана
    pyautogui.moveTo(x2, y2, duration=0.5)
    
    # Эмулируем нажатие левой клавиши мыши
    pyautogui.click()
    # Нажимаем сочетание клавиш Ctrl+V для вставки текста
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.hotkey('enter')
    # Пауза для завершения вставки текста
    time.sleep(0.5)




    
if __name__ == "__main__":
    # Координаты области экрана (left, top, right, bottom)
    xp1 = 181
    yp1 = 850
    xp2 = 1123
    yp2 = 853

    x1 = 1192
    y1 = 966
    x2 = 238
    y2 = 968
    time.sleep(10)
    # Открываем и читаем текстовый файл
    with open('combined_file.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    # Разбиваем текст по знакам препинания ., !, ?
    sentences = re.split(r'[.!?]', text)

    # Убираем лишние пробелы и пустые строки
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    print(len(sentences))
    time.sleep(4)
    nom_sentence = 0#848  535
    del sentences[0:nom_sentence]

    # Выводим список предложений

    for i, sentence in enumerate(sentences, start=1):

        print(f"{i}: {sentence}")
        paste_text_at(sentence,253, 985)
        time.sleep(2)
        paste_text_at(sentence, 1185, 980)
        
        time.sleep(40)
        
        extracted_text1 = get_text_from_screen(196, 878)
        time.sleep(2)
        extracted_text2 = get_text_from_screen(1126, 877)
      
        # Записываем результат в файл
        with open('outCaiT0(2)_text.txt', 'a', encoding='utf-8') as file:
            file.write(sentence + '\n' + extracted_text1 + '\n')
        with open('outCaiT1(2)_text.txt', 'a', encoding='utf-8') as file:
            file.write(sentence + '\n' + extracted_text2 + '\n')

        time.sleep(1)
    time.sleep(60)
    os.system('shutdown -s')
'''
    while True:
       
        # Получение текста из указанной области экрана
        #extracted_text1 = get_text_from_screen(xp1, yp1)
        #time.sleep(1)

        #paste_text_at(extracted_text1, x1, y1)
        #time.sleep(40)
        extracted_text2 = get_text_from_screen(xp2, yp2)

        time.sleep(1)
        paste_text_at(extracted_text2, x2, y2)
        # Записываем результат в файл
        with open('outCaiT_text.txt', 'a', encoding='utf-8') as file:
            file.write(extracted_text1 + '\n' + extracted_text2 + '\n')

        time.sleep(40)

'''

