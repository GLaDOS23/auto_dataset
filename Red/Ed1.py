import glob

# Путь к директории, где лежат txt файлы
directory_path = 'D:/Новое/Бд/Текст/veritasium'

# Путь к выходному файлу, куда будем записывать объединенный результат
output_file = 'D:/Новое/Бд/Текст/Compil_veritasium.txt'

# Список всех файлов в директории, которые заканчиваются на .txt
txt_files = glob.glob(directory_path + '/*.txt')

# Открываем выходной файл в режиме добавления (append)
with open(output_file, 'w') as outfile:
    for txt_file in txt_files:
        with open(txt_file, 'r') as infile:
            # Читаем содержимое текущего txt файла
            content = infile.read()
            # Записываем содержимое в выходной файл
            outfile.write(content)
            # Добавляем разделитель между содержимым файлов
            outfile.write('\n')  # Можно использовать любой другой разделитель

#print(f'Все файлы объединены в {output_file}')
