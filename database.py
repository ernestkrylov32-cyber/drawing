import sqlite3
import os
from pathlib import Path

# Render disk или локальная папка
DATA_DIR = os.environ.get("DATA_DIR")

if DATA_DIR:
    try:
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Диск не примонтирован или нет прав — fallback на локальную папку
        DATA_DIR = Path(__file__).parent / "data"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
else:
    DATA_DIR = Path(__file__).parent / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(DATA_DIR) / "app.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS drawings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT,
            image_data TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_drawings_user ON drawings(user_id);
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
