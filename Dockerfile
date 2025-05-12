# Use uma imagem base com Python
FROM python:3.12-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Define variáveis de ambiente para Gunicorn e Flask
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Ajustado para a nova localização do app Flask
ENV FLASK_APP=src.app.main:app
ENV FLASK_ENV=production
# A porta que o Gunicorn vai escutar DENTRO do container
ENV APP_PORT=5000
# Adiciona /app ao PYTHONPATH para que imports como `from src...` funcionem
ENV PYTHONPATH=/app

# Cria um usuário não-root para rodar a aplicação (boa prática)
RUN addgroup --system app && adduser --system --group app

# Copia o arquivo requirements.txt para o WORKDIR (/app)
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o diretório src (que agora contém toda a aplicação) para /app/src
COPY src/ /app/src/

# Copia outros arquivos necessários da raiz para /app (como .env_example)
# Se .env_example foi fornecido pelo usuário, ele estará em /home/ubuntu/upload/.env_example
# Preciso verificar se ele existe e copiá-lo. Assumindo que ele foi copiado para a raiz do projeto v3_corrected.
COPY .env_example /app/

# Garante que o usuário 'app' seja dono dos arquivos da aplicação.
# O diretório /app/src/app/reports/ será criado por src/app/main.py.
# O usuário 'app' precisa de permissão para escrever em /app/src/app/.
RUN chown -R app:app /app
USER app

# Expõe a porta que o Gunicorn estará rodando
EXPOSE ${APP_PORT}

# Comando para rodar a aplicação com Gunicorn (forma de shell para expansão de variável)
# Aponta para o objeto 'app' em 'src/app/main.py'

CMD gunicorn --bind "0.0.0.0:${APP_PORT}" --timeout 800 src.app.main:app

