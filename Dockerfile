# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    UVICORN_WORKERS=4

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app/ ./app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
 && chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

# We leave ENTRYPOINT unset so that both `docker run` and Compose can override as needed.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
