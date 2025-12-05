from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONNECTION_STR = os.getenv("DATABASE_URL")

try:
    db_engine = create_engine(DB_CONNECTION_STR)
    print("Database connection established successfully.")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    db_engine = None