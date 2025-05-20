FROM python:3.13.0-slim

WORKDIR /backend

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off io buffering
ENV PYTHONUNBUFFERED 1

COPY . .

CMD ["fastapi", "dev", "src/main.py", "--port", "9090", "--host", "0.0.0.0"]
