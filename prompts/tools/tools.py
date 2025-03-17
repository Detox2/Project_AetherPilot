from typing import Callable, Dict, Optional

from prompts.tools.ask_followup_question import get_ask_followup_question_description
from prompts.tools.attempt_completion import get_attempt_completion_description
from prompts.tools.web_search import get_web_search_description
from prompts.tools.emu_download import get_download_tool_description
from prompts.tools.screenshot import get_screenshot_description
from prompts.tools.open_emulator import get_emu_description
from prompts.tools.run_game import get_game_description
from prompts.tools.check_rom import get_check_game_folder_description
from prompts.tools.movement import get_movement_description

# Dictionary mapping tool names to their description functions
TOOL_DESCRIPTION_MAP: Dict[str, Callable] = {
    "ask_followup_question": get_ask_followup_question_description,
    "attempt_completion": get_attempt_completion_description,
    "web_search": get_web_search_description,
    "download_url": get_download_tool_description,
    "run_emu": get_emu_description,
    "run_game": get_game_description,
    "check_rom": get_check_game_folder_description,
    "movement": get_movement_description
}

# Always available tools
ALWAYS_AVAILABLE_TOOLS = {"attempt_completion",
                          "ask_followup_question", "web_search", "download_url", "run_emu", "check_rom", "run_game", "screenshot", "movement"}

# Sample tool groups (this can be loaded dynamically)
TOOL_GROUPS = {
    "default": {"tools": [""]},
}


def get_tool_descriptions_for_mode(
    mode: str,
) -> str:
    """
    Generates tool descriptions based on the given mode.

    Returns:
        str: The formatted tool descriptions.
    """
    tools = set()

    # Add tools from mode's group
    tool_group = TOOL_GROUPS.get(mode, {}).get("tools", [])
    tools.update(tool_group)

    # Add always available tools
    tools.update(ALWAYS_AVAILABLE_TOOLS)

    # Generate tool descriptions
    descriptions = [TOOL_DESCRIPTION_MAP[tool]()
                    for tool in tools if tool in TOOL_DESCRIPTION_MAP]

    return "# Tools\n\n{}".format("\n\n".join(descriptions))


# # Example usage
if __name__ == "__main__":
    mode = "default"

    print(get_tool_descriptions_for_mode(mode))
