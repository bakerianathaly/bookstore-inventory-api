FROM ghcr.io/astral-sh/uv:0.6.6 AS uv

FROM python:3.12-slim AS builder
WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-hashes -o requirements.txt

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Caracas

COPY --from=uv /uv /usr/local/bin/uv
COPY --from=builder /app/requirements.txt /app/requirements.txt
RUN uv pip install --system -r /app/requirements.txt

COPY . .

COPY Docker/local/entrypoint.sh /entrypoint.sh
COPY Docker/local/start.sh /start.sh
RUN chmod +x /entrypoint.sh /start.sh

EXPOSE 8020

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
