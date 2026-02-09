from sqlmodel import SQLModel, create_engine, text
from typing import Generator
from sqlmodel import Session
import os

# Use absolute path for database to avoid data loss on restart/cwd change
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sqlite_file_name = os.path.join(BASE_DIR, "database.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)
    
    # Auto-migration for existing requirement table to add version_id
    with engine.connect() as conn:
        try:
            # Check if column exists (naive check)
            result = conn.execute(text("PRAGMA table_info(requirement)")).fetchall()
            columns = [row[1] for row in result]
            if "version_id" not in columns:
                print("Migrating: Adding version_id to requirement table...")
                conn.execute(text("ALTER TABLE requirement ADD COLUMN version_id INTEGER REFERENCES projectversion(id)"))
                conn.commit()
        except Exception as e:
            print(f"Migration check failed (safe to ignore if new db): {e}")

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
