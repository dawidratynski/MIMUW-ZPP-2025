FROM python:3.13.3-slim

WORKDIR /backend

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --no-cache-dir uv

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off io buffering
ENV PYTHONUNBUFFERED 1

ENV UV_HTTP_TIMEOUT=1200

COPY requirements.txt .
RUN uv pip install -r requirements.txt --system --no-cache

COPY . .

CMD ["fastapi", "dev", "src/main.py", "--port", "9090", "--host", "0.0.0.0"]
