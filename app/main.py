import json
import os
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional

app = FastAPI(title="FastAPI Docker Compose Watch Demo")

FAKE_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "fake_data.json")
def load_fake_data() -> List[Dict[str, Any]]:
    try:
        with open(FAKE_DATA_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки фейковых данных: {e}")
        return []

@app.get("/")
def read_root():
    return {
        "message": "FastAPI Docker Compose Watch Demo",
        "info": "Измените этот файл, чтобы увидеть автоматическое обновление!",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Этот документ"},
            {"path": "/items", "method": "GET", "description": "Получить все элементы"},
            {"path": "/items/{item_id}", "method": "GET", "description": "Получить элемент по ID"},
            {"path": "/api/info", "method": "GET", "description": "Информация об API"}
        ]
    }

@app.get("/api/info")
def api_info():
    return {
        "name": "FastAPI Docker Compose Watch Demo API",
        "version": "1.0.0",
        "description": "Демо API для показа работы Docker Compose Watch"
    }

@app.get("/items")
def read_items():
    """
    Возвращает все товары из фейковых данных
    """
    return load_fake_data()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    """
    Возвращает товар по ID из фейковых данных
    """
    fake_data = load_fake_data()
    for item in fake_data:
        if item.get("id") == item_id:
            return item
    
    raise HTTPException(status_code=404, detail="Элемент не найден")