

import re
import pyautogui
import pyperclip

import time
import os

import keyboard
import cv2
import numpy as np
import random
from PIL import Image


def on_press_q(x , y):



    screenshot = pyautogui.screenshot()

    # Определить цвет пикселя
    pixel_color = screenshot.getpixel((x, y))

    # Цвет в формате RGB
    target_color = (209, 213, 219)  # RGB
    #print(pixel_color )
    # Сравнение цветов
    if pixel_color == target_color:
        return True
    else:
        return False  



def compare_strings(str1, str2):#проверка на повтор
    # Проверяем первое слово в строке
    first_space_index1 = str1.find(' ')
    first_space_index2 = str2.find(' ')

    if first_space_index1 == -1 or first_space_index2 == -1:
        return 0

    first_word1 = str1[:first_space_index1]
    first_word2 = str2[:first_space_index2]

    if first_word1 != first_word2:
        return 0

    # Проверяем последнее слово в строке
    last_space_index1 = str1.rfind(' ')
    last_space_index2 = str2.rfind(' ')

    if last_space_index1 == -1 or last_space_index2 == -1:
        return 0

    last_word1 = str1[last_space_index1 + 1:]
    last_word2 = str2[last_space_index2 + 1:]

    if last_word1 == last_word2:
        return 1
    else:
        return 0

    

def on_press_w(event):
    global xp1, xp2, yp1, yp2 , x1, y1, x2, y2, xu1, yu1
    if event.name == '1':
        xp1, yp1 = pyautogui.position()
        print(f'1) вставка: x={xp1}, y={yp1}')
    if event.name == '2':
        x1, y1 = pyautogui.position()
        print(f'1) копирование: x={x1}, y={y1}')
    if event.name == '3':#для обновления генератора
        xu1, yu1 = pyautogui.position()
        print(f'1) удаление: x={x1}, y={y1}')
    if event.name == '4':#для обновления генератора
        xp2, yp2 = pyautogui.position()
        print(f'1) проверка: x={xp2}, y={yp2}')
    if event.name == '5':#для обновления генератора
        x2, y2 = pyautogui.position()
        print(f'1) рестарт: x={x2}, y={y2}')    
    '''
    if event.name == '3':
        xp2, yp2 = pyautogui.position()
        print(f'2) вставка: x={xp2}, y={yp2}')
    if event.name == '4':
        x2, y2 = pyautogui.position()
        print(f'2) копирование: x={x2}, y={y2}')
    '''
def get_text_from_screen(xf2, yf2):
    #x2 = 624
    #y2 = 861    
    pyautogui.moveTo(xf2, yf2, duration=0.5)
        
    # Эмулируем нажатие левой клавиши мыши
    time.sleep(0.2)
    #pyautogui.doubleClick()
    pyautogui.click()
    time.sleep(0.2)
    pyautogui.click()
    #pyautogui.hotkey('ctrl', 'c')
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
    time.sleep(1)
    pyautogui.hotkey('enter')
    time.sleep(0.2)
    pyautogui.hotkey('enter')
    time.sleep(0.2)
    pyautogui.hotkey('enter')
    time.sleep(0.2)
    pyautogui.hotkey('enter')
    # Пауза для завершения вставки текста
    time.sleep(0.5)




    
def on_press(event):
    global xp1, xp2, yp1, yp2 , x1, y1, x2, y2, xu1, yu1
    if event.name == 'q':

        # Открываем и читаем текстовый файл
        with open('Elli4.txt', 'r', encoding='utf-8') as file:
            text = file.read()

        # Разбиваем текст по знакам препинания ., !, ?
        sentences = re.split(r'&', text)

        # Убираем лишние пробелы и пустые строки
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        print(len(sentences))
        time.sleep(4)
        nom_sentence = 2249
        del sentences[0:nom_sentence]

        # Выводим список предложений
        extracted_text1 = ""
        extracted_text1T = ""
        nom_text1T = 0# filian3.txt - 2035
        #stroc = ['Imagine that you are an AI', 'Imagine that you are a person with artificial intelligence', 'Imagine that you are a cheerful AI gamer','Imagine that you are an AI gamer communicating with an audience']
        example = ["Based on the sentence excerpt, generate a dialogue between the AI streamer and the viewer. Sentences should not be long. The dialogue should correspond to the style of the passage and the given topic. Keep in mind that an AI streamer is a character with a unique personality that can joke, ask questions, give advice, or share opinions. The viewer can ask questions, joke, express emotions, or keep up a conversation.\nFragment: is celebrated tonsils ripped in half and started speaking directly into her skull like a JBL speaker is she ok Google.\nExample of dialog design:\nviewer:...\nAI:...","Based on the sentence excerpt, generate a dialogue between the AI streamer and the viewer. Sentences should not be long. The dialogue should correspond to the style of the passage and the given topic. Keep in mind that an AI streamer is a character with a unique personality that can joke, ask questions, give advice, or share opinions. The viewer can ask questions, joke, express emotions, or keep up a conversation.\nFragment: I cannot turn off so please be nice I will watch whatever you guys send in you will never in a million years guess what this is an intro for.\nExample of dialog design:\nviewer:...\nAI:..."]

        st = "Based on the sentence excerpt, generate a dialogue between the AI streamer and the viewer. Sentences should not be long. The dialogue should correspond to the style of the passage and the given topic. Keep in mind that an AI streamer is a character with a unique personality that can joke, ask questions, give advice, or share opinions. The viewer can ask questions, joke, express emotions, or keep up a conversation.\nFragment:"
        
        st3 = ".\nExample of dialog design:\nviewer:...\nAI:..."
        step = 0
        for i, sentence in enumerate(sentences, start=1):
            if step < 20:
                step +=1
                print(f"{i}: {sentence}")
                #time.sleep(4000)
                #nom_pred = random.randint(2,5)
                #nom_fr= random.randint(0,3)
                #sentence2 = stroc[nom_fr] +', and briefly (about ' + str(nom_pred) + ' sentences) respond to this message: ' + sentence

                sentence2 = st + " " + sentence + st3

                
                paste_text_at(sentence2,xp1,yp1 )
                '''
                time.sleep(2)
                paste_text_at(sentence, xp2, yp2)
                '''
                pyautogui.moveTo(xp2, yp2, duration=0.5)
                time.sleep(5)
                while on_press_q(xp2, yp2):
                    time.sleep(5)

                time.sleep(1)
                extracted_text1 = get_text_from_screen(x1, y1)
                # проверка на повторы
                '''
                result = compare_strings(extracted_text1, extracted_text1T)
                if nom_text1T < 4 and result == 1:
                    nom_text1T +=1
                elif nom_text1T >= 4:
                    step = 23
                else:
                    nom_text1T = 0
                '''
                if extracted_text1 == sentence2:#проверка для рестарта страницы
                    time.sleep(1)
                    pyautogui.moveTo(x2, y2, duration=0.5)
                    pyautogui.click()
                    time.sleep(30)
                    pyautogui.click()
                    time.sleep(30)
                    step = 23
                else:
                    if extracted_text1T != extracted_text1:
                        extracted_text1T = extracted_text1
                        #print(extracted_text1T)
                        '''
                        time.sleep(2)
                        extracted_text2 = get_text_from_screen(x2, y2)
                        '''
                        # Записываем результат в файл
                         
                        with open('Elli_T2.txt', 'a', encoding='utf-8') as file:
                            file.write( extracted_text1 + '\n\n')
                        '''
                        with open('outCaiT1(2)_text.txt', 'a', encoding='utf-8') as file:
                            file.write(sentence + '\n' + extracted_text2 + '\n')
                        '''
                        time.sleep(1)
            else:
                pyautogui.moveTo(xu1, yu1, duration=0.5)
                pyautogui.click()
                time.sleep(0.2)
                pyautogui.click()
                time.sleep(0.5)
                for pred in example:
                    paste_text_at(pred,xp1,yp1)

                    pyautogui.moveTo(xp2, yp2, duration=0.5)
                    time.sleep(40)
                    while on_press_q(xp2, yp2):
                        time.sleep(5)
                    #time.sleep(40)



                
        time.sleep(60)
        os.system('shutdown -s')#автоматическое отключение системы
keyboard.on_press(on_press_w)
keyboard.on_press(on_press)
keyboard.wait('esc')  # Ждем нажатия клавиши esc для завершения программы


