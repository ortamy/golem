"""
server.py — Локальный API сервер для SmolVLM-256M

Запуск:
    pip install fastapi uvicorn pillow transformers torch
    python server.py

Эндпоинт:
    POST /describe
    {
        "image": "data:image/png;base64,...",
        "prompt": "Опиши изображение"
    }
    Response: { "description": "..." }
"""

import os
import sys
import base64
import io
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Golem Vision API",
    description="Локальный API для визуального анализа изображений через SmolVLM-256M",
    version="1.0.0"
)

# CORS для доступа из браузера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== МОДЕЛЬ ДАННЫХ =====
class DescribeRequest(BaseModel):
    image: str  # base64 data URL
    prompt: Optional[str] = "Опиши подробно, что изображено на этой картинке."

class DescribeResponse(BaseModel):
    description: str
    model: str = "SmolVLM-256M-Instruct"

# ===== ГЛОБАЛЬНАЯ ПЕРЕМЕННАЯ ДЛЯ МОДЕЛИ =====
_model = None
_processor = None
_device = None

def load_model():
    """Загружает модель SmolVLM-256M"""
    global _model, _processor, _device

    if _model is not None:
        return True

    try:
        import torch
        from transformers import AutoProcessor, AutoModelForVision2Seq

        logger.info("Загрузка модели SmolVLM-256M-Instruct...")

        model_id = "HuggingFaceTB/SmolVLM-256M-Instruct"

        _device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Используется устройство: {_device}")

        _processor = AutoProcessor.from_pretrained(model_id)
        _model = AutoModelForVision2Seq.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if _device == "cuda" else torch.float32,
            device_map="auto" if _device == "cuda" else None,
            low_cpu_mem_usage=True
        )

        if _device == "cpu":
            _model = _model.to(_device)

        logger.info("Модель успешно загружена")
        return True

    except ImportError as e:
        logger.error(f"Ошибка импорта: {e}")
        logger.error("Установите зависимости: pip install transformers torch pillow")
        return False
    except Exception as e:
        logger.error(f"Ошибка загрузки модели: {e}")
        return False


def process_image(base64_data: str, prompt: str) -> str:
    """Обрабатывает изображение через модель"""
    global _model, _processor, _device

    try:
        # Извлекаем base64 данные
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        # Декодируем изображение
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Форматируем промпт для модели
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]
            }
        ]

        # Подготавливаем входные данные
        prompt_text = _processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = _processor(
            images=image,
            text=prompt_text,
            return_tensors="pt"
        ).to(_device)

        # Генерируем ответ
        generated_ids = _model.generate(
            **inputs,
            max_new_tokens=500,
            temperature=0.2,
            top_p=0.95,
            do_sample=True
        )

        # Декодируем ответ
        generated_text = _processor.decode(
            generated_ids[0],
            skip_special_tokens=True
        )

        # Извлекаем только ответ модели (после последнего пользовательского сообщения)
        if "Assistant:" in generated_text:
            generated_text = generated_text.split("Assistant:")[-1].strip()
        elif "assistant" in generated_text.lower():
            parts = generated_text.lower().split("assistant")
            if len(parts) > 1:
                generated_text = parts[-1].strip()

        return generated_text

    except Exception as e:
        logger.error(f"Ошибка обработки изображения: {e}")
        raise


# ===== ЭНДПОИНТЫ =====

@app.get("/")
def root():
    return {
        "service": "Golem Vision API",
        "model": "SmolVLM-256M-Instruct",
        "status": "loaded" if _model is not None else "not_loaded",
        "endpoints": {
            "POST /describe": "Анализ изображения"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": _model is not None
    }


@app.post("/describe", response_model=DescribeResponse)
async def describe(request: DescribeRequest):
    """Анализирует изображение и возвращает текстовое описание"""

    if _model is None:
        loaded = load_model()
        if not loaded:
            raise HTTPException(
                status_code=503,
                detail="Модель не загружена. Убедитесь, что установлены зависимости: transformers, torch, pillow"
            )

    try:
        description = process_image(request.image, request.prompt)
        return DescribeResponse(description=description)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка анализа: {str(e)}"
        )


# ===== ТОЧКА ВХОДА =====
if __name__ == "__main__":
    import uvicorn

    # Пробуем загрузить модель при старте
    logger.info("Попытка предварительной загрузки модели...")
    load_model()

    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Запуск сервера на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)