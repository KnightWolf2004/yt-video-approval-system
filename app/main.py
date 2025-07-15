from dotenv import load_dotenv
load_dotenv()

from sqlmodel import Session
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import create_db_and_tables
from app.auth.routes import auth_routes
from app.users.routes import user_routes
from app.videos.routes import video_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(video_routes.router)
