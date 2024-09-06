FROM python:3.10-slim

RUN apt-get update && apt-get install -y gcc libcairo2-dev libopenjp2-7 libtiff5

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app /app

EXPOSE 7000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]
