
from .config import settings
from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends

engine = create_engine(settings.database_url)

# création des tables de la base de données
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise

get_db = Annotated[Session, Depends(get_session)]

