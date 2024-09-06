FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    gcc \
    libcairo2-dev \
    libopenjp2-7 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod -R 755 /app

COPY app.py .

RUN mkdir -p temp

ENV PORT=7000
ENV HOST=0.0.0.0

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7000"]
