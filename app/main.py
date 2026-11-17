from fastapi import FastAPI

app = FastAPI(title="FixMyCity", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  (registers the tables)
from .database import init_db
from .routers import auth as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FixMyCity", version="0.1.0", lifespan=lifespan)

app.include_router(auth_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}