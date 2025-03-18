import openai
import json
import re
import subprocess

def natural_language_to_jq(natural_language_query, json_data, openai_api_key):
    """
    Converts a natural language query to a jq filter against a given JSON document.

    Args:
        natural_language_query: The natural language query (string).
        json_data: The JSON data (string or dict).
        openai_api_key: Your OpenAI API key.

    Returns:
        A tuple: (jq_filter, result, error_message).
        - jq_filter: The generated jq filter (string), or None if an error occurred.
        - result: The result of applying the jq filter to the JSON data, or None if an error.
        - error_message:  An error message (string), or None if no error occurred.
    """

    openai.api_key = openai_api_key

    # 1. Prepare the prompt for OpenAI
    if isinstance(json_data, str):
        try:
            json_object = json.loads(json_data)  # Try parsing if it's a string
        except json.JSONDecodeError:
            return None, None, "Invalid JSON data provided."
    elif isinstance(json_data, dict):
        json_object = json_data  # Use directly if already a dict
    else:
        return None, None, "json_data must be a string or a dictionary."


    prompt = f"""
You are a helpful assistant that translates natural language queries into jq filters.  You are given a JSON document and a natural language query.  Your task is to generate a valid jq filter that extracts the information requested in the natural language query.

Do *NOT* provide any additional text, explanations or apologies. Only provide the valid jq program.  If the query is ambiguous or cannot be converted to jq, return '.'.

JSON Document:
```json
{json.dumps(json_object, indent=2)}