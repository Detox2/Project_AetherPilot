def get_web_search_description() -> str:
    return f"""
## web_search
Description: This tool is used to search the web for information.
Parameters:
- query: (required) The query to search the web for.

Usage:
<web_search>
<query>
What is the capital of France?
</query>
</web_search>
"""
