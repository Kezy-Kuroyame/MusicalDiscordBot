# Stage 1: сборка зависимостей Python
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: финальный образ
FROM python:3.11-slim
WORKDIR /app

# Копируем зависимости
COPY --from=builder /install /usr/local
COPY . /app

# Устанавливаем FFmpeg + Opus + dev пакеты
RUN apt-get update && apt-get install -y ffmpeg libopus-dev build-essential && rm -rf /var/lib/apt/lists/*

CMD ["python", "main.py"]
