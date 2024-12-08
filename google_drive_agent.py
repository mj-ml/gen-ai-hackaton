# Import required libraries
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io

# Configuration
CREDENTIALS_FILE = "credentials.json"  # Path to your Google Cloud credentials
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']  # Read-only access to Google Drive
FOLDER_ID = "YOUR_FOLDER_ID"  # Replace with the ID of your Google Drive folder

# Authentication function
def authenticate():
    """
    Authenticate and create a Google Drive API service.
    Uses a Service Account to connect to the API.
    """
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)

# Function to list all files in a folder
def list_files_in_folder(service, folder_id):
    """
    List all files in a specified Google Drive folder.

    Parameters:
        service: Authenticated Google Drive API service.
        folder_id: The ID of the folder to query.

    Returns:
        A list of files (name and ID).
    """
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files

# Function to search for files by keyword
def search_files(service, folder_id, keyword):
    """
    Search for files within a folder by keyword in their names.

    Parameters:
        service: Authenticated Google Drive API service.
        folder_id: The ID of the folder to query.
        keyword: Keyword to search for in file names.

    Returns:
        A list of matching files (name and ID).
    """
    query = f"'{folder_id}' in parents and trashed = false and name contains '{keyword}'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files

# Function to download a file by its ID
def download_file(service, file_id, file_name):
    """
    Download a file from Google Drive.

    Parameters:
        service: Authenticated Google Drive API service.
        file_id: The ID of the file to download.
        file_name: The name to save the file locally.

    Returns:
        None
    """
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    print(f"File '{file_name}' downloaded successfully.")

# Main execution
if __name__ == "__main__":
    # Authenticate with Google Drive API
    service = authenticate()
    print("Authenticated successfully!")

    # List all files in the folder
    print("Listing all files in the folder:")
    files = list_files_in_folder(service, FOLDER_ID)
    for file in files:
        print(f"Name: {file['name']}, ID: {file['id']}")

    # Search for files by keyword
    keyword = "report"  # Replace with the search keyword
    print(f"\nSearching for files containing '{keyword}':")
    search_results = search_files(service, FOLDER_ID, keyword)
    for file in search_results:
        print(f"Name: {file['name']}, ID: {file['id']}")

    # Optionally download the first matching file
    if search_results:
        file_to_download = search_results[0]
        download_file(service, file_to_download['id'], file_to_download['name'])
