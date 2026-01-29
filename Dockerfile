FROM python:3.9-slim

WORKDIR /app/api

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/src ./src

EXPOSE 10000

# Use sh -c to expand PORT env var, Render sets PORT dynamically
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
