import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import datetime
import re

# Define the Google Drive API scopes and service account file path
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = "/home/pi/Documents/smesh/snode/credentials.json" # Replace with the path to your service account file

# Create credentials using the service account file
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Google Drive service
service = build('drive', 'v3', credentials=credentials)

def upload_files(folder_path, drive_folder_id=None):
    """Upload all files in the specified folder to Google Drive."""

    for node in os.listdir(folder_path):
        print(f"Writing data for node {node}")

        node_folder_path = os.path.join(folder_path, node)
        for filename in os.listdir(node_folder_path):
            print(f"Checking for filename {filename}")

            if filename.endswith(".txt"):
                continue

            file_path = os.path.join(node_folder_path, filename)

            print(f"cur file_path {file_path}")
            if os.path.isfile(file_path):

                print(f"Trying to upload for {file_path}")

                # Build the query to search for existing files
                query = f"mimeType != 'application/vnd.google-apps.folder' and name = '{filename}' and trashed = false"
                if drive_folder_id:
                    query += f" and '{drive_folder_id}' in parents"

                # Search for the file
                response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
                files = response.get('files', [])

                media = MediaFileUpload(file_path, resumable=True)

                if files:
                    # File exists, update it
                    file_id = files[0]['id']
                    print(f'[{datetime.datetime.now()}] File {filename} exists. Updating...')
                    updated_file = service.files().update(fileId=file_id, media_body=media).execute()
                    print(f'{filename} updated successfully.')
                else:
                    print(f'[{datetime.datetime.now()}] Uploading {filename}...')
                    file_metadata = {'name': filename}
                    if drive_folder_id:
                        file_metadata['parents'] = [drive_folder_id]
                    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    print(f'{filename} uploaded successfully.')

def get_latest_data_folder(base_path):
    """
    Find the most recent folder in base_path matching pattern: data-YYYY-MM-DD_HH-MM-SS
    """
    folder_pattern = re.compile(r"^data-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$")
    
    folders = [
        f for f in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, f)) and folder_pattern.match(f)
    ]
    
    if not folders:
        raise FileNotFoundError("No matching data folders found")

    # Sort by datetime parsed from the folder name
    latest_folder = max(
        folders,
        key=lambda name: datetime.datetime.strptime(name, "data-%Y-%m-%d_%H-%M-%S")
    )
    
    return os.path.join(base_path, latest_folder)

if __name__ == '__main__':
    print(f'[{datetime.datetime.now()}] STARTING UPLOAD PYTHON SCRIPT.')

    # simply select the latest folder
    base_path = "/home/pi/Documents/smesh/snode"
    folder_to_upload = get_latest_data_folder(base_path)
    print(f"[{datetime.datetime.now()}] Latest folder: {folder_to_upload}")

    # Optionally, specify the Google Drive folder ID where you want to upload the files
    # If you leave drive_folder_id as None, files will be uploaded to the root directory
    drive_folder_id = "13E62bL_auwAmuIFAQLVoc6MlOeNJkU7h"  # Replace with your folder ID if needed

    upload_files(folder_to_upload, drive_folder_id)

