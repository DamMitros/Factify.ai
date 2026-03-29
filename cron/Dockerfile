FROM python:3.10-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml uv.lock ./

ENV UV_PROJECT_ENVIRONMENT="/opt/venv"
RUN uv sync --group cron --no-install-project --no-default-groups
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir /modules
ENV PYTHONPATH=/modules

FROM base AS dev
WORKDIR /app

CMD ["uv", "run", "main.py"]

FROM base AS prod
WORKDIR /app

COPY cron/src/ .
COPY common ./modules/common

RUN python jobs/analyze/nlp/utils/download_base_model.py

CMD ["uv", "run", "main.py"]
