FROM python:3.12-slim

WORKDIR /app

# Устанавливаем git для GitPython
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY src/ ./src/
COPY templates/ ./templates/

EXPOSE 8000

CMD ["git-changelog-mcp"]
