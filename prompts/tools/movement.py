import time
import logging
import pydirectinput

def get_movement_description() -> str:
    return f"""
## move
Description: This tool allows movement in a game through emulation, but currently only 'down' is implemented.

### Parameters:
- **direction** (required) → Must be 'down'

### Usage Example:
```xml
<move>
    down
</move>
"""

def handle_move(tag) -> str:
    """
    Only handles the 'down' direction, pressing 's'.
    Everything else returns an error.
    """

    move_tag = tag.find('move')
    if not move_tag:
        return "No <move> specified for movement."

    direction = move_tag.get_text(strip=True).lower()

    logging.info(f"Movement direction: {direction}")

    try:
        if direction == 'down':
            pydirectinput.press('s')  # Press 's' for Down
            time.sleep(0.5)
            return "Moved Down (S key pressed)"
        else:
            return f"Error: Unsupported command '{direction}'. Only 'down' is implemented."

    except Exception as e:
        logging.error(f"Error in handle_move: {e}")
        return f"Error: Something went wrong pressing 'down'."
