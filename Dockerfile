FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    WALKIE_DATA_DIR=/data

COPY . .

RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    fi

CMD ["python", "main.py"]
