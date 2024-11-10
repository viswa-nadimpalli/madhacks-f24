from flask import Flask, request, jsonify
import sqlite3
import subprocess
import os
from google_drive_app import *

app = Flask(__name__)

# Function to add a new account
def add_new_accountAPI(account_name, conn=None, cursor=None):
    """Authenticate and add a new account."""
    
    # Authenticate the new account
    service = authenticate(account_name)
    print(f"Account {account_name} authenticated and saved.")

    if conn is None or cursor is None:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goofiles (
            Gideon TEXT PRIMARY KEY,
            Parent TEXT,
            Name TEXT,
            Type TEXT,
            Account TEXT
        )
    ''')
    print_and_store_drive_structure(service, cursor, parent_id='root', indent=0, account=account_name)

def print_and_store_drive_structure(service, cursor, parent_id='root', indent=0, account=''):
    """Recursively print the structure of the Google Drive and store details in a database, including the root folder."""
    # If processing the root folder, handle it separately
      
    if parent_id == 'root':
        # Fetch the root folder's metadata

        root_metadata = service.files().get(fileId='root', fields='id, name, mimeType').execute() 
        # Insert root folder into the database
        cursor.execute('''
            INSERT OR IGNORE INTO goofiles (Gideon, Parent, Name, Type, Account)
            VALUES (?, ?, ?, ?, ?)
        ''', (root_metadata['id'], None, root_metadata['name'], "FOLDER" if root_metadata['mimeType'] == "application/vnd.google-apps.folder" else "FILE", account))
        
        # Commit the changes
        cursor.connection.commit()
        
        # Print root folder info
        print(f"{root_metadata['name']} (ID: {root_metadata['id']}, Type: folder, Parent: None)")
    
    # List files and folders in the current folder
    results = service.files().list(
        q=f"'{parent_id}' in parents",
        fields="nextPageToken, files(id, name, mimeType, parents)",
        pageSize=100).execute()
    
    items = results.get('files', [])
    
    if not items:
        print('  ' * indent + 'No files found.')
    else:
        for item in items:
            # Get the file's parent ID (should be the folder ID we are currently iterating over)
            parent_id = "Root" if not item.get('parents') else item['parents'][0]
            
            # Indentation for folder structure visualization
            print('  ' * indent + f"{item['name']} (ID: {item['id']}, Type: {item['mimeType']}, Parent: {parent_id})")
            
            # Insert file/folder details into the database
            cursor.execute('''
                INSERT OR IGNORE INTO goofiles (Gideon, Parent, Name, Type, Account)
                VALUES (?, ?, ?, ?, ?)
            ''', (item['id'], parent_id, item['name'], "FOLDER" if item['mimeType'] == "application/vnd.google-apps.folder" else "FILE", account))
            
            # Commit changes to the database
            cursor.connection.commit()
            
            # If the item is a folder, recursively call this function
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                print_and_store_drive_structure(service, cursor, parent_id=item['id'], indent=indent + 1, account=account)


def getFiles(filePaths, conn=None, cursor=None):
    if conn is None or cursor is None:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

    # Update table schema to include filepath
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            inode INTEGER PRIMARY KEY,
            parent_inode INTEGER,
            filename TEXT,
            type TEXT,
            filepath TEXT
        )
    ''')  # types: FILE, FOLDER

    for filepath1 in filePaths:
        if not os.path.exists(filepath1):
            continue

        # Set parent_inode to NULL for the first level
        parent_inode = None

        # Process files in the directory (non-directories)
        fileData = subprocess.run(
            f"ls -i1p '{filepath1}' | grep -v /", 
            capture_output=True, text=True, shell=True
        ).stdout.split('\n')
        
        for n in range(len(fileData)):
            fileData[n] = fileData[n].lstrip().split(' ', maxsplit=1)
            if fileData[n] != ['']:
                inode, filename = fileData[n]
                filepath = os.path.join(filepath1, filename)
                cursor.execute("SELECT 1 FROM files WHERE inode = ?", (inode,))
                row = cursor.fetchone()
                if row:
                    cursor.execute("""
                        UPDATE files
                        SET parent_inode = ?, filename = ?, type = ?, filepath = ?
                        WHERE inode = ?
                    """, (parent_inode, filename, "FILE", filepath, inode))
                else:
                    cursor.execute("""
                        INSERT INTO files (inode, parent_inode, filename, type, filepath)
                        VALUES (?, ?, ?, ?, ?)
                    """, (inode, parent_inode, filename, "FILE", filepath))

        # Process directories at first level
        fileDataDirectories = subprocess.run(
            f"ls -1p '{filepath1}' | grep '/$' | grep -v '.app/$'",
            capture_output=True, text=True, shell=True
        ).stdout.split('\n')

        fileDataDirectories = [d.rstrip('/') for d in fileDataDirectories if d]
        if fileDataDirectories:
            for index in range(len(fileDataDirectories)):
                dir_path = os.path.join(filepath1, fileDataDirectories[index])
                dir_inode = os.stat(dir_path).st_ino
                cursor.execute("SELECT 1 FROM files WHERE inode = ?", (dir_inode,))
                row = cursor.fetchone()
                if row:
                    cursor.execute("""
                        UPDATE files
                        SET parent_inode = ?, filename = ?, type = ?, filepath = ?
                        WHERE inode = ?
                    """, (parent_inode, fileDataDirectories[index], "FOLDER", dir_path, dir_inode))
                else:
                    cursor.execute("""
                        INSERT INTO files (inode, parent_inode, filename, type, filepath)
                        VALUES (?, ?, ?, ?, ?)
                    """, (dir_inode, parent_inode, fileDataDirectories[index], "FOLDER", dir_path))

    conn.commit()
    if conn and not filePaths:
        conn.close()


def getFilesGoog(conn=None, cursor=None):
    # Ensure the tokens directory exists
    if not os.path.exists(TOKEN_DIR):
        os.makedirs(TOKEN_DIR)

    if conn is None or cursor is None:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goofiles (
            Gideon TEXT PRIMARY KEY,
            Parent TEXT,
            Name TEXT,
            Account TEXT,
            Type TEXT
        )
    ''') #type can be "FILE" or "FOLDER"

    # List available accounts
    accounts = list_available_accounts()

    if not accounts:
        print("No accounts found. Please create a new account.")
        return
    
    for account in accounts:
        service_for_files = authenticate(account)
        print_and_store_drive_structure(service_for_files, cursor ,"root", 0, account)
        


@app.route('/LocalPaths', methods=['POST'])
def handle_post_localfiles():
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
    
@app.route('/gooPaths/<name>', methods=['POST'])
def handle_post_gfiles(name):
    try:
        # Execute the function with the path variable `name`
        result = add_new_accountAPI(name)
        
        # Return a success response if the function completes without errors
        return jsonify({"status": "success", "message": result}), 200
    
    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!"


def vtableSetup(conn=None, cursor=None):
    if conn is None or cursor is None:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vtable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent TEXT,
            name TEXT,
            source INTEGER,
            type TEXT,
            iid TEXT
        )
    ''')  # types: FILE, FOLDER
    

    conn.commit()
    conn.close()

# Route to add a new row to vtable
@app.route('/add_vtable_entry', methods=['POST'])
def add_vtable_entry():
    vtableSetup()
    
    data = request.get_json()

    # Validate the request payload
    required_keys = ['parent', 'name', 'source', 'type', 'iid']
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing one or more required fields: parent, name, source, type, iid"}), 400

    try:
        # Connect to the database and insert the new entry
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vtable (parent, name, source, type, iid)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['parent'], data['name'], data['source'], data['type'], data['iid']))
        conn.commit()
        entry_id = cursor.lastrowid  # Get the auto-incremented ID of the inserted row
        conn.close()

        # Return a success response with the ID of the new entry
        return jsonify({"status": "success", "id": entry_id, "message": "Entry added successfully"}), 201

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/getDir/<type>/<id>', methods=['GET'])
def getDirLocal(type, id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    if type == '1':
        try:
            # Query to get all inode and filename where the parent inode matches the provided id
            cursor.execute('''
                SELECT inode, filename FROM files WHERE parent_inode = ?
            ''', (id,))
            rows = cursor.fetchall()

            # Format the result as a list of dictionaries
            result = [{"inode": row[0], "filename": row[1]} for row in rows]

            conn.close()
            return jsonify({"status": "success", "data": result}), 200

        except sqlite3.Error as e:
            conn.close()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    elif type == '2':
        try:
            # Query to get all inode and filename where the parent inode matches the provided id
            cursor.execute('''
                SELECT Gideon, Name FROM goofiles WHERE Parent = ?
            ''', (id,))
            rows = cursor.fetchall()

            # Format the result as a list of dictionaries
            result = [{"Gideon": row[0], "Name": row[1]} for row in rows]

            conn.close()
            return jsonify({"status": "success", "data": result}), 200

        except sqlite3.Error as e:
            conn.close()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    else:
        try:
            # Query to get all inode and filename where the parent inode matches the provided id
            cursor.execute('''
                SELECT id, source FROM vtable WHERE Parent = ?
            ''', (id,))
            rows = cursor.fetchall()

            # Format the result as a list of dictionaries
            result = [{"id": row[0], "source": row[1]} for row in rows]

            conn.close()
            return jsonify({"status": "success", "data": result}), 200

        except sqlite3.Error as e:
            conn.close()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/delDir/<type>', methods=['DELETE'])
def delete(type, conn=None, cursor=None):
    try:
        id = request.args.get('id')
        if not id:
            return jsonify({"error": "ID query parameter is required"}), 400


        if conn is None or cursor is None:
            conn = sqlite3.connect('my_database.db')
            cursor = conn.cursor()

        if type == '1':  # Case for local files
            # Delete from `files` where the filepath matches the given `id`
            cursor.execute("""
                DELETE FROM files
                WHERE filepath LIKE ?
            """, (f'{id}%',))

            # Delete from `vtable` where the source matches `1-<id>`
            cursor.execute("""
                DELETE FROM vtable
                WHERE source LIKE ?
            """, (f'1-{id}%',))

        elif type == '2':  # Case for Google files
            # Delete from `goofiles` where the account matches the given `id`
            cursor.execute("""
                DELETE FROM goofiles
                WHERE account = ?
            """, (id,))

            # Delete from `vtable` where the source matches `2-<id>`
            cursor.execute("""
                DELETE FROM vtable
                WHERE source LIKE ?
            """, (f'2-{id}%',))

        else:  # Default case for other deletions
            cursor.execute("""
                DELETE FROM vtable
                WHERE parent = ? AND source = '3'
            """, (id,))

        conn.commit()
        return jsonify({"status": "success", "message": f"Entries deleted for type {type} and id {id}."}), 200

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/listAccounts', methods=['GET'])
def list_accounts_endpoint():
    try:
        accounts = list_available_accounts()
        return jsonify({"status": "success", "accounts": accounts}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/openFile/<type>/<file_id>', methods=['POST'])
def open_file_endpoint(type, file_id):
    if type == '2':  # For Google Drive files
        try:
            url = open_file_in_browser(file_id)
            return jsonify({"status": "success", "message": f"File opened in browser: {url}"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    elif type == '1':  # For local storage using inode
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect('my_database.db')
            cursor = conn.cursor()

            # Query to get the file path and filename from the inode
            cursor.execute("SELECT filepath, filename FROM files WHERE inode = ?", (file_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                filepath, filename = result
                if os.path.exists(filepath):
                    webbrowser.open(f'file://{filepath}')
                    print(f"Opened file: {filepath}")
                    return jsonify({"status": "success", "message": f"Local file opened: {filename}"}), 200
                else:
                    return jsonify({"status": "error", "message": "File not found on disk"}), 404
            else:
                return jsonify({"status": "error", "message": "Inode not found in the database"}), 404
        except sqlite3.Error as e:
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid type provided"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)