from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling
# Загрузка настроенной модели и токенизатора
from transformers import pipeline
from googletrans import Translator, constants
import re
import pyautogui
import pyperclip
import time

# Создаем объект Translator
translator = Translator()

model = GPT2LMHeadModel.from_pretrained('D:/Новое/Модели/Текст/Blocks_V0/Диалоги/Старые/TestTAI_1_Data')
tokenizer = GPT2Tokenizer.from_pretrained('D:/Новое/Модели/Текст/Тест1/TestTAI_M/TestTAI_1_Tok_M')
# Создание пайплайна для генерации текста
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)#fine_tuned_







# Генерация текста
def gen (input_text):
    #input_text  = input()
    
    

    output = generator( input_text, max_new_tokens=30, num_return_sequences=1,temperature=0.5)
    generated_text2 =output[0]['generated_text'].replace(input_text,'')
    #generated_text2 = translator.translate(generated_text2 , dest='ru')

    #print(generated_text2)#полный текст
    #обрезать до .
    generated_text_stop =generated_text2.find('.')# generated_text2.text.find('.')
    text = generated_text2[0:generated_text_stop + 1]
    if len(text) <2:
        return generated_text2 
    else:
        return text 





def get_text_from_screen():
    x2 = 624
    y2 = 861    
    pyautogui.moveTo(x2, y2, duration=0.5)
        
    # Эмулируем нажатие левой клавиши мыши
    pyautogui.doubleClick()
    pyautogui.click()
    time.sleep(0.2)  
    pyautogui.hotkey('ctrl', 'c')
    # Извлечение текста из буфера обмена
    copied_text = pyperclip.paste()
    return copied_text

#редактор строки
def process_string(input_text):
    # Удаляем все английские символы (латинские буквы)
    text_without_english = re.sub(r'[A-Za-z]', '', input_text)
    text_without_english = text_without_english.replace('~','')
    print("CAI: ", text_without_english)
    # Инициализируем переводчик
    translator = Translator()
    
    # Переводим текст с русского на английский
    translated_text = translator.translate(text_without_english, src='ru', dest='en').text
    #print(translated_text)
    
    return translated_text


#вставить текст
def paste_text_at(text):

    x1 = 23
    y1 = 1011
    x2 = 705
    y2 = 968
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




    text_p = ''
    while True:
        try:
            # Получение текста из указанной области экрана
            extracted_text = get_text_from_screen()
                
            txt = process_string(extracted_text)

            outxt = gen(txt)
            if outxt != text_p:
                generated_text = translator.translate(outxt, dest='ru').text
                print('Tai: ', generated_text)
                paste_text_at(generated_text)
                # Записываем результат в файл
                with open('out_text.txt', 'a', encoding='utf-8') as file:
                    file.write(txt + '\n' + outxt + '\n')
                text_p = outxt
                time.sleep(20)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            time.sleep(10)


