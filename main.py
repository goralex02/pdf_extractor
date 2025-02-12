from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from extractor import extract_text  # Импортируйте вашу функцию
import logging

app = FastAPI()

# Временная папка для загруженных файлов
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)

@app.post("/extract-text/")
async def extract_text_endpoint(file: UploadFile = File(...)):
    logging.info(f"Received file: {file.filename}")
    try:
        # Сохраняем загруженный файл
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Извлекаем текст
        extracted_text = extract_text(file_path)

        # Удаляем временный файл
        os.remove(file_path)
        return JSONResponse(content={"text": extracted_text})
    except Exception as e:
        logging.error(f"Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})