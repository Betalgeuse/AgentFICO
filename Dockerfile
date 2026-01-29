FROM python:3.9-slim

WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/src ./src

EXPOSE 10000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "10000"]
