from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1234@localhost/test'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True,
    # needed only for SQLite
    # connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
