FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Non-root user (SEC-0022)
RUN groupadd --system --gid 1000 app && \
    useradd --system --uid 1000 --gid app --home-dir /app --no-create-home --shell /usr/sbin/nologin app && \
    mkdir -p /app && \
    chown -R app:app /app

WORKDIR /app

COPY --chown=app:app pyproject.toml uv.lock ./
COPY --chown=app:app app ./app

RUN uv sync --frozen --no-dev && \
    chown -R app:app /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER app

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=20s \
  CMD curl -fsS http://localhost:8001/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--proxy-headers"]
