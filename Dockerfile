FROM node:25-alpine AS node-builder

WORKDIR /builder

COPY src src

WORKDIR /builder/src/frontend

RUN npm install && \
    npm run build

FROM python:3.14.0-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY uv.lock .
COPY pyproject.toml .
COPY README.md .
COPY src src

COPY --from=node-builder /builder/src/resources/static/css/main.css src/resources/static/css/main.css

EXPOSE 8080

ENTRYPOINT ["uv", "run", "uvicorn", "src.microfastapitodowebapp.main:app", "--no-access-log", "--port", "8080"]
