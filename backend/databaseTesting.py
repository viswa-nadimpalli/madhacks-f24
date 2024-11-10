from flask import Flask, request, jsonify
import sqlite3
import subprocess
import os

app = Flask(__name__)

# Function to get files and directories recursively
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
        if not os.path.exists(filepath1):
            continue

        # Process files in the directory (non-directories)
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

        # Process directories recursively
        fileDataDirectories = subprocess.run(f"ls -1p '{filepath1}' | grep '/$' | grep -v '.app/$'", capture_output=True, text=True, shell=True).stdout.split('\n')
        fileDataDirectories = [d.rstrip('/') for d in fileDataDirectories if d]
        if fileDataDirectories:
            for index in range(len(fileDataDirectories)):
                fileDataDirectories[index] = os.path.join(filepath1, fileDataDirectories[index])
            getFiles(fileDataDirectories, conn, cursor)

    conn.commit()
    if conn and not filePaths:
        conn.close()


@app.route('/LocalPaths', methods=['POST'])
def handle_post():
    # Get filePaths from the POST request
    data = request.get_json()
    if 'filePaths' not in data:
        return jsonify({"error": "filePaths key is required in the JSON payload"}), 400

    filePaths = data['filePaths']
    if not isinstance(filePaths, list) or not filePaths:
        return jsonify({"error": "filePaths should be a non-empty list"}), 400

    try:
        # Initialize DB connection
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
        # Get files
        getFiles(filePaths, conn, cursor)
        return jsonify({"status": "success", "message": "File paths processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)