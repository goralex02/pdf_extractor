# pdf_extractor

--- 

## Описание файлов

Dockerfile - для развертывания через докер

PDF_JPG_text_extractor.ipynb - для демонстрации, можно удалить

extractor.py - основные функции

main.py - fastapi ручка

requirements.txt - нужные библиотеки

test.py - тестовый скрипт, можно удалить

в тесте используется папка data/, не стал грузить ее на гитхаб ибо там конфиденциальная информация

Передавать нужно путь к файлу. Распознанный текст выплевывается в консоль, а также сохраняется в output.txt

---

## Развертывание через Dockerfile

1. Клонируйте репозиторий

git clone https://github.com/goralex02/pdf_extractor.git

cd text-extractor

2. Соберите Docker-образ

docker build -t text-extractor .

3. Запустите контейнер

docker run -d -p 8000:8000 text-extractor

Приложение будет доступно по адресу: http://localhost:8000
