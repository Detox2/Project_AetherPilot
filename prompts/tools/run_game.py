import logging
import time
import pydirectinput

def get_game_description() -> str:
    return f"""
## run_game
Description: This tool **starts Games** if they are not running and returns a structured result.

### Parameters:
- **folder_path** (required) → Gives the game location to open the game

### Usage Example:
#### ✅ If the game started successfully
```xml
<run_game>
    <folder_path>C:/Users/Agentic_AI/Documents/Project_AetherPilot/games</folder_path>
</run_game>
"""

def handle_run_game(tag) -> str:
    """
    Steps:
    1) Press Ctrl+O
    2) Type the folder path
    3) Press Enter
    4) Press Ctrl+E to focus the search bar
    5) Press Enter twice to confirm
    """

    # Extract the <folder_path> text directly from the XML
    folder_tag = tag.find('folder_path')
    if not folder_tag:
        return "No <folder_path> specified for run_game."

    # Strip only surrounding whitespace
    folder_name = folder_tag.get_text(strip=True)

    # If your XML usage includes quotes, remove them:
    if folder_name.startswith('"') and folder_name.endswith('"'):
        folder_name = folder_name[1:-1]

    # Print debug info to see exactly what path is being typed
    logging.info(f"DEBUG final folder_name: {repr(folder_name)}")

    try:
        logging.info("Using PyDirectInput to open game folder...")

        # Step 1: Press Ctrl+O
        pydirectinput.keyDown('ctrl')
        pydirectinput.press('o')
        pydirectinput.keyUp('ctrl')
        time.sleep(1)

        # Step 2: Type the folder path
        pydirectinput.write(folder_name, interval=0.05)
        time.sleep(0.5)

        # Step 3: Press Enter
        pydirectinput.press('enter')
        time.sleep(2)

        # Step 4: Press Ctrl+E for search bar
        pydirectinput.keyDown('ctrl')
        pydirectinput.press('e')
        pydirectinput.keyUp('ctrl')
        time.sleep(1)

        # Step 5 & 6: Press Enter twice
        pydirectinput.press('enter')
        time.sleep(2)
        pydirectinput.press('enter')
        time.sleep(2)

        return "success"

    except Exception as e:
        logging.error(f"Error in handle_run_game: {e}")
        return "failure"
