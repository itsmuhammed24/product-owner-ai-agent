FROM python:3.11-slim
WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -e ".[dev,rag,chroma]"

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()" || exit 1
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
