FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN cd backend && pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]