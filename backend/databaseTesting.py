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

# Function to get files and directories recursively
def getFiles(filePaths, conn=None, cursor=None):
    if conn is None or cursor is None:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            inode INTEGER PRIMARY KEY,
            filepath TEXT,
            filename TEXT,
            type TEXT
        )
    ''') #types FILE FOLDER

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
                                     SET filepath = ?, filename = ?, type = ?
                                     WHERE inode = ?
                                     """, (filepath1, fileData[n][1], "FOLDER" if os.path.isdir(filepath1) else "FILE", fileData[n][0]))
                else:
                    cursor.execute("INSERT INTO files (inode, filepath, filename, type) VALUES (?, ?, ?, ?)", (fileData[n][0], filepath1, fileData[n][1], "FOLDER" if not os.path.isdir(filepath1) else "FILE"))

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)