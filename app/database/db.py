from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import AppSettings

# Initialize the database engine
engine = create_engine(AppSettings.DATABASE_URL)

# Create a custom base class for declarative models
BaseModel = declarative_base()

# Initialize the session factory
# `expire_on_commit=False` ensures that session objects remain valid across transactions
DatabaseSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()
