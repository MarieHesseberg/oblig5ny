import sqlite3

# Define the name of your database file
DATABASE = 'soknader.db'

# Create a connection to the database (it will create the file if it does not exist)
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Create a table in the database
cursor.execute('''
    CREATE TABLE IF NOT EXISTS soknader (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        navn_forelder_1 TEXT,
        prioriterte_barnehager TEXT,
        resultat TEXT,
        valgt_barnehage TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database '{DATABASE}' created successfully with table 'soknader'.")
