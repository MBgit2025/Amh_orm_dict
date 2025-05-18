#database_utils.py (Merges models.py, database.py, and backend logic from main.py)
import os
import random
from typing import Optional, List, Dict

import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import streamlit as st # For st.cache_resource and st.cache_data

# --- Database Setup ---
DATABASE_FILE = "multilingual_dictionary.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

Base = declarative_base()

class Word(Base):
    __tablename__ = "langtable"
    id = Column(Integer, primary_key=True, index=True)
    srno = Column(Integer, index=True, autoincrement=True) # Keep srno if needed, but id is primary
    Amharic = Column(String, index=True)
    OromLatin = Column(String, index=True)
    OromSaba = Column(String, index=True)
    English = Column(String, index=True)

# Use st.cache_resource for expensive resource creation like engine
@st.cache_resource
def get_engine():
    print("Creating database engine...")
    # The connect_args={"check_same_thread": False} is essential for SQLite with Streamlit/multithreading
    return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

engine = get_engine() # Initialize engine once

@st.cache_resource
def get_sessionmaker(_engine): # Pass engine to make it cacheable based on engine
    print("Creating session maker...")
    return sessionmaker(autocommit=False, autoflush=False, bind=_engine)

SessionLocal = get_sessionmaker(engine) # Initialize SessionLocal once

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables_if_not_exist():
    print("Checking and creating tables...")
    Base.metadata.create_all(bind=engine)

def populate_database_from_excel(db: Session):
    """Populates the database from the Excel file if it's empty."""
    if db.query(Word).first():
        print("Database already populated.")
        return

    print("Populating database from Excel...")
    excel_file_path = os.path.join(os.path.dirname(__file__), "data", "lang.xlsx")
    # If database_utils.py is in root, and data/ is a subdir:
    # excel_file_path = os.path.join("data", "lang.xlsx")


    try:
        df = pd.read_excel(excel_file_path)
        required_columns = ["Amharic", "OromLatin", "OromSaba", "English"] # srno is auto
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        words_to_add = []
        for index, row in df.iterrows():
            # Handle potential NaN values from Excel, convert to None (NULL in DB)
            amharic = row["Amharic"] if pd.notna(row["Amharic"]) else None
            oromlatin = row["OromLatin"] if pd.notna(row["OromLatin"]) else None
            oromsaba = row["OromSaba"] if pd.notna(row["OromSaba"]) else None
            english = row["English"] if pd.notna(row["English"]) else None

            word_data = Word(
                Amharic=amharic,
                OromLatin=oromlatin,
                OromSaba=oromsaba,
                English=english,
            )
            words_to_add.append(word_data)
        
        db.bulk_save_objects(words_to_add)
        db.commit()
        print(f"Database populated successfully with {len(words_to_add)} entries.")

    except FileNotFoundError:
        st.error(f"Error: Excel file not found at {excel_file_path}. Ensure 'data/lang.xlsx' exists.")
        print(f"Error: Excel file not found at {excel_file_path}")
    except Exception as e:
        st.error(f"Error populating database: {e}")
        print(f"Error populating database: {e}")

# --- Database Query Functions ---
# Use st.cache_data for functions that return data and can be cached
# Note: Caching might not be ideal for search if results need to be fresh or DB is huge.
# For this small app, it's okay. Consider TTL or more granular caching if needed.

def search_word_in_db(language: str, query: str) -> List[Dict[str, Optional[str]]]:
    db_gen = get_db()
    db = next(db_gen)
    try:
        if not query: # Return empty list if query is empty
            return []

        # Case-insensitive search using lower() or ilike() if supported by SQLite version/SQLAlchemy
        # For simplicity with basic SQLite, contains might be case-sensitive.
        # Using func.lower for case-insensitivity
        query_lower = query.lower()

        if language == "Amharic":
            results = db.query(Word).filter(func.lower(Word.Amharic).contains(query_lower)).all()
        elif language == "OromLatin":
            results = db.query(Word).filter(func.lower(Word.OromLatin).contains(query_lower)).all()
        elif language == "OromSaba":
            results = db.query(Word).filter(func.lower(Word.OromSaba).contains(query_lower)).all()
        elif language == "English":
            results = db.query(Word).filter(func.lower(Word.English).contains(query_lower)).all()
        else:
            return [] # Or raise an error

        return [
            {
                "amharic": word.Amharic,
                "oromlatin": word.OromLatin,
                "oromsaba": word.OromSaba,
                "english": word.English,
            }
            for word in results
        ]
    finally:
        db.close()

def get_random_word_from_db() -> Optional[Dict[str, Optional[str]]]:
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Efficient way to get a random row in SQLite
        random_word = db.query(Word).order_by(func.random()).first()
        if random_word:
            return {
                "amharic": random_word.Amharic,
                "oromlatin": random_word.OromLatin,
                "oromsaba": random_word.OromSaba,
                "english": random_word.English,
            }
        return None
    finally:
        db.close()

# --- One-time setup ---
def initialize_database():
    """Creates tables and populates the database if needed."""
    # This function will be called once at the start of the Streamlit app.
    # We use a flag in session state to ensure it only runs truly once per app lifecycle,
    # not just per script run if using st.cache_resource for engine/session.
    if "db_initialized" not in st.session_state:
        create_tables_if_not_exist()
        db_gen = get_db()
        db = next(db_gen)
        try:
            populate_database_from_excel(db)
        finally:
            db.close()
        st.session_state.db_initialized = True
        print("Database initialization complete.")
    else:
        print("Database already initialized in this session.")
