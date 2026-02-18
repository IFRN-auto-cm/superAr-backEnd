FROM python:3.12-slim

# Evita .pyc e deixa logs mais “diretos”
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências necessárias para compilar mysqlclient (Flask-MySQLdb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# Dependências de runtime (geralmente não precisa de build tools aqui)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .

# Opcional: rodar como usuário não-root
RUN useradd -m appuser
USER appuser

CMD ["flask", "--app", "api", "run", "--host=0.0.0.0", "--port=5000", "--debug"]