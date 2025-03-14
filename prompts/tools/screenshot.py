import logging
import os
import pyautogui  # pip install pyautogui
import tempfile
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_screenshot_description() -> str:
    return f"""
## screenshot
Description: This tool takes a screenshot of the current screen, uploads it to Google Drive, and returns a shareable URL.

Parameters:
- description (optional): A brief description of the screenshot. If not provided, a timestamp will be used.

Usage:
<screenshot>
    <description>Game menu screen</description>
</screenshot>
"""

def get_drive_service():
    """
    Creates and returns a Google Drive service object.
    Requires a service account credentials file.
    """
    try:
        # Check if credentials file exists
        creds_file = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
        if not creds_file or not os.path.exists(creds_file):
            logging.error("Google Drive credentials file not found")
            return None
            
        # Load credentials from the service account file
        creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
        
        # Build the Drive service
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error creating Drive service: {e}")
        return None

def upload_to_drive(file_path, file_name):
    """
    Uploads a file to Google Drive and returns the file ID and shareable URL.
    """
    try:
        service = get_drive_service()
        if not service:
            return None, "Failed to initialize Google Drive service"
        
        # File metadata
        file_metadata = {
            'name': file_name,
            'mimeType': 'image/png'
        }
        
        # Upload file
        media = MediaFileUpload(file_path, mimetype='image/png')
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        # Get file ID
        file_id = file.get('id')
        
        # Make the file publicly accessible
        service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()
        
        # Get shareable URL
        shareable_url = f"https://drive.google.com/uc?id={file_id}"
        
        return file_id, shareable_url
    except Exception as e:
        logging.error(f"Error uploading to Google Drive: {e}")
        return None, f"Error uploading to Google Drive: {e}"

def handle_screenshot(tag) -> str:
    """
    Handler for <screenshot> tag.
    Takes a screenshot, uploads it to Google Drive, and returns a response with the image URL.
    """
    # Get description if provided
    description_tag = tag.find('description')
    if description_tag and description_tag.get_text(strip=True):
        image_description = description_tag.get_text(strip=True)
    else:
        image_description = f"Screenshot taken at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        # Create a temporary file for the screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Capture the screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(temp_filename)
        logging.info(f"Screenshot saved temporarily as {temp_filename}")
        
        # Upload to Google Drive
        file_id, image_url = upload_to_drive(temp_filename, f"Screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png")
        
        # Clean up the temporary file
        try:
            os.unlink(temp_filename)
        except Exception as e:
            logging.warning(f"Failed to delete temporary file {temp_filename}: {e}")
        
        if not file_id:
            return f"Error: {image_url}"
        
        # Format the response for Claude
        content_list = []
        content_list.append({
            "type": "text",
            "text": f"Screenshot generated with description: {image_description}"
        })
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        })
        
        # Return a formatted response that Claude can understand
        return f"Screenshot uploaded to Google Drive. URL: {image_url}\n\nDescription: {image_description}"
    except Exception as e:
        logging.error(f"Error capturing or uploading screenshot: {e}")
        return f"Error capturing or uploading screenshot: {e}"
