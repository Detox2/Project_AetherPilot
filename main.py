import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from bs4 import BeautifulSoup
from tavily import TavilyClient

from prompts.tools.tools import get_tool_descriptions_for_mode
from prompts.sections.tool_use import getSharedToolUseSection
from prompts.sections.tool_use_guidelines import getToolUseGuidelinesSection
from prompts.sections.objective import getObjectiveSection
from prompts.sections.noToolsUsed import get_no_tools_used_section
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

telegram_token = "<PUT_YOUR_TELEGRAM_TOKEN_HERE>"
openrouter_api_key = "<PUT_YOUR_OPENROUTER_API_KEY_HERE>"
openrouter_base_url = "https://openrouter.ai/api/v1"
openrouter_model = "anthropic/claude-3.7-sonnet"
openrouter_temperature = 0.5
tavily_api_key = "<TAVILY_API_KEY_HERE>"
conversation_history = []

model = ChatOpenAI(api_key=openrouter_api_key, base_url=openrouter_base_url,
                   model=openrouter_model, temperature=openrouter_temperature)


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am your bot. How can I assist you?')


async def echo(update: Update, context: CallbackContext) -> None:
    logging.info(f'User message: {update.message.text}')

    # Loop until isFinished is true or maximum iterations reached
    max_iterations = 3
    iterations = 0
    isFinished = False
    isToolUsed = False
    tool_response = ""
    while not isFinished and iterations < max_iterations:
        next_step = await handle_message(update.message.text if not isToolUsed else tool_response, isToolUsed)
        logging.info(f"Next step: {next_step}")
        await update.message.reply_text(next_step) # This can be removed
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
You are a professional topic researcher.
You are given a message from user.
And you got those tools to help you to accomplish the task:
{get_tool_descriptions_for_mode("default", False)}
{getSharedToolUseSection()}
{getToolUseGuidelinesSection()}
{getObjectiveSection()}

Always return the response in XML-style tags, and ensure that all content is enclosed within appropriate XML tags.
Your final goal is to return short and concise research results to the user.
"""


async def handle_message(message: str, tools: bool = False) -> str:

    messages = [
        SystemMessage(
            content=f"{manage_system_message()} \n\n ConversationHistory:{(conversation_history)}"),
        HumanMessage(
            content=f"Tools result: {message} \n\n The tools have been successfully executed. You can think about next step and proceed." if tools else message)
    ]
    logging.info(f"Messages: {messages}")
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
