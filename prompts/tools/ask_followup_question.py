
def get_ask_followup_question_description() -> str:
    return f"""
## ask_followup_question
Description: This tool is used to ask the user for additional information. It is typically invoked when the user's request is not clear or when more information is needed to proceed with the task. The response can include any relevant information or feedback based on the user's initial query.
Parameters:
- question: (required) The question to be asked to the user.
Usage:
<ask_followup_question>
<question>What is the name of the project?</question>
</ask_followup_question>
"""
