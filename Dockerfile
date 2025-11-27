FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction

COPY . .

CMD ["python"]