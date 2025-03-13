import logging
import pyautogui  # pip install pyautogui

def get_screenshot_description() -> str:
    return f"""
## screenshot
Description: This tool takes a screenshot of the current screen and saves it as a PNG file.

Parameters:
- filename (optional): Name of the screenshot file to save. If not provided, use a default like screenshot.png.

Usage:
<screenshot>
    <filename>my_screenshot.png</filename>
</screenshot>
"""

def handle_screenshot(tag) -> str:
    """
    Handler for <claude_screenshot> tag.
    Checks for <filename> child. If found, uses it; otherwise uses a default name.
    """
    filename_tag = tag.find('filename')
    if filename_tag and filename_tag.get_text(strip=True):
        filename = filename_tag.get_text(strip=True)
    else:
        filename = "screenshot.png"

    try:
        # Capture the screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        logging.info(f"Screenshot saved as {filename}")
        return f"Screenshot saved successfully as {filename}"
    except Exception as e:
        logging.error(f"Error capturing screenshot: {e}")
        return f"Error capturing screenshot: {e}"
