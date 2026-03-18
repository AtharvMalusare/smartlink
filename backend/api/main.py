from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import engine, Base
import api.models
from api.routes import links, slug, redirect, rules, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartLink")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(links.router)
app.include_router(slug.router)
app.include_router(rules.router)
app.include_router(analytics.router)
app.include_router(redirect.router)

@app.get("/health")
def health():
    return {"status": "ok"}