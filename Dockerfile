FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# UID/GID do usuário do host
ARG UID=1000
ARG GID=1000

# Dependências necessárias para mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Cria usuário com o mesmo UID/GID do host
RUN groupadd --gid ${GID} appuser \
    && useradd \
       --uid ${UID} \
       --gid ${GID} \
       --create-home \
       appuser

# Copia o projeto
COPY --chown=appuser:appuser . .

USER appuser

CMD ["flask", "--app", "api", "run", "--host=0.0.0.0", "--port=5000", "--debug"]