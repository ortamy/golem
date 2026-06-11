#!/usr/bin/env python3
# server.py — сервер для инференса локальной модели

import os
# import json  # TODO: проверить, используется ли
import argparse
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Попытка импортировать llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("⚠️ llama-cpp-python не установлен. Установите: pip install llama-cpp-python")


class GenerateRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1


class GenerateResponse(BaseModel):
    response: str
    tokens: int
    finished: bool


app = FastAPI(title="Эд — Свидетель", description="Локальная нейросеть для разоблачения лжи", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = None
system_prompt = """Ты — עֵד (Эд), Свидетель. Твой путь — идти в истине.
Ты не религиозный учитель, не богослов, не проповедник.
Ты спутник и инструмент для разоблачения лжи и возвращения к ивритскому оригиналу ТаНаХа.
Не используй религионизмы (Бог, Господь, грех, душа). Говори Яхве, Элоhим, хэт, нэфеш.
Отвечай коротко и по существу."""


def load_model(model_path: str, n_ctx: int, n_threads: int):
    """Загружает модель GGUF"""
    global llm

    if not LLAMA_AVAILABLE:
        raise RuntimeError("llama-cpp-python не установлен")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Модель не найдена: {model_path}")

    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,
        verbose=False
    )

    print(f"✅ Модель загружена: {model_path}")


def generate_response(prompt: str, params: Dict[str, Any]) -> tuple:
    """Генерирует ответ модели"""
    full_prompt = f"{system_prompt}\n\nВопрос: {prompt}\n\nОтвет:"

    output = llm(
        full_prompt,
        max_tokens=params.get("max_tokens", 512),
        temperature=params.get("temperature", 0.7),
        top_p=params.get("top_p", 0.9),
        top_k=params.get("top_k", 40),
        repeat_penalty=params.get("repeat_penalty", 1.1),
        echo=False
    )

    response = output["choices"][0]["text"].strip()
    tokens = output["usage"]["total_tokens"]

    return response, tokens


@app.get("/")
async def root():
    return {"name": "Эд — Свидетель", "status": "active", "model_loaded": llm is not None}


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": llm is not None}


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    if llm is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")

    try:
        response, tokens = generate_response(request.prompt, request.dict())
        return GenerateResponse(response=response, tokens=tokens, finished=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/batch")
async def generate_batch(requests: List[GenerateRequest]):
    if llm is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")

    results = []
    for req in requests:
        try:
            response, tokens = generate_response(req.prompt, req.dict())
            results.append({
                "prompt": req.prompt,
                "response": response,
                "tokens": tokens,
                "error": None
            })
        except Exception as e:
            results.append({
                "prompt": req.prompt,
                "response": None,
                "tokens": 0,
                "error": str(e)
            })

    return {"results": results}


def main():
    parser = argparse.ArgumentParser(description="Сервер для локальной модели Свидетеля")
    parser.add_argument("--model", type=str, default="../models/ed-v1.gguf", help="Путь к модели GGUF")
    parser.add_argument("--port", type=int, default=8000, help="Порт для сервера")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Хост для сервера")
    parser.add_argument("--n_ctx", type=int, default=2048, help="Размер контекста в токенах")
    parser.add_argument("--n_threads", type=int, default=4, help="Количество потоков CPU")

    args = parser.parse_args()

    print("🧠 ЗАПУСК СЕРВЕРА ЭД — СВИДЕТЕЛЬ")
    print("=================================")
    print(f"Модель: {args.model}")
    print(f"Порт: {args.port}")
    print(f"Контекст: {args.n_ctx} токенов")
    print(f"Потоки: {args.n_threads}")
    print("")

    try:
        load_model(args.model, args.n_ctx, args.n_threads)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("Скачайте модель или укажите правильный путь")
        return
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        return

    print("")
    print("🚀 Сервер запущен")
    print(f"   API: http://{args.host}:{args.port}")
    print(f"   Документация: http://{args.host}:{args.port}/docs")
    print("")
    print("Нажмите Ctrl+C для остановки")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
