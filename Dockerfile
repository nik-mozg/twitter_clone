# Используем официальный Python-образ как базовый
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем всю структуру проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем дополнительные зависимости для работы с PostgreSQL
RUN apt-get update && apt-get install -y build-essential libpq-dev netcat-openbsd

# Выполняем populate_db.py, если он существует
CMD ["/bin/bash", "-c", "python3 /app/populate_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
