FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY etl etl
COPY analysis analysis
COPY dashboard dashboard
COPY scripts scripts

RUN chmod +x scripts/entrypoint.sh
