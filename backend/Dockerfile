FROM python:3.10-slim AS base
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY common/python/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /modules
ENV PYTHONPATH=/modules

FROM base AS dev
WORKDIR /app

CMD ["python", "main.py"]

FROM base AS prod
WORKDIR /app

COPY backend/src/ .
COPY common ./modules/common

CMD ["python", "main.py"]
