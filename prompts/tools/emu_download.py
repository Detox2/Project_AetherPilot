import os
import requests
import logging

def get_download_tool_description() -> str:
    return f"""
## download_url
Description: This tool downloads a file from a given URL and saves it locally.

Parameters:
- url: (required) The direct URL of the file to download.

Usage:
<download_url>
    <url>https://example.com/path/to/file.pdf</url>
</download_url>
"""

def handle_download_tool(tag) -> str:
    """
    Handler for <download_tool> tag.
    Looks for <url> child tag and attempts to download the file.
    Returns a plain-text message indicating success or failure.
    """
    url_tag = tag.find('url')
    if url_tag:
        download_url = url_tag.get_text(strip=True)
        print('download_url', download_url)
        if download_url:
            try:
                filename = download_file(download_url)
                print('filename', filename)
                return f"File downloaded successfully. Saved as: {filename}"
            except Exception as e:
                logging.error(f"Error during file download: {e}")
                return f"Error downloading file: {e}"
    return "No URL provided for download tool."


def download_file(download_url: str) -> str:
    local_filename = os.path.basename(download_url) or download_file
    print('localfilename', local_filename)

    response = requests.get(download_url, stream=True)
    print('response', response)
    response.raise_for_status()  # Raises HTTPError if the status is 4xx/5xx

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return local_filename

