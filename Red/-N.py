def replace_multiple_newlines(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Заменяем несколько \n на один
    cleaned_content = '\n'.join([line for line in content.splitlines() if line.strip() != ''])
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

# Путь к исходному текстовому файлу
input_file_path = 'Noita_outHAG1_text_T.txt'
# Путь к выходному текстовому файлу
output_file_path = 'Noita_outHAG1_text_T-N.txt'

replace_multiple_newlines(input_file_path, output_file_path)
