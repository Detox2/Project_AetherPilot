from typing import Callable, Dict, Optional

from prompts.tools.ask_followup_question import get_ask_followup_question_description
from prompts.tools.attempt_completion import get_attempt_completion_description
from prompts.tools.web_search import get_web_search_description

# Dictionary mapping tool names to their description functions
TOOL_DESCRIPTION_MAP: Dict[str, Callable] = {
    "ask_followup_question": get_ask_followup_question_description,
    "attempt_completion": get_attempt_completion_description,
    "web_search": get_web_search_description,
}

# Always available tools
ALWAYS_AVAILABLE_TOOLS = {"attempt_completion",
                          "ask_followup_question", "web_search"}

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
