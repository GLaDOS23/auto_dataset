import re
import json
from pathlib import Path
from typing import List, Tuple
import PyPDF2
from docx import Document

def parse_page_ranges(page_ranges: str) -> List[Tuple[int, int]]:
    """Парсит строку с диапазонами страниц и возвращает список кортежей (start, end)"""
    if not page_ranges:
        return None
    
    ranges = []
    for part in page_ranges.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            ranges.append((start, end))
        else:
            page = int(part)
            ranges.append((page, page))
    return ranges

def is_page_in_ranges(page_num: int, ranges: List[Tuple[int, int]]) -> bool:
    """Проверяет, находится ли номер страницы в указанных диапазонах"""
    if not ranges:
        return False
    return any(start <= page_num <= end for start, end in ranges)

def extract_text_from_pdf(pdf_path: str, exclude_ranges: List[Tuple[int, int]] = None) -> str:
    """Извлекает текст из PDF файла с возможностью исключения страниц"""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for i, page in enumerate(reader.pages, start=1):
            if not is_page_in_ranges(i, exclude_ranges):
                text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_path: str, exclude_ranges: List[Tuple[int, int]] = None) -> str:
    """Извлекает текст из Word файла (имитация исключения страниц)"""
    doc = Document(docx_path)
    paragraphs = []
    words_per_page = 500  # Примерное количество слов на страницу
    word_count = 0
    current_page = 1
    
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            words = len(paragraph.text.split())
            word_count += words
            
            if not is_page_in_ranges(current_page, exclude_ranges):
                paragraphs.append(paragraph.text)
            
            if word_count >= words_per_page:
                word_count = 0
                current_page += 1
    
    return "\n".join(paragraphs)

def clean_text(text: str) -> str:
    """Очищает текст от номеров страниц, содержания и других ненужных элементов"""
    text = re.sub(r'(?i)(стр|page)\s*\d+', '', text)
    text = re.sub(r'(?i)(header|footer|колонтитул|подвал):?.+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'(\[\d+\]|\(\w+\s\d+\)|\d+\))', '', text)
    return text

def process_single_file(input_file: str, output_dir: str, exclude_pages: str = None):
    """Обрабатывает один файл (PDF или Word) и сохраняет результат в JSONL"""
    input_path = Path(input_file)
    output_dir = Path(output_dir)
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    exclude_ranges = parse_page_ranges(exclude_pages) if exclude_pages else None
    
    try:
        if input_path.suffix.lower() == '.pdf':
            raw_text = extract_text_from_pdf(input_file, exclude_ranges)
        elif input_path.suffix.lower() == '.docx':
            raw_text = extract_text_from_docx(input_file, exclude_ranges)
        else:
            print(f"Неподдерживаемый формат файла: {input_path.suffix}")
            return
        
        clean_content = clean_text(raw_text)
        
        if clean_content:
            output_file = output_dir / f"{input_path.stem}.jsonl"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"text": clean_content}, f, ensure_ascii=False)
                f.write('\n')
            print(f"Файл успешно обработан: {output_file}")
        else:
            print("После обработки файл не содержит текста")
    except Exception as e:
        print(f"Ошибка при обработке файла {input_file}: {e}")

if __name__ == "__main__":
    input_file = input("Введите путь к файлу (PDF или Word): ").strip()
    output_directory = input("Введите папку для сохранения результатов: ").strip() or "processed_output"
    #'1-2,5,10-12'
    exclude_pages = '1-2,120-121'.strip()
    
    process_single_file(input_file, output_directory, exclude_pages if exclude_pages else None)
