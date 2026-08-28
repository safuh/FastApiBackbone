# syntax=docker/dockerfile:1
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install . \
    && chown -R app:app /app

USER app
EXPOSE 8000

CMD ["uvicorn", "fastapi_backbone.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
