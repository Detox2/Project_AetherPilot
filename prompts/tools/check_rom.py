import os

def get_check_game_folder_description() -> str:
    return f"""
## check_rom
Description: This tool checks if a specified game file is present in a known "games" folder.

Parameters:
- game_name (required): The exact name of the game file to check (e.g. "my_game.exe").

Usage:
<check_rom>
    <game_name>my_game.exe</game_name>
</check_rom>
"""

def handle_check_game_folder(tag) -> str:

    # 1) Extract <game_name> from the tag
    game_tag = tag.find('game_name')
    if not game_tag or not game_tag.get_text(strip=True):
        return "Error: No <game_name> provided."

    game_name = game_tag.get_text(strip=True)


    # 2) Define your "games" folder path
    games_folder = "C:/Users/Agentic_AI/Documents/Project_AetherPilot/games"
    full_path = os.path.join(games_folder, game_name)

    # 3) Check if the file exists
    if os.path.isfile(full_path):
        return f"Found {game_name} at {full_path}"
    else:
        return f"{game_name} not found in {games_folder}"
