FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
ARG PIP_INDEX_URL=https://pypi.org/simple
RUN pip install --index-url "$PIP_INDEX_URL" --no-cache-dir -r requirements.txt

COPY app.py workflow.py smoke_api.py ./

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]