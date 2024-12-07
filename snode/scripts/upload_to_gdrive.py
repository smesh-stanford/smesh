import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Define the Google Drive API scopes and service account file path
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = "/home/pi/smesh/snode/credentials.json" # Replace with the path to your service account file

# Create credentials using the service account file
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Google Drive service
service = build('drive', 'v3', credentials=credentials)

def upload_files(folder_path, drive_folder_id=None):
    """Upload all files in the specified folder to Google Drive."""

    # If drive_folder_id is None, upload to the root directory.
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            continue

        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
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
                print(f'File {filename} exists. Updating...')
                updated_file = service.files().update(fileId=file_id, media_body=media).execute()
                print(f'{filename} updated successfully.')
            else:
                print(f'Uploading {filename}...')
                file_metadata = {'name': filename}
                if drive_folder_id:
                    file_metadata['parents'] = [drive_folder_id]
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f'{filename} uploaded successfully.')

if __name__ == '__main__':
    # Replace 'your/local/folder/path' with the path to your local folder
    folder_to_upload = '/home/pi/smesh/snode/data' # Replace with the path to your data folder

    # Optionally, specify the Google Drive folder ID where you want to upload the files
    # If you leave drive_folder_id as None, files will be uploaded to the root directory
    drive_folder_id = "1W3gRqD1Szc4eqjIz9ESWps5qM-8NQ2Qj"  # Replace with your folder ID if needed

    upload_files(folder_to_upload, drive_folder_id)

    
