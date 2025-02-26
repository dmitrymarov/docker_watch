import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional

app = FastAPI(title="FastAPI Docker Compose Watch Demo")

# Добавление CORS для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к файлу с фейковыми данными
FAKE_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "fake_data.json")

# Функция для загрузки фейковых данных
def load_fake_data() -> List[Dict[str, Any]]:
    try:
        with open(FAKE_DATA_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки фейковых данных: {e}")
        return []

# Функция для подключения к БД
def get_db_connection():
    try:
        conn = psycopg2.connect(
            os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/mydb"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

# Инициализация БД (пример для реальной среды)

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Создаем таблицу, если она не существует
                cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price NUMERIC(10, 2)
                )
                """)
                
                # Проверяем, есть ли уже данные
                cur.execute("SELECT COUNT(*) FROM items")
                count = cur.fetchone()["count"]
                
                # Если таблица пуста, добавляем данные из fake_data.json
                if count == 0:
                    fake_data = load_fake_data()
                    for item in fake_data:
                        cur.execute(
                            "INSERT INTO items (name, description, price) VALUES (%s, %s, %s)",
                            (item.get("name"), item.get("description"), item.get("price"))
                        )
                conn.commit()
                print("БД инициализирована успешно")
        except Exception as e:
            print(f"Ошибка инициализации БД: {e}")
        finally:
            conn.close()

# Попробуем инициализировать БД при запуске (закомментируйте для тестов без БД)
try:
    init_db()
except Exception as e:
    print(f"Ошибка при инициализации: {e}")

@app.get("/")
def read_root():
    return {
        "message": "FastAPI Docker Compose Watch Demo",
        "info": "Измените этот файл, чтобы увидеть автоматическое обновление! - Изменил",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Этот документ"},
            {"path": "/items", "method": "GET", "description": "Получить все элементы"},
            {"path": "/items/{item_id}", "method": "GET", "description": "Получить элемент по ID"}
        ]
    }

@app.get("/items")
def read_items():
    """
    Читает элементы из базы данных, если доступно подключение.
    В противном случае возвращает фейковые данные.
    """
    # Пробуем получить данные из БД
    conn = get_db_connection()
    fake_data = load_fake_data()
    items = []
    for item in fake_data:
        items.append(item)
    return list(items)
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM items")
                items = cur.fetchall()
                return list(items)
        except Exception as e:
            print(f"Ошибка чтения из БД: {e}")
        finally:
            conn.close()
    
    # Если БД недоступна или произошла ошибка, используем фейковые данные
    return load_fake_data()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    """
    Читает элемент по ID из базы данных, если доступно подключение.
    В противном случае ищет в фейковых данных.
    """
    # Пробуем получить данные из БД
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
                item = cur.fetchone()
                if item:
                    return item
        except Exception as e:
            print(f"Ошибка чтения из БД: {e}")
        finally:
            conn.close()
    
    # Если БД недоступна или элемент не найден, ищем в фейковых данных
    fake_data = load_fake_data()
    for item in fake_data:
        if item.get("id") == item_id:
            return item
    
    raise HTTPException(status_code=404, detail="Элемент не найден")