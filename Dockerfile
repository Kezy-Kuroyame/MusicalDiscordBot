# Stage 1: сборка зависимостей Python
FROM python:3.11-alpine AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: финальный образ
FROM python:3.11-alpine
WORKDIR /app

# Копируем зависимости
COPY --from=builder /install /usr/local
COPY . /app

# Устанавливаем FFmpeg + Opus + dev пакеты
RUN apk add --no-cache ffmpeg opus opus-dev build-base

CMD ["python", "main.py"]
