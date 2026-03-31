import os
from sqlmodel import Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def get_db():
    with Session(engine) as session:
        yield session
