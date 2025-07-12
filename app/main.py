from sqlmodel import Session
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from .database import engine, create_db_and_tables
from .models import Role, Status, User, Video

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(lifespan=lifespan)
