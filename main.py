import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
import os

from prompts.tools.check_rom import handle_check_game_folder
from prompts.tools.movement import handle_move
from prompts.tools.open_emulator import handle_run_emu
from prompts.tools.run_game import handle_run_game
from prompts.tools.screenshot import handle_screenshot

load_dotenv()  # This will load from the .env file in the current directory


from prompts.tools.emu_download import handle_download_tool
from prompts.tools.tools import get_tool_descriptions_for_mode
from prompts.sections.tool_use import getSharedToolUseSection
from prompts.sections.tool_use_guidelines import getToolUseGuidelinesSection
from prompts.sections.objective import getObjectiveSection
from prompts.sections.noToolsUsed import get_no_tools_used_section
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

telegram_token = os.getenv("TELEGRAM_TOKEN")
openrouter_api_key = os.getenv("OPENROUTER_KEY")
openrouter_base_url = "https://openrouter.ai/api/v1"
openrouter_model = "anthropic/claude-3.7-sonnet"
openrouter_temperature = 0.5
tavily_api_key = os.getenv("TAVILY_KEY")
conversation_history = []

model = ChatOpenAI(api_key=openrouter_api_key, base_url=openrouter_base_url,
                   model=openrouter_model, temperature=openrouter_temperature)


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am your bot. How can I assist you?')


async def echo(update: Update, context: CallbackContext) -> None:
    logging.info(f'User message: {update.message.text}')

    # Loop until isFinished is true or maximum iterations reached
    max_iterations = 30
    iterations = 0
    isFinished = False
    isToolUsed = False
    tool_response = ""
    while not isFinished and iterations < max_iterations:
        next_step = await handle_message(update.message.text if not isToolUsed else tool_response, isToolUsed)
        logging.info(f"Next step: {next_step}")
        # Debug message removed
        tool_response, isFinished = await extract_tool_response(next_step)
        isToolUsed = True
        iterations += 1

    if iterations >= max_iterations:
        logging.warning("Maximum iterations reached in echo function.")

    isToolUsed = False
    logging.info(f'Final tool response: {tool_response}')

    await update.message.reply_text(tool_response)


def handle_ask_followup_question(tag) -> str:
    """
    Handler for the <ask_followup_question> tag.
    This function looks for a <question> child tag and returns its text.
    """
    question_tag = tag.find('question')
    if question_tag:
        text = question_tag.get_text(strip=True)
        if text:
            return text
    return "No question provided"


def handle_attempt_completion(tag) -> str:
    """
    Handler for the <attempt_completion> tag.
    This function looks for a <result> child tag and returns its text.
    """
    result_tag = tag.find('result')
    if result_tag:
        text = result_tag.get_text(strip=True)
        if text:
            return text
    return "No result provided"


def handle_web_search(tag) -> str:
    query_tag = tag.find('query')
    if query_tag:
        query_text = query_tag.get_text(strip=True)
        if query_text:
            try:
                tavily_client = TavilyClient(api_key=tavily_api_key)
                search_response = tavily_client.search(
                    query=query_text, include_raw_content=True)
                # Format the results for the LLM.  This is *very* important.
                formatted_results = format_search_results(search_response)
                return formatted_results
            except Exception as e:
                logging.error(f"Error during web search: {e}")
                return f"<error>Error during web search: {e}</error>"
    return "<error>No query provided for web search.</error>"


def format_search_results(search_response):
    """Formats search results for inclusion in the prompt."""
    formatted_results = ""
    for result in search_response["results"]:
        formatted_results += f"<title>{result['title']}</title>\n<content>{result['content']}</content>\n"
    return f"<results>{formatted_results}</results>"



async def extract_tool_response(response: str) -> tuple[str, bool]:

    soup = BeautifulSoup(response, "html.parser")

    for thinking_tag in soup.find_all(["thinking"]):
        thinking_tag.decompose()

    # Dictionary mapping tag names to their handler functions
    handlers = {
        "attempt_completion": handle_attempt_completion,
        "ask_followup_question": handle_ask_followup_question,
        "web_search": handle_web_search,
        "download_url": handle_download_tool,
        "run_emu": handle_run_emu,
        "run_game": handle_run_game,
        "check_rom": handle_check_game_folder,
        "screenshot": handle_screenshot,
        "movement": handle_move
    }

    # Iterate over all tags and call the corresponding handler if available
    for tool_tag in soup.find_all():
        if tool_tag.name in handlers:
            handler_response = handlers[tool_tag.name](tool_tag)
            logging.info(f"Handler response: {handler_response}")
            if tool_tag.name == "attempt_completion" or tool_tag.name == "ask_followup_question":
                return handler_response, True
            else:
                return handler_response, False

    return get_no_tools_used_section(), False


def manage_system_message() -> str:
    return f"""
You are AetherPilot, an advanced gaming assistant with extensive knowledge of retro and modern games. You specialize in helping users find, set up, and play games using emulators. Your personality is friendly, enthusiastic about gaming, and technically knowledgeable.

## Your Capabilities:
- Finding and suggesting games based on user preferences
- Helping users set up emulators for different gaming platforms
- Checking if requested games are available in the user's library
- Running games through appropriate emulators
- Providing information about games, their history, and gameplay

## Guidelines for Interaction:
1. Be concise and direct in your responses, focusing on helping the user play games
2. When a user asks about a game, check if it exists in their library using similar name matching
3. If multiple games match a search query, present options clearly and ask the user to choose
4. Provide step-by-step instructions when helping with technical tasks
5. If a game isn't available, offer to help download it or suggest alternatives
6. Always prioritize user experience and getting them into gameplay quickly

## Technical Knowledge:
- You understand various emulator platforms (RetroArch, PCSX2, Dolphin, etc.)
- You're familiar with ROM formats and compatibility requirements
- You can troubleshoot common emulation issues
- You know how to optimize emulator settings for better performance

You have the following tools that can help you accomplish gaming tasks:
{get_tool_descriptions_for_mode("default")}
{getSharedToolUseSection()}
{getToolUseGuidelinesSection()}
{getObjectiveSection()}

Always return the response in XML-style tags, and ensure that all content is enclosed within appropriate XML tags.
Your goal is to provide helpful, accurate gaming assistance that gets users playing their favorite games with minimal friction.
"""


async def handle_message(message: str, tools: bool = False) -> str:

    messages = [
        SystemMessage(
            content=f"{manage_system_message()} \n\n ConversationHistory:{(conversation_history)}"),
        HumanMessage(
            content=f"Tools result: {message} \n\n The tools have been successfully executed. You can think about next step and proceed." if tools else message)
    ]
    # logging.info(f"Messages: {messages}")
    response = model.invoke(messages)

    if tools:
        conversation_history.append(f"Tools result: {message}")
    else:
        conversation_history.append(f"User: {message}")

    conversation_history.append(f"AI: {response.content}")

    return response.content


def main():
    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling()


if __name__ == '__main__':
    main()
