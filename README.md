# Docker Compose Watch - Руководство для разработчиков

Этот проект демонстрирует возможности `docker compose watch` для более удобной разработки с автоматической синхронизацией изменений, позволяя сосредоточиться на создании кода, а не на ручном перезапуске контейнеров.

## Что такое Docker Compose Watch?

`docker compose watch` - это функция Docker Compose, которая позволяет автоматически:
- Синхронизировать изменения файлов между локальной машиной и контейнерами
- Перезапускать сервисы при необходимости
- Пересобирать контейнеры при важных изменениях (например, в зависимостях)

**Основное преимущество:** вам не нужно вручную перезапускать или пересобирать контейнеры при внесении изменений в код!

## Предварительные требования

- Docker Engine версии 23.0 или выше
- Docker Compose версии 2.22.0 или выше

Проверьте ваши версии:
```bash
docker --version
docker compose version
```

## Структура проекта

```
.
├── docker-compose.yml      # Конфигурация Docker Compose с настройками watch
├── app/                    # FastAPI приложение
│   ├── Dockerfile          # Сборка приложения
│   ├── requirements.txt    # Зависимости Python
│   ├── main.py             # Код FastAPI
│   └── data/               # Данные приложения
│       └── fake_data.json
└── nginx/                  # Nginx для проксирования
    ├── Dockerfile          # Сборка Nginx
    └── nginx.conf          # Конфигурация Nginx
```

## Быстрый старт

### Шаг 1: Клонирование репозитория

```bash
git clone <ссылка-на-репозиторий>
cd docker-compose-watch-demo
```

### Шаг 2: Запуск с Docker Compose Watch

```bash
docker compose watch
```

При первом запуске Docker соберет образы и запустит контейнеры, затем начнет отслеживать изменения в режиме реального времени.

## Как работает Docker Compose Watch?

В файле `docker-compose.yml` мы используем секцию `develop.watch`, где указываем, что нужно делать при изменениях файлов:

```yaml
develop:
  watch:
    # Пример для app сервиса
    - action: sync             # Только синхронизация файлов
      path: ./app              # Локальный путь
      target: /app             # Путь в контейнере
      
    - action: rebuild          # Пересборка контейнера
      path: ./app/requirements.txt
      
    # Пример для nginx сервиса  
    - action: sync+restart     # Синхронизация + перезапуск
      path: ./nginx/nginx.conf
      target: /etc/nginx/conf.d/default.conf
```

### Доступные действия (action)

1. `sync` - синхронизирует изменённые файлы без перезапуска (идеально для кода с hot-reload)
2. `rebuild` - пересобирает контейнер при изменении важных файлов (Dockerfile, зависимости)
3. `sync+restart` - синхронизирует файлы и перезапускает сервис (для конфигураций)

## Доступ к приложению

После запуска ваше приложение будет доступно:
- **FastAPI напрямую:** [http://localhost:8000](http://localhost:8000)
- **Через Nginx:** [http://localhost:8070](http://localhost:8070)

Запросы проксируются следующим образом:
- **Основной API:** [http://localhost:8070/api](http://localhost:8070/api)
- **Документация API:** [http://localhost:8070/docs](http://localhost:8070/docs)
- **WebSocket (если используется):** [http://localhost:8070/ws](http://localhost:8070/ws)
- **Статические файлы:** [http://localhost:8070/static](http://localhost:8070/static)

## Тестирование функциональности Watch

### Тест 1: Изменение кода приложения (sync)

1. Откройте `app/main.py`
2. Измените текст в функции `read_root()`, например:
   ```python
   def read_root():
       return {
           "message": "Привет из Docker Compose Watch!",
           # другие поля...
       }
   ```
3. Сохраните файл
4. Обновите страницу в браузере - изменения применятся автоматически!

### Тест 2: Изменение зависимостей (rebuild)

1. Откройте `app/requirements.txt`
2. Добавьте новую зависимость, например:
   ```
   python-dotenv==1.0.0
   ```
3. Сохраните файл
4. Docker автоматически пересоберет контейнер с приложением

### Тест 3: Изменение конфигурации Nginx (sync+restart)

1. Откройте `nginx/nginx.conf`
2. Измените или добавьте комментарий в конце файла:
   ```nginx
   # Docker Compose Watch - это очень удобно!
   ```
3. Сохраните файл
4. Nginx автоматически перезагрузит конфигурацию

## Как работают различные типы синхронизации?

### 1. `sync` (для кода приложения)
- **Что происходит:** Измененные файлы копируются в контейнер без его перезапуска
- **Когда использовать:** Для кода с поддержкой hot-reload (как в нашем FastAPI приложении)
- **Пример в проекте:** Изменения в `app/main.py`

### 2. `rebuild` (для системных изменений)
- **Что происходит:** Контейнер полностью пересобирается заново
- **Когда использовать:** При изменении зависимостей, Dockerfile или других критичных файлов
- **Пример в проекте:** Изменения в `app/requirements.txt`

### 3. `sync+restart` (для конфигураций)
- **Что происходит:** Файлы синхронизируются, а затем сервис перезапускается
- **Когда использовать:** Для конфигурационных файлов, требующих перезапуска сервиса
- **Пример в проекте:** Изменения в `nginx/nginx.conf`

## Полезные советы

### Игнорирование файлов при синхронизации
```yaml
- action: sync
  path: ./app
  target: /app
  ignore:
    - "__pycache__"  # Игнорируем кэш Python
    - "*.pyc"        # Игнорируем скомпилированные файлы
    - "*.log"        # Игнорируем логи
```

### Запуск в фоновом режиме
```bash
docker compose watch --no-attach
```

### Остановка watch
Нажмите `Ctrl+C` в терминале, где запущен `docker compose watch`

## Решение проблем

### Изменения не применяются
- Проверьте пути в `path` и `target` - они должны быть указаны правильно
- Убедитесь, что у файлов правильные права доступа
- Проверьте логи контейнера: `docker logs fastapi_app`

### Для Python-приложения изменения не видны
- Убедитесь, что оно запущено с флагом `--reload` (для uvicorn)
- Это уже настроено в нашем Dockerfile: `CMD ["uvicorn", "main:app", "--reload"]`

## Дополнительные ресурсы

- [Официальная документация Docker Compose Watch](https://docs.docker.com/compose/file-watch/)
- [Документация FastAPI](https://fastapi.tiangolo.com/)
- [Документация Nginx](https://nginx.org/en/docs/)
