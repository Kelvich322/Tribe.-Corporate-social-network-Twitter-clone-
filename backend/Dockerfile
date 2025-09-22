# Образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы с зависимостями
COPY pyproject.toml poetry.lock* ./

# Устанавливаем системные зависимости и потом чистим кэш пакетов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем pipx и poetry
RUN pip install --no-cache-dir pipx && \
    pipx install poetry

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:${PATH}"

# Настраиваем Poetry, чтоб он не создавал отдельную вирт.среду в контейнере
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости (этот слой будет закеширован, если не менялись pyproject.toml/poetry.lock)
RUN poetry install --without dev --no-root

# В самом конце копируем код
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

