import sqlite3
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


@app.route('/LocalPaths', methods=['POST'])
def getFiles(filePaths, conn=None, cursor=None):
    if conn is None or cursor is None:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            inode INTEGER PRIMARY KEY,
            filepath TEXT,
            filename TEXT
        )
    ''')

    for filepath1 in filePaths:
        fileData = subprocess.run(f"ls -i1p '{filepath1}' | grep -v /", capture_output=True, text=True, shell=True).stdout.split('\n')
        for n in range(len(fileData)):
            fileData[n] = fileData[n].lstrip()
            fileData[n] = fileData[n].split(' ', maxsplit=1)
            if fileData[n] != ['']:
                cursor.execute("SELECT 1 FROM files WHERE inode = ?", (fileData[n][0],))
                row = cursor.fetchone()
                if row:
                    cursor.execute("""UPDATE files
                                     SET filepath = ?, filename = ?
                                     WHERE inode = ?
                                     """, (filepath1, fileData[n][1], fileData[n][0]))
                else:
                    cursor.execute("INSERT INTO files (inode, filepath, filename) VALUES (?, ?, ?)", (fileData[n][0], filepath1, fileData[n][1]))

        fileDataDirectories = subprocess.run(f"ls -1p '{filepath1}' | grep '/$' | grep -v '\.app/$'", capture_output=True, text=True, shell=True).stdout.split('\n')
        fileDataDirectories = [d.rstrip('/') for d in fileDataDirectories if d]
        if fileDataDirectories:
            for index in range(len(fileDataDirectories)):
                fileDataDirectories[index] = filepath1 + "/" + fileDataDirectories[index]
            getFiles(fileDataDirectories, conn, cursor)

    conn.commit()
    if conn and not filePaths:
        conn.close()

filepath = "/Users/kanishk/Desktop/MadHacksTest"
getFiles(filePaths=[filepath])
