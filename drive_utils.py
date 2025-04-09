import os
import io
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Load environment variables
load_dotenv()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials():
    """Get valid user credentials from the existing OAuth session.

    Returns:
        Credentials, the obtained credential.
    """
    try:
        # Import Flask session
        from flask import session

        # Check if we have a Google token in the session
        if 'google_token' in session:
            token_data = session['google_token']
            print(f"Found Google token in session: {token_data.keys() if isinstance(token_data, dict) else 'Not a dict'}")

            # Create credentials from the token
            if isinstance(token_data, dict) and 'access_token' in token_data:
                from google.oauth2.credentials import Credentials

                # Create credentials directly from environment variables
                # This bypasses the need for a refresh token
                client_id = os.environ.get('GOOGLE_CLIENT_ID')
                client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

                # Use the access token from the session
                access_token = token_data.get('access_token')

                # Create credentials with all required fields
                # For non-refreshable credentials, we need to set refresh_token=None
                creds = Credentials(
                    token=access_token,
                    refresh_token=None,  # Explicitly set to None to indicate non-refreshable
                    client_id=client_id,
                    client_secret=client_secret,
                    token_uri='https://oauth2.googleapis.com/token',
                    scopes=['https://www.googleapis.com/auth/drive.file']
                )

                print("Successfully created credentials from session token")
                return creds
            else:
                print("Token data doesn't contain access_token")
        else:
            print("No Google token found in session")

        # If we get here, we couldn't create credentials
        print("WARNING: Could not create Google Drive credentials from session")
        print("Please make sure you're logged in and have authorized the application")
        return None

    except Exception as e:
        print(f"ERROR creating credentials: {str(e)}")
        return None

def get_drive_service():
    """Get a Google Drive service instance.

    Returns:
        Drive service instance.
    """
    creds = get_credentials()
    if not creds:
        return None

    try:
        # If we got a string (access token), create credentials from it
        if isinstance(creds, str):
            from google.oauth2.credentials import Credentials
            creds = Credentials(creds)

        # Build the service
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"ERROR creating Drive service: {str(e)}")
        return None

def upload_file_to_drive(file_path, file_name, folder_id=None):
    """Upload a file to Google Drive.

    Args:
        file_path: Path to the file to upload
        file_name: Name to give the file in Drive
        folder_id: ID of the folder to upload to (optional)

    Returns:
        ID of the uploaded file, or None if upload failed
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            return None

        # Get Drive service
        service = get_drive_service()
        if not service:
            print("ERROR: Could not get Drive service - Google Drive integration is not properly configured")
            print("To enable Google Drive integration, you need to:")
            print("1. Set up OAuth 2.0 credentials in Google Cloud Console")
            print("2. Add the Google Drive API scope to your OAuth consent screen")
            print("3. Configure the redirect URI in Google Cloud Console")
            print("4. Complete the OAuth flow once to get a refresh token")
            return None

        # Prepare file metadata
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # Upload the file
        # Use non-resumable upload to avoid token refresh issues
        media = MediaFileUpload(file_path, resumable=False)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"SUCCESS: File uploaded to Drive with ID: {file.get('id')}")
        return file.get('id')

    except Exception as e:
        error_msg = str(e)
        print(f"ERROR uploading file to Drive: {error_msg}")

        # For token-related errors, return a special value to indicate local file storage
        if "token" in error_msg.lower() or "credentials" in error_msg.lower() or "refresh" in error_msg.lower():
            print("Token-related error detected. Falling back to local file storage.")
            return 'local_file'
        # Provide more specific error messages based on common issues
        elif "invalid_grant" in error_msg.lower():
            print("The OAuth token has expired or is invalid. Please re-authenticate.")
            return 'local_file'
        elif "permission" in error_msg.lower():
            print("Permission denied. Make sure the authenticated user has access to the folder.")
            return 'local_file'
        elif "not found" in error_msg.lower():
            print(f"Folder not found: {folder_id}. Check that the folder ID is correct.")
            return 'local_file'

        return None

def get_file_url(file_id):
    """Get the URL for a file in Google Drive.

    Args:
        file_id: ID of the file in Drive

    Returns:
        URL to access the file, or None if retrieval failed
    """
    try:
        service = get_drive_service()
        if not service:
            print("ERROR: Could not get Drive service")
            return None

        # Get the file to ensure it exists and get its permissions
        file = service.files().get(fileId=file_id, fields='webViewLink').execute()

        # Return the web view link
        return file.get('webViewLink')

    except Exception as e:
        print(f"ERROR getting file URL: {str(e)}")
        return None

def get_or_create_folder(folder_name, parent_folder_id=None):
    """Get a folder by name, or create it if it doesn't exist.

    Args:
        folder_name: Name of the folder
        parent_folder_id: ID of the parent folder (optional)

    Returns:
        ID of the folder, or None if retrieval/creation failed
    """
    try:
        service = get_drive_service()
        if not service:
            print("ERROR: Could not get Drive service")
            return None

        # Search for the folder
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"

        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        # If folder exists, return its ID
        if items:
            print(f"Found existing folder: {folder_name} with ID: {items[0]['id']}")
            return items[0]['id']

        # If folder doesn't exist, create it
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        folder = service.files().create(body=folder_metadata, fields='id').execute()
        print(f"Created new folder: {folder_name} with ID: {folder.get('id')}")
        return folder.get('id')

    except Exception as e:
        print(f"ERROR getting/creating folder: {str(e)}")
        return None

def download_file_from_drive(file_id, output_path):
    """Download a file from Google Drive.

    Args:
        file_id: ID of the file in Drive
        output_path: Path where to save the downloaded file

    Returns:
        True if download was successful, False otherwise
    """
    try:
        service = get_drive_service()
        if not service:
            print("ERROR: Could not get Drive service")
            return False

        # Get the file
        request = service.files().get_media(fileId=file_id)

        # Download the file
        with io.BytesIO() as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")

            # Save the file
            with open(output_path, 'wb') as f:
                f.write(fh.getvalue())

        print(f"File downloaded to: {output_path}")
        return True

    except Exception as e:
        print(f"ERROR downloading file: {str(e)}")
        return False
