# Docker Compose Watch - Пример для начинающих

Этот проект демонстрирует использование функциональности `docker compose watch` для удобной разработки с автоматической синхронизацией кода и перезапуском контейнеров.

## Что такое Docker Compose Watch?

`docker compose watch` - это функция Docker Compose, которая упрощает процесс разработки, позволяя:
- Автоматически синхронизировать файлы между локальной машиной и контейнерами
- Перезапускать сервисы при изменении файлов
- Пересобирать контейнеры при изменении критических файлов (например, Dockerfile или зависимостей)

## Предварительные требования

- Docker Engine версии 23.0 или выше
- Docker Compose версии 2.22.0 или выше
- Права доступа к Docker socket (для функций управления контейнерами)

Для проверки версий выполните:
```bash
docker --version
docker compose version
```

### Настройка прав доступа к Docker socket

Для корректной работы API управления контейнерами, необходимо предоставить доступ к Docker socket:

1. В Linux убедитесь, что ваш пользователь входит в группу docker:
   ```bash
   sudo usermod -aG docker $USER
   # Перезайдите в систему или выполните
   newgrp docker
   ```

2. В Docker Compose мы уже настроили монтирование Docker socket:
   ```yaml
   volumes:
     - /var/run/docker.sock:/var/run/docker.sock
   ```

## Структура проекта

```
.
├── docker-compose.yml      # Основной файл Docker Compose с настройками watch
├── app/                    # Папка с FastAPI приложением
│   ├── Dockerfile          # Dockerfile для сборки приложения
│   ├── requirements.txt    # Зависимости Python
│   ├── main.py             # Код FastAPI приложения
│   └── data/               # Фейковые данные
│       └── fake_data.json
└── nginx/                  # Папка с настройками Nginx
    ├── Dockerfile          # Dockerfile для Nginx
    ├── nginx.conf          # Основной конфиг Nginx
    └── templates/          # Шаблоны конфигурации Nginx
        └── default.conf.template
```

## Начало работы

### Шаг 1: Клонирование репозитория

```bash
git clone <ссылка-на-репозиторий>
cd docker-compose-watch-sample
```

### Шаг 2: Запуск с Docker Compose Watch

```bash
docker compose watch
```

При первом запуске Docker соберет образы и запустит контейнеры. Затем включится режим отслеживания изменений.

## Что происходит после запуска

После запуска `docker compose watch`:

1. Docker создаст и запустит два контейнера:
   - `app` - FastAPI приложение
   - `nginx` - веб-сервер для проксирования запросов к приложению

2. Docker начнет отслеживать изменения в файлах и действовать в соответствии с настройками в `docker-compose.yml`:

   - Если вы измените код в папке `app/`, изменения будут автоматически синхронизированы с контейнером
   - Если вы измените `app/requirements.txt` или `app/Dockerfile`, контейнер будет пересобран
   - Если вы измените конфигурацию Nginx в папке `nginx/templates/`, файлы будут синхронизированы и Nginx будет перезапущен

## Доступ к приложению

После запуска ваше приложение будет доступно по следующим адресам:

- Напрямую через FastAPI: [http://localhost:8000](http://localhost:8000)
- Через Nginx: [http://localhost](http://localhost)
- API через Nginx: [http://localhost/api](http://localhost/api)

## API для управления Docker контейнерами

Приложение предоставляет API для мониторинга и управления Docker контейнерами:

### Получение списка всех контейнеров

```
GET /containers
```

Пример ответа:
```json
{
  "containers": [
    {
      "id": "1a2b3c4d5e6f",
      "name": "docker-compose-watch-sample_app_1",
      "image": "docker-compose-watch-sample_app:latest",
      "status": "running",
      "state": "running",
      "created": "2023-01-01T12:00:00Z",
      "ports": [
        {
          "container_port": "8000/tcp",
          "host_ip": "0.0.0.0",
          "host_port": "8000"
        }
      ],
      "networks": ["docker-compose-watch-sample_default"]
    }
  ],
  "count": 1
}
```

### Получение информации о конкретном контейнере

```
GET /containers/{container_id}
```

### Управление контейнером

```
POST /containers/{container_id}/{action}
```

Доступные действия:
- `start` - запуск контейнера
- `stop` - остановка контейнера
- `restart` - перезапуск контейнера

## Тестирование функциональности Watch

### Тест 1: Синхронизация кода приложения

1. Откройте файл `app/main.py`
2. Измените сообщение в функции `read_root`, например:
   ```python
   @app.get("/")
   def read_root():
       return {"message": "Hello from Docker Compose Watch!"}
   ```
3. Сохраните файл
4. Обновите страницу в браузере - изменения применятся автоматически!

### Тест 2: Добавление зависимостей (ребилд)

1. Откройте файл `app/requirements.txt`
2. Добавьте новую зависимость, например:
   ```
   pydantic==2.5.2
   ```
3. Сохраните файл
4. Docker автоматически пересоберет контейнер с приложением

### Тест 3: Изменение конфигурации Nginx

1. Откройте файл `nginx/templates/default.conf.template`
2. Добавьте новую конфигурацию, например новый location:
   ```nginx
   location /health {
       proxy_pass http://app:8000/healthcheck;
   }
   ```
3. Сохраните файл
4. Nginx автоматически перезагрузит конфигурацию

## Остановка контейнеров

Для остановки работы нажмите `Ctrl+C` в терминале, где запущен `docker compose watch`.

## Как работает Docker Compose Watch

В нашем файле `docker-compose.yml` мы используем секцию `develop.watch` для настройки отслеживания:

```yaml
develop:
  watch:
    - action: sync              # Просто синхронизация файлов
      path: ./app               # Локальный путь для отслеживания
      target: /app              # Путь в контейнере
    - action: rebuild           # Пересборка контейнера
      path: ./app/requirements.txt
    - action: sync+restart      # Синхронизация + перезапуск сервиса
      path: ./nginx/templates
      target: /etc/nginx/templates
```

### Типы действий (action)

1. `sync` - синхронизирует измененные файлы без перезапуска сервиса
2. `rebuild` - пересобирает контейнер при изменении файла
3. `sync+restart` - синхронизирует файлы и перезапускает сервис

## Советы и трюки

- Используйте `ignore` для исключения файлов из синхронизации
- Добавляйте `restart: unless-stopped` для сервисов, которые должны автоматически перезапускаться после ребилда
- Используйте `--no-attach` для запуска в фоновом режиме:
  ```bash
  docker compose watch --no-attach
  ```

## Решение проблем

### Контейнеры не обновляются

- Убедитесь, что пути в `path` и `target` указаны правильно
- Проверьте права доступа к файлам и папкам

### Приложение не видит изменения

- Возможно, ваше приложение требует перезапуска. Добавьте `action: sync+restart` вместо простого `sync`
- Для Python приложений используйте режим отладки или hot-reload (как настроено в нашем примере)

### API контейнеров возвращает ошибку доступа

- Убедитесь, что Docker socket правильно монтируется в контейнер
- Проверьте права доступа к `/var/run/docker.sock`
- На Linux выполните: `sudo chmod 666 /var/run/docker.sock` (временное решение)
- Для постоянного решения добавьте пользователя в группу docker: `sudo usermod -aG docker $USER`

## Дополнительные ресурсы

- [Официальная документация Docker Compose Watch](https://docs.docker.com/compose/file-watch/)
- [Документация FastAPI](https://fastapi.tiangolo.com/)
- [Документация Nginx](https://nginx.org/en/docs/)
