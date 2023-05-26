from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://admin:TUVdH980kaZKj6hFe6UmzfBRrGsVqBP0@dpg-ch4dbpm4dad97s29seng-a.singapore-postgres.render.com/dbchat"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()