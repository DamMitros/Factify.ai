FROM python:3.10-slim AS base
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY src/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS final
WORKDIR /app

COPY src/ .

CMD ["python", "main.py"]
