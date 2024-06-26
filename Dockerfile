FROM python:alpine
WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY init ./init
COPY src ./src

RUN pip install -r requirements.txt --break-system-packages
