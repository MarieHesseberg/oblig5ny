from flask import g
import sqlite3

def get_db():
    db = sqlite3.connect('soknader.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()

    # Create soknader table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soknader (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            navn_forelder_1 TEXT,
            prioriterte_barnehager TEXT,
            resultat TEXT,
            valgt_barnehage TEXT,
            tidspunkt_oppstart TEXT  -- New column for start date
        )
    ''')
    db.commit()

    # Optional: Check if the column 'tidspunkt_oppstart' already exists
    # If not, add it (useful if running this after table creation)
    table_info = cursor.execute("PRAGMA table_info(soknader)").fetchall()
    columns = [info[1] for info in table_info]

    if 'tidspunkt_oppstart' not in columns:
        cursor.execute("ALTER TABLE soknader ADD COLUMN tidspunkt_oppstart TEXT")
        db.commit()

    db.close()

def close_connection(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    init_db()
