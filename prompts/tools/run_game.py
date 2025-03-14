import logging
import time
import pydirectinput
import os

def get_game_description() -> str:
    return f"""
## run_game
Description: This tool **starts Games** if they are not running and returns a structured result.

### Parameters:
- **game_name** (optional) → Name of the game to search for in the games folder
- **game_path** (optional) → Full path to the specific game file to open
- **folder_path** (optional) → Gives the game location to open the game folder

### Usage Example:
#### ✅ If the game started successfully with specific game path
```xml
<run_game>
    <game_path>C:\\Users\\Agentic_AI\\Documents\\Project_AetherPilot\\games\\Pokemon Ruby.gba</game_path>
</run_game>
"""

def handle_run_game(tag) -> str:
    """
    Steps:
    1) Press Ctrl+O
    2) Type the path (game or folder), one character at a time, preserving uppercase letters
       and handling backslashes correctly.
    3) Press Enter
    4) If folder path was provided, press Ctrl+E to focus the search bar
    5) If game_name was provided, type the search term
    6) Press Enter twice to confirm
    """
    # Default games folder path with backslashes as required
    games_folder = "C:\\Users\\Agentic_AI\\Documents\\Project_AetherPilot\\games"
    
    game_name_tag = tag.find('game_name')
    game_tag = tag.find('game_path')
    folder_tag = tag.find('folder_path')
    
    if game_name_tag:
        # If game_name is provided, we'll open the games folder and search for the game
        game_name = game_name_tag.get_text(strip=True)
        path = games_folder
        is_game_path = False
        search_term = game_name
        logging.info(f"Game name specified: {game_name}, will search in games folder")
    elif game_tag:
        path = game_tag.get_text(strip=True)
        # Convert forward slashes to backslashes if present
        path = path.replace('/', '\\')
        # If path doesn't include the full games folder path, prepend it
        if not path.lower().startswith("c:\\users\\agentic_ai\\documents\\project_aetherpilot\\games"):
            game_file = path.split('\\')[-1] if '\\' in path else path
            path = f"{games_folder}\\{game_file}"
        is_game_path = True
        search_term = None
        logging.info(f"Full game path specified: {path}")
    elif folder_tag:
        path = folder_tag.get_text(strip=True)
        # Convert forward slashes to backslashes if present
        path = path.replace('/', '\\')
        # If path doesn't include the full games folder path, use the default
        if not path.lower().startswith("c:\\users\\agentic_ai\\documents\\project_aetherpilot\\games"):
            path = games_folder
        is_game_path = False
        search_term = None
        logging.info(f"Folder path specified: {path}")
    else:
        # Default to games folder if no parameters specified
        path = games_folder
        is_game_path = False
        search_term = None
        logging.info(f"No parameters specified, defaulting to games folder: {path}")

    # Remove surrounding quotes if present
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]

    logging.info(f"DEBUG final path: {repr(path)}")

    try:
        logging.info("Using PyDirectInput to open game...")

        # Step 1: Press Ctrl+O
        pydirectinput.keyDown('ctrl')
        pydirectinput.press('o')
        pydirectinput.keyUp('ctrl')
        time.sleep(1)

        # Step 2: Press each character individually
        for char in path:
            # Space
            if char == ' ':
                pydirectinput.press('space')

            # Backslash
            elif char == '\\':
                # Press the backslash key
                pydirectinput.press('\\')

            # Colon
            elif char == ':':
                # Press the colon key (shift + semicolon)
                pydirectinput.keyDown('shift')
                pydirectinput.press(';')
                pydirectinput.keyUp('shift')
                
            # Underscore
            elif char == '_':
                # Press the underscore key (shift + minus)
                pydirectinput.keyDown('shift')
                pydirectinput.press('-')
                pydirectinput.keyUp('shift')

            # Alphabetic characters
            elif char.isalpha():
                if char.isupper():
                    # Press SHIFT + the lowercase version of the char
                    pydirectinput.keyDown('shift')
                    pydirectinput.press(char.lower())
                    pydirectinput.keyUp('shift')
                else:
                    pydirectinput.press(char)
            
            # Everything else (digits, punctuation, etc.)
            else:
                # If pydirectinput supports the char name, it will succeed
                # Otherwise, you'd handle more special cases here
                pydirectinput.press(char)

            time.sleep(0.05)

        time.sleep(0.5)

        # Step 3: Press Enter
        pydirectinput.press('enter')
        time.sleep(2)

        # If it's a folder path, we need additional steps to select a game
        if not is_game_path:
            # Step 4: Press Ctrl+E to focus the search bar
            pydirectinput.keyDown('ctrl')
            pydirectinput.press('e')
            pydirectinput.keyUp('ctrl')
            time.sleep(1)
            
            # If we have a search term, type it
            if search_term:
                logging.info(f"Typing search term: {search_term}")
                for char in search_term:
                    # Space
                    if char == ' ':
                        pydirectinput.press('space')
                    # Underscore
                    elif char == '_':
                        # Press the underscore key (shift + minus)
                        pydirectinput.keyDown('shift')
                        pydirectinput.press('-')
                        pydirectinput.keyUp('shift')
                    # Alphabetic characters
                    elif char.isalpha():
                        if char.isupper():
                            # Press SHIFT + the lowercase version of the char
                            pydirectinput.keyDown('shift')
                            pydirectinput.press(char.lower())
                            pydirectinput.keyUp('shift')
                        else:
                            pydirectinput.press(char)
                    # Everything else (digits, punctuation, etc.)
                    else:
                        pydirectinput.press(char)
                    time.sleep(0.05)
                
                time.sleep(0.5)

            # Steps 5 & 6: Press Enter twice
            pydirectinput.press('enter')
            time.sleep(2)
            pydirectinput.press('enter')
            time.sleep(2)

        return "success"

    except Exception as e:
        logging.error(f"Error in handle_run_game: {e}")
        return "failure"
