FROM python:3.11-slim
WORKDIR /app
COPY app ./app
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn==0.32.0
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
