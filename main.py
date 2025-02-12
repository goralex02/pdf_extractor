from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from extractor import extract_text  # Импортируйте вашу функцию

app = FastAPI()

# Временная папка для загруженных файлов
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
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
        return JSONResponse(status_code=500, content={"error": str(e)})