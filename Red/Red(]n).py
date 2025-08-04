
def replace_double_enters(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    # Преобразуем список строк в один текст
    text = ''.join(lines)
    updated_text = text.replace('vedal', '')
    updated_text = updated_text.replace('Vedal', '')
    updated_text = updated_text.replace('Neuro-sama', '')
    updated_text = updated_text.replace('neuro-sama', '')
    updated_text = updated_text.replace('Neurosama', '')
    updated_text = updated_text.replace('neurosama', '')
    updated_text = updated_text.replace('Neuro sama', '')
    updated_text = updated_text.replace('neuro sama', '')
    updated_text = updated_text.replace('Neuro', '')
    updated_text = updated_text.replace('neuro', '')
    updated_text = updated_text.replace('Bot: ', '')
    updated_text = updated_text.replace('User: ', '')

    # Заменяем двойные энтеры на одиночные
    updated_text = updated_text.replace('\n\n', '\n')
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(updated_text)

for i in range(10):
    name = 'output.txt'
    #name = input()
    #name += '.txt'
    input_file = name  
    output_file = 'output_BERT_v0.txt' 

    replace_double_enters(input_file, output_file)
    print("ok")
