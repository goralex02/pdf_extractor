# Для чтения PDF
import PyPDF2
# Для анализа структуры PDF и извлечения текста
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# Для извлечения текста из таблиц в PDF
import pdfplumber
# Для извлечения изображений из PDF
from PIL import Image
from pdf2image import convert_from_path
# Для выполнения OCR для извлечения текста из изображений
import pytesseract
# Для удаления дополнительных созданных файлов
import os
import sys

# Создание функции для извлечения текста

def text_extraction(element):
    # Извлечение текста из элемента встроенного текста
    line_text = element.get_text()

    # Поиск форматов текста
    # Инициализация списка со всеми форматами, появившимися в строке текста
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            # Итерация по каждому символу в строке текста
            for character in text_line:
                if isinstance(character, LTChar):
                    # Добавление имени шрифта символа
                    line_formats.append(character.fontname)
                    # Добавление размера шрифта символа
                    line_formats.append(character.size)
    # Поиск уникальных размеров шрифтов и названий в строке
    format_per_line = list(set(line_formats))

    # Возврат кортежа с текстом в каждой строке вместе с его форматом
    return (line_text, format_per_line)

# Извлечение таблиц со страницы

def extract_table(pdf_path, page_num, table_num):
    # Открытие PDF файла
    pdf = pdfplumber.open(pdf_path)
    # Поиск рассматриваемой страницы
    table_page = pdf.pages[page_num]
    # Извлечение соответствующей таблицы
    table = table_page.extract_tables()[table_num]

    return table

# Преобразование таблицы в соответствующий формат
def table_converter(table):
    table_string = ''
    # Итерация по каждой строке таблицы
    for row_num in range(len(table)):
        row = table[row_num]
        # Удаление переносов строк из обернутых текстов
        cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
        # Преобразование таблицы в строку
        table_string += ('|' + '|'.join(cleaned_row) + '|' + '\n')
    # Удаление последнего переноса строки
    table_string = table_string[:-1]
    return table_string

# Создание функции для проверки, находится ли элемент в какой-либо таблице на странице
def is_element_inside_any_table(element, page, tables):
    x0, y0up, x1, y1up = element.bbox
    # Изменение координат, так как pdfminer считает от низа к верху страницы
    y0 = page.bbox[3] - y1up
    y1 = page.bbox[3] - y0up
    for table in tables:
        tx0, ty0, tx1, ty1 = table.bbox
        if tx0 <= x0 <= x1 <= tx1 and ty0 <= y0 <= y1 <= ty1:
            return True
    return False

# Функция для поиска таблицы для данного элемента
def find_table_for_element(element, page, tables):
    x0, y0up, x1, y1up = element.bbox
    # Изменение координат, так как pdfminer считает от низа к верху страницы
    y0 = page.bbox[3] - y1up
    y1 = page.bbox[3] - y0up
    for i, table in enumerate(tables):
        tx0, ty0, tx1, ty1 = table.bbox
        if tx0 <= x0 <= x1 <= tx1 and ty0 <= y0 <= y1 <= ty1:
            return i  # Возвращаем индекс таблицы
    return None

# Создание функции для обрезки элементов изображений из PDF
def crop_image(element, pageObj):
    # Получение координат для обрезки изображения из PDF
    [image_left, image_top, image_right, image_bottom] = [element.x0, element.y0, element.x1, element.y1]
    # Обрезка страницы с использованием координат (левый, нижний, правый, верхний)
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # Сохранение обрезанной страницы в новый PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # Сохранение обрезанного PDF в новый файл
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)

# Создание функции для преобразования PDF в изображения
def convert_to_images(input_file):
    images = convert_from_path(input_file)
    image = images[0]
    output_file = 'PDF_image.png'
    image.save(output_file, 'PNG')

def get_file_extension(file_path):
    """Возвращает расширение файла в нижнем регистре."""
    return os.path.splitext(file_path)[1].lower()

def image_to_text(image_path):
    try:
        # Открываем изображение с явным указанием формата
        img = Image.open(image_path)

        # Конвертируем в RGB если нужно
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Явно указываем формат для сохранения
        temp_file = "temp_image.png"
        img.save(temp_file, format='PNG')

        # Переоткрываем сохраненное изображение
        img = Image.open(temp_file)

        text = pytesseract.image_to_string(img, lang='rus+eng')
        os.remove(temp_file)  # Удаляем временный файл
        return text

    except Exception as e:
        print(f"Ошибка обработки изображения: {str(e)}")
        return ""

def extract_text(pdf_path: str):
    """
    Функция для извлечения текста из PDF-файла или изображения (JPG/PNG).
    Возвращает распознанный текст в виде строки.
    """

    # Проверяем расширение файла
    extension = get_file_extension(pdf_path)

        # Обработка изображений
    if extension in ['.jpg', '.jpeg', '.png']:
        return image_to_text(pdf_path)

    # Создать объект файла PDF
    pdfFileObj = open(pdf_path, 'rb')
    # Создать объект для чтения PDF
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)

    # Создать словарь для извлечения текста из каждого изображения
    text_per_page = {}
    # Создать булеву переменную для обнаружения изображений
    image_flag = False

    # Извлекаем страницы из PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        # Инициализируем переменные, необходимые для извлечения текста со страницы
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        line_format = []
        text_from_images = []
        text_from_tables = []
        page_content = []
        # Инициализируем номер рассматриваемых таблиц
        table_in_page = -1
        # Открываем PDF файл
        pdf = pdfplumber.open(pdf_path)
        # Находим рассматриваемую страницу
        page_tables = pdf.pages[pagenum]
        # Находим количество таблиц на странице
        tables = page_tables.find_tables()
        if len(tables) != 0:
            table_in_page = 0

        # Извлечение таблиц со страницы
        for table_num in range(len(tables)):
            # Извлекаем информацию о таблице
            table = extract_table(pdf_path, pagenum, table_num)
            # Преобразуем информацию о таблице в структурированный строковый формат
            table_string = table_converter(table)
            # Добавляем строку таблицы в список
            text_from_tables.append(table_string)

        # Находим все элементы
        page_elements = [(element.y1, element) for element in page._objs]
        # Сортируем все элементы так, как они появляются на странице
        page_elements.sort(key=lambda a: a[0], reverse=True)

        # Находим элементы, которые составляют страницу
        for i, component in enumerate(page_elements):
            # Извлекаем элемент макета страницы
            element = component[1]

            # Проверяем элементы на наличие таблиц
            if table_in_page == -1:
                pass
            else:
                if is_element_inside_any_table(element, page, tables):
                    table_found = find_table_for_element(element, page, tables)
                    if table_found == table_in_page and table_found is not None:
                        page_content.append(text_from_tables[table_in_page])
                        page_text.append('table')
                        line_format.append('table')
                        table_in_page += 1
                    # Пропускаем эту итерацию, так как содержимое этого элемента было извлечено из таблиц
                    continue

            if not is_element_inside_any_table(element, page, tables):
                # Проверяем, является ли элемент текстовым элементом
                if isinstance(element, LTTextContainer):
                    # Используем функцию для извлечения текста и формата для каждого текстового элемента
                    (line_text, format_per_line) = text_extraction(element)
                    # Добавляем текст каждой строки к тексту страницы
                    page_text.append(line_text)
                    # Добавляем формат для каждой строки с текстом
                    line_format.append(format_per_line)
                    page_content.append(line_text)

                # Проверяем элементы на наличие изображений
                if isinstance(element, LTFigure):
                    # Обрезаем изображение из PDF
                    crop_image(element, pageObj)
                    # Конвертируем обрезанный PDF в изображение
                    convert_to_images('cropped_image.pdf')
                    # Извлекаем текст из изображения
                    image_text = image_to_text('PDF_image.png')
                    text_from_images.append(image_text)
                    page_content.append(image_text)
                    # Добавляем заполнитель в списки текста и формата
                    page_text.append('image')
                    line_format.append('image')
                    # Обновляем флаг для обнаружения изображений
                    image_flag = True

        # Создаем ключ словаря
        dctkey = 'Page_' + str(pagenum)
        # Добавляем список списков в качестве значения по ключу страницы
        text_per_page[dctkey] = [page_text, line_format, text_from_images, text_from_tables, page_content]

    # Закроем объект пдф
    pdfFileObj.close()

    # Удаляем дополнительные файлы, созданные при обнаружении изображения
    if image_flag:
        os.remove('cropped_image.pdf')
        os.remove('PDF_image.png')

    # Объединяем текст со всех страниц
    result = ''
    for page_key in text_per_page:
        result += ''.join(text_per_page[page_key][4])

    return result

# Путь к файлу (PDF, JPG или PNG)
#file_path = './data/Анализ кровь_page-0001.jpg'

# Извлечение текста
#extracted_text = extract_text(file_path)

# Сохранение текста в файл .txt
#with open('output.txt', 'w', encoding='utf-8') as f:
#    f.write(extracted_text)

#print("Текст успешно извлечен и сохранен в output.txt")

"""next  is used debug-only"""

def extract_main():
    # Проверяем, что передан хотя бы один аргумент (путь к файлу)
    if len(sys.argv) != 2:
        print("Использование: python extract.py <путь_к_файлу>")
        sys.exit(1)

    # Получаем путь к файлу из аргументов командной строки
    file_path = sys.argv[1]

    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        sys.exit(1)

    # Извлекаем текст из файла
    try:
        extracted_text = extract_text(file_path)
        print("Текст успешно извлечен.")

        # Сохраняем текст в файл output.txt
        output_file = 'output.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f"Текст сохранен в файл: {output_file}")

    except Exception as e:
        print(f"Произошла ошибка при извлечении текста: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    extract_main()

