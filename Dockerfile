FROM python:3.12-slim

WORKDIR /app

# Устанавливаем git для GitPython и curl для smoke test
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
COPY pyproject.toml .
COPY src/ ./src/
COPY templates/ ./templates/
RUN pip install --no-cache-dir -e .

# Устанавливаем AI зависимости (для GitHub Models)
RUN pip install --no-cache-dir openai

# Копируем entrypoint скрипт
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Точка входа с аргументом по умолчанию
ENTRYPOINT ["/entrypoint.sh"]
CMD ["serve"]
