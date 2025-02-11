FROM python:3.10

WORKDIR /app

COPY requirements.txt .

EXPOSE 8554

# Instala as dependências listadas no arquivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código fonte para o diretório de trabalho
COPY . .

# Define o comando padrão a ser executado quando o container for iniciado
CMD [ "python", "bash" ]
