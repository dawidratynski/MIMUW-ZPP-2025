FROM python:3.13.0-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off io buffering
ENV PYTHONUNBUFFERED 1

COPY . .

CMD ["fastapi", "dev", "app/main.py", "--port", "9090", "--host", "0.0.0.0"]
