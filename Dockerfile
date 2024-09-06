# Use a imagem base do tiangolo
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Define o diretório de trabalho
WORKDIR /app

# Copie o código da aplicação para o contêiner
COPY ./app /app

# Copie o requirements.txt para o contêiner
COPY requirements.txt 

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta padrão
EXPOSE 7000

# Comando para rodar o servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]
