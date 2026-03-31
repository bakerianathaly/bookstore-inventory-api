FROM ghcr.io/astral-sh/uv:0.6.6 AS uv

FROM python:3.12-slim AS builder
WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Caracas
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY . .

COPY Docker/test/entrypoint.sh /entrypoint.sh
COPY Docker/test/start.sh /start.sh
RUN chmod +x /entrypoint.sh /start.sh

EXPOSE 8020

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
