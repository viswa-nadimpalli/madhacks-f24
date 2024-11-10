import os
import pickle
import google.auth
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# The SCOPES variable defines the access permissions the app requests
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# File where we save the tokens for each account
TOKEN_DIR = "./tokens/"

# Ensure the tokens directory exists
if not os.path.exists(TOKEN_DIR):
    os.makedirs(TOKEN_DIR)

# Function to handle authentication
def authenticate(account_name):
    """Authenticate the user and return the drive service for the given account."""
    token_file = os.path.join(TOKEN_DIR, f"token_{account_name}.pickle")
    
    # Check if token file exists for this account
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    else:
        creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the current account
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    # Build the Google Drive API service
    service = build('drive', 'v3', credentials=creds)
    return service

# Function to list files in the Google Drive
def list_drive_files(service):
    """List files in the authenticated user's Google Drive."""
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(f'{item["name"]} ({item["id"]})')

# Function to iteratively print the structure of the Google Drive
def print_drive_structure_iteratively(service, parent_id='root'):
    """Iteratively print the structure of the Google Drive."""
    # Queue to hold folders to process
    queue = [{"id": parent_id, "indent": 0}]
    
    while queue:
        current_folder = queue.pop(0)  # Get the first folder in the queue
        folder_id = current_folder["id"]
        indent = current_folder["indent"]
        
        # List files and folders in the current folder
        results = service.files().list(
            q=f"'{folder_id}' in parents",  # Fetch files within the parent folder
            fields="nextPageToken, files(id, name, mimeType, parents)",
            pageSize=100).execute()
        
        items = results.get('files', [])
        
        if not items:
            print('No files found.')
        else:
            for item in items:
                # Get the file's parent ID (should be the folder ID we are currently iterating over)
                parent_name = "Root" if not item.get('parents') else item['parents'][0]
                
                # Indentation for folder structure visualization
                print('  ' * indent + f"{item['name']} (ID: {item['id']}, Type: {item['mimeType']}, Parent: {parent_name})")
                
                # If the item is a folder, add it to the queue to process its contents
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    queue.append({"id": item['id'], "indent": indent + 1})
                    
# Function to get a list of available accounts
def list_available_accounts():
    """List all available accounts by checking saved token files."""
    accounts = []
    for filename in os.listdir(TOKEN_DIR):
        if filename.startswith("token_") and filename.endswith(".pickle"):
            accounts.append(filename[6:-7])  # Extract account name from filename
    return accounts

# Function to add a new account
def add_new_account():
    """Authenticate and add a new account."""
    account_name = input("Enter a name for your new account: ")
    print(f"Authenticating new account: {account_name}...")
    
    # Authenticate the new account
    authenticate(account_name)
    print(f"Account {account_name} authenticated and saved.")

def open_file_in_browser(file_id):
    """Opens a Google Drive file in the default web browser using its File ID."""
    base_url = "https://drive.google.com/file/d/{}/view"
    url = base_url.format(file_id)
    webbrowser.open(url)
    print(f"Opened file: {url}")

# Main function to select an account and list files or add a new account
def main():
    print("Welcome to Google Drive File Access")
    
    # List available accounts
    accounts = list_available_accounts()

    if not accounts:
        print("No accounts found. Please create a new account.")
        add_new_account()
        return

    accToAccess = None

    # Ask whether to sign in with an existing account or a new account
    print("Select an option:")
    print("1. Sign in with an existing account")
    print("2. Sign in with a new account")

    option = input("Enter the option number: ")

    if option == '1':
        # If there are existing accounts, prompt the user to select one
        print("Select an account to use:")
        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. {account}")
        selected_account = int(input("Enter the account number: ")) - 1

        if selected_account < 0 or selected_account >= len(accounts):
            print("Invalid selection.")
            return

        accToAccess = accounts[selected_account]

    elif option == '2':
        # Add a new account
        add_new_account()
        return

    else:
        print("Invalid selection.")
        return

    # Ask if the user wants to see the first 10 files from one of the saved accounts
    print("Do you want to see the first 10 files from any of your accounts?")
    print("1. Yes")
    print("2. No")
    view_files_option = input("Enter the option number: ")

    if view_files_option == '1':
        print(f"Viewing the first 10 files from account: {accToAccess}...")

        # Authenticate the selected account and list files
        service_for_files = authenticate(accToAccess)
        print_drive_structure_iteratively(service_for_files)
    
    # file_id = input("Enter the Google Drive File ID: ")
    # open_file_in_browser(file_id)

if __name__ == '__main__':
    main()
