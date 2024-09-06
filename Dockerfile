FROM python:3.10-slim

# Atualize os repositórios e instale dependências do sistema necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    gcc \
    libcairo2-dev \
    libopenjp2-7 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie o arquivo requirements.txt e instale as dependências Python
COPY requirements.txt ./
COPY app.py ./

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod -R 755 /app

EXPOSE 7000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "7000"]
