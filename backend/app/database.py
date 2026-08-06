# app/database.py
import sqlite3
from typing import Dict, Any, List, Optional

DB_NAME = "readora.db"

def init_db():
    """Initializes the database table if it doesn't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_text TEXT,
                simplified_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_document(filename: str, original_text: str, simplified_text: str) -> int:
    """Saves a document extraction and its simplified text into the history."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO document_history (filename, original_text, simplified_text)
            VALUES (?, ?, ?)
        """, (filename, original_text, simplified_text))
        conn.commit()
        return cursor.lastrowid

def get_all_documents() -> List[Dict[str, Any]]:
    """Retrieves all saved document history entries ordered by newest first."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, original_text, simplified_text, created_at 
            FROM document_history 
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_document_by_id(doc_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single document entry by its ID."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, original_text, simplified_text, created_at 
            FROM document_history 
            WHERE id = ?
        """, (doc_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_document(doc_id: int) -> bool:
    """Deletes a document entry from history by ID."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM document_history WHERE id = ?", (doc_id,))
        conn.commit()
        return cursor.rowcount > 0