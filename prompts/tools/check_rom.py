import os

def get_check_game_folder_description() -> str:
    return f"""
## check_rom
Description: This tool checks if a game with a similar name is present in the "games" folder.

Parameters:
- game_name (required): The name of the game to search for (e.g. "sonic" or "pokemon").

Usage:
<check_rom>
    <game_name>sonic</game_name>
</check_rom>
"""

def handle_check_game_folder(tag) -> str:

    # 1) Extract <game_name> from the tag
    game_tag = tag.find('game_name')
    if not game_tag or not game_tag.get_text(strip=True):
        return "Error: No <game_name> provided."

    game_name = game_tag.get_text(strip=True).lower()

    # 2) Define your "games" folder path
    games_folder = "C:/Users/Agentic_AI/Documents/Project_AetherPilot/games"
    
    # 3) Get all files in the games folder
    if not os.path.exists(games_folder):
        return f"Games folder not found at {games_folder}"
    
    all_games = [f for f in os.listdir(games_folder) if os.path.isfile(os.path.join(games_folder, f))]
    
    # 4) Find games with similar names
    similar_games = [game for game in all_games if game_name.lower() in game.lower()]
    
    # 5) Handle results based on number of matches
    if not similar_games:
        return f"No games containing '{game_name}' found in {games_folder}"
    elif len(similar_games) == 1:
        # Only one match found, return it
        matched_game = similar_games[0]
        full_path = os.path.join(games_folder, matched_game)
        return f"Found game with similar name: {matched_game} at {full_path}"
    else:
        # Multiple matches found, ask user to choose
        options = "\n".join([f"{i+1}. {game}" for i, game in enumerate(similar_games)])
        return f"Found multiple games containing '{game_name}':\n{options}\nPlease specify which game you want to play."
