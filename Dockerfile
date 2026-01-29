FROM python:3.9-slim

WORKDIR /app/api

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/src ./src

EXPOSE 10000

# Now WORKDIR is /app/api, so src.main:app will be found
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "${PORT:-10000}"]
