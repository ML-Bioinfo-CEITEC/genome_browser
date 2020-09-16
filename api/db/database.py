from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from db.config import SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True,
)
Base = declarative_base()
db = SQLAlchemy()

