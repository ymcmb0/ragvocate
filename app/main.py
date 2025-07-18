# app/main.py

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="RAGvocate API")

app.include_router(router, prefix="/api")
