FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    WALKIE_DATA_DIR=/data

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS test
COPY . .
CMD ["pytest"]

FROM base AS runtime
COPY . .
CMD ["python", "main.py"]
