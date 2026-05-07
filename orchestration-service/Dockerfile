FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости и Docker CLI
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ca-certificates \
    && curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.3.1.tgz -o docker.tgz \
    && tar -xzf docker.tgz \
    && mv docker/docker /usr/local/bin/ \
    && rm -rf docker docker.tgz \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/

# Создаем пользователя и добавляем его в группу docker (группа создается с GID 999)
RUN useradd -m -u 1000 appuser && \
    groupadd -g 999 docker && \
    usermod -aG docker appuser

USER appuser

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
