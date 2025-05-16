from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import settings
from typing import Generator


engine = create_engine(settings.DATABASE, echo=False)

SessionLocal = sessionmaker(
                        bind=engine,
                        autocommit = False,
                        autoflush = False
                        )

Base = declarative_base()


def get_db() -> Generator:
    '''This function will yield a connection to the database everytime it called'''
    
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
