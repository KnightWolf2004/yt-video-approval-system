from sqlmodel import SQLModel, create_engine

postgres_url = "postgresql://postgres:adm1n@localhost:5432/yt_app"
engine = create_engine(postgres_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)