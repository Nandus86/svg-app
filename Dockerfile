# Use a imagem base do Python
FROM python:3.11-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Atualize o pip e instale as dependências
RUN pip install --upgrade pip

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação para o diretório de trabalho
COPY . .

# Defina a variável de ambiente para o FastAPI
ENV UVICORN_CMD="uvicorn app:app --host 0.0.0.0 --port 7000"

# Exponha a porta em que a aplicação será executada
EXPOSE 7000

# Comando para executar a aplicação FastAPI
CMD ["sh", "-c", "$UVICORN_CMD"]
