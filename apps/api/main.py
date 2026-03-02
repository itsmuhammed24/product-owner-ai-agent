"""Entrypoint FastAPI — CORS, rate limit, routes."""

from dotenv import load_dotenv

load_dotenv()  # Charger .env avant tout accès à os.getenv

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.rate_limit import RateLimitMiddleware
from apps.api.routes import router

app = FastAPI(
    title="Product Owner AI Agent",
    version="0.1.0",
    description="Workflow agentic : feedback → insights → backlog → stories",
)

# CORS : CORS_ORIGINS=url1,url2 ou * (toutes)
_cors_origins = os.getenv("CORS_ORIGINS", "*")
_cors_list = [o.strip() for o in _cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_list if _cors_list else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Rate limit (désactivable via RATE_LIMIT_PER_MIN=0)
if int(os.getenv("RATE_LIMIT_PER_MIN", "20")) > 0:
    app.add_middleware(RateLimitMiddleware)
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Product Owner AI Agent", "docs": "/docs", "health": "/health"}
