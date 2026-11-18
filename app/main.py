import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import config, models  # noqa: F401  (registers the tables)
from .database import init_db
from .routers import admin as admin_router
from .routers import auth as auth_router
from .routers import complaints as complaints_router

os.makedirs(config.UPLOAD_DIR, exist_ok=True)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FixMyCity", version="0.1.0", lifespan=lifespan)

app.include_router(auth_router.router)
app.include_router(complaints_router.router)
app.include_router(admin_router.router)
app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}


# Frontend (HTML/CSS/JS). Mounted last so it never hides the API routes.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
