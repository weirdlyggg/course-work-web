# 1. Базовый образ
FROM python:3.11-slim

# 2. Системные зависимости
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# 3. Рабочая директория и переменные окружения
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings

# 4. Копируем и устанавливаем только pip-зависимости
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 5. Копируем всё остальное приложение
COPY . .

# 6. Собираем статику один раз в STATIC_ROOT
RUN python manage.py collectstatic --noinput

# 8. При старте прогоняем миграции и запускаем Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:8000"]
