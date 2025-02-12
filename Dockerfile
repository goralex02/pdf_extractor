FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Копирование кода
WORKDIR /app
COPY . .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]