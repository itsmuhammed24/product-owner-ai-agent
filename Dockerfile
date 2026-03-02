FROM python:3.11-slim
WORKDIR /app

# 1. Deps d'abord → cache pip quand seul le code change (sentence-transformers ~50s)
COPY requirements-docker.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements-docker.txt
# 2. Code ensuite — pip install . --no-deps ~1s (deps déjà installées)
COPY pyproject.toml README.md .
COPY po_agent po_agent
COPY apps apps
RUN pip install . --no-deps

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()" || exit 1
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
