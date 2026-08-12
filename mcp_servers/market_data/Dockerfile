FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
ARG BUILD_ID=dev
ENV BUILD_ID=${BUILD_ID}
ENV PORT=8081
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY mcp_servers ./mcp_servers
ENV PYTHONPATH=/app/mcp_servers
EXPOSE 8081
CMD ["sh", "-c", ".venv/bin/python -m market_data.server"]
