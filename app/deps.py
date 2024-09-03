from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_htmx import htmx_init
from starlette.templating import Jinja2Templates

from app.models import SessionLocal, init_db


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


templates = Jinja2Templates(directory="app/templates")

htmx_init(templates=templates)
