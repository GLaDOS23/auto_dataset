

import re
import pyautogui
import pyperclip

import time
import os

import keyboard
import cv2
import numpy as np


def on_press_w(event):
    global xp1, xp2, yp1, yp2 , x1, y1, x2, y2
    if event.name == '1':
        xp1, yp1 = pyautogui.position()
        print(f'1) вставка: x={xp1}, y={yp1}')
    if event.name == '2':
        x1, y1 = pyautogui.position()
        print(f'1) копирование: x={x1}, y={y1}')
    if event.name == '3':
        xp2, yp2 = pyautogui.position()
        print(f'2) вставка: x={xp2}, y={yp2}')
    if event.name == '4':
        x2, y2 = pyautogui.position()
        print(f'2) копирование: x={x2}, y={y2}')
def get_text_from_screen(xf2, yf2):
    #x2 = 624
    #y2 = 861    
    pyautogui.moveTo(xf2, yf2, duration=0.5)
        
    # Эмулируем нажатие левой клавиши мыши
    pyautogui.doubleClick()
    pyautogui.click()
    time.sleep(0.2)  
    pyautogui.hotkey('ctrl', 'c')
    # Извлечение текста из буфера обмена
    copied_text = pyperclip.paste()
    return copied_text




#вставить текст
def paste_text_at(text, xf2, yf2):

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
    pyautogui.moveTo(xf2, yf2, duration=0.5)
    
    # Эмулируем нажатие левой клавиши мыши
    pyautogui.click()
    # Нажимаем сочетание клавиш Ctrl+V для вставки текста
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.hotkey('enter')
    # Пауза для завершения вставки текста
    time.sleep(0.5)




    
def on_press_q(event):
    global xp1, xp2, yp1, yp2 , x1, y1, x2, y2
    if event.name == 'q':

        # Открываем и читаем текстовый файл
        with open('combined_file.txt', 'r', encoding='utf-8') as file:
            text = file.read()

        # Разбиваем текст по знакам препинания ., !, ?
        sentences = re.split(r'[.!?]', text)

        # Убираем лишние пробелы и пустые строки
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        print(len(sentences))
        time.sleep(4)
        nom_sentence = 1678# 296  848  535
        del sentences[0:nom_sentence]

        # Выводим список предложений

        for i, sentence in enumerate(sentences, start=1):

            print(f"{i}: {sentence}")
            
            paste_text_at(sentence,xp1,yp1 )
            time.sleep(2)
            paste_text_at(sentence, xp2, yp2)
            
            time.sleep(40)
            
            extracted_text1 = get_text_from_screen(x1, y1)
            time.sleep(2)
            extracted_text2 = get_text_from_screen(x2, y2)
          
            # Записываем результат в файл
            with open('outCaiT0(2)_text.txt', 'a', encoding='utf-8') as file:
                file.write(sentence + '\n' + extracted_text1 + '\n')
            with open('outCaiT1(2)_text.txt', 'a', encoding='utf-8') as file:
                file.write(sentence + '\n' + extracted_text2 + '\n')

            time.sleep(1)
        time.sleep(60)
        #os.system('shutdown -s')#автоматическое отключение системы
keyboard.on_press(on_press_w)
keyboard.on_press(on_press_q)
keyboard.wait('esc')  # Ждем нажатия клавиши esc для завершения программы
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

