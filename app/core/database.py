from sqlmodel import SQLModel, create_engine
import os


postgres_url = os.getenv("DATABASE_URL")
assert postgres_url is not None
engine = create_engine(postgres_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)