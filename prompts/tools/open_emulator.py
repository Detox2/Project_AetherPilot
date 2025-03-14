import pyautogui as pg
import time

def get_emu_description() -> str:
    return f"""
## run_emu
Description: This tool **starts BizHawk Emulator** if it is not running and returns a structured result. This is so that the game can be launched

### Usage Example:
#### ✅ If BizHawk successfully started
```xml
<run_emu>
Request to open BizHawk
</run_emu>
"""
    
def handle_run_emu(tag) -> str:
    """
    Attempts to start BizHawk by:
    1) Pressing Windows key
    2) Typing "EmuHawk"
    3) Pressing Enter
    
    Returns:
      'success' on no exceptions,
      'failure: <error>' on exception.
    """
    try:
        pg.press("winleft")
        time.sleep(1)
        pg.write("EmuHawk", interval=0.05)
        time.sleep(0.5)
        pg.press("enter")
        time.sleep(10)

        # If we got here without an error, assume success
        return "success"
    except Exception as e:
        return f"failure: {e}"
