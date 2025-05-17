# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем и переходим в рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости Python
# Устанавливаем pip и gunicorn глобально
RUN pip install --upgrade pip && \
    pip install gunicorn

# Копируем зависимости Python
COPY pyproject.toml poetry.lock /app/

# Устанавливаем Poetry и зависимости проекта
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Копируем весь проект
COPY . /app/

# Открываем порт
EXPOSE 7777

CMD ["sh", "-c", "python main/manage.py runserver 0.0.0.0:7777 --noreload --insecure"]