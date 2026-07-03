from sqlmodel import create_engine, Session, SQLModel
from app.models import ChatSession, ChatMessage 

#Create a local SQLite file 
sqlite_file_name = "medical_state.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

#echo=True prints the raw SQL to your terminal for learning
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    """Tells SQLModel to create the database file and all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """A helper function to open a database connection for our API endpoints."""
    with Session(engine) as session:
        yield session