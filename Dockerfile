FROM python:3.12-slim

WORKDIR /app

# Устанавливаем git для GitPython и curl для smoke test
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем весь проект сначала
COPY pyproject.toml .
COPY src/ ./src/
COPY templates/ ./templates/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -e .

# Копируем entrypoint скрипт
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Точка входа с аргументом по умолчанию
ENTRYPOINT ["/entrypoint.sh"]
CMD ["serve"]
