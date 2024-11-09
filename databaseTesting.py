import sqlite3
import subprocess

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('my_database.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        inode INTEGER,
        filepath TEXT,
        filename TEXT
    )
''')

# Insert data
filepath = "/Users/rishinatraj/Downloads"
fileData = subprocess.run(f"ls -i1p '{filepath}' | grep -v /", capture_output=True, text=True, shell=True).stdout.split('\n')
for(n) in range(len(fileData)):
    fileData[n]=fileData[n].lstrip()
    fileData[n]=fileData[n].split(' ', maxsplit=1)
    if fileData[n] != ['']:
        cursor.execute("INSERT INTO users (inode, filepath, filename) VALUES (?, ?, ?)", (fileData[n][0], filepath, fileData[n][1]))



# Query data
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

# Commit changes and close the connection
conn.commit()
conn.close()