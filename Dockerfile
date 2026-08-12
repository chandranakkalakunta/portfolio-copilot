FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
ARG BUILD_ID=dev
ENV BUILD_ID=${BUILD_ID}
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY api ./api
EXPOSE 8080
CMD ["sh", "-c", ".venv/bin/uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
