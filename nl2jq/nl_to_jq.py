import json
import re
import spacy

# Load a pre-trained spaCy model (you might need to download one)
# python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

def generate_jq(natural_language_query, json_data):
    """
    Generates a jq expression from a natural language query against a given JSON document.

    Args:
        natural_language_query (str): The natural language query.
        json_data (str or dict): The JSON data as a string or a dictionary.

    Returns:
        str: The jq expression, or None if the query cannot be translated.
    """

    if isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return "Error: Invalid JSON data."
    elif isinstance(json_data, dict):
        data = json_data
    else:
        return "Error: Invalid json_data type.  Must be string or dict."

    doc = nlp(natural_language_query)

    jq_expression = ""

    # Simple keyword-based translation (expand as needed)
    for token in doc:
        if token.text.lower() == "name":
            jq_expression += ".name"
        elif token.text.lower() == "age":
            jq_expression += ".age"
        elif token.text.lower() == "address":
            jq_expression += ".address"
        elif token.text.lower() == "city":
            jq_expression += ".address.city"
        elif token.text.lower() == "country":
            jq_expression += ".address.country"
        elif token.text.lower() == "first":
            jq_expression = ".[] | first"  # Assuming array
        elif token.text.lower() == "last":
            jq_expression = ".[] | last"  # Assuming array
        elif token.text.lower() == "all":
            jq_expression = ".[]"  # Assuming array
        elif token.text.lower() == "filter" or token.text.lower() == "where":
            # This is a placeholder for more complex filtering logic
            # You'll need to parse the following tokens to build the filter condition
            jq_expression += " | select("
            # Example: "filter where age > 30"
            # You'd need to extract "age > 30" from the doc
            # This is where more sophisticated NLP is needed.
            pass
        elif token.text.lower() == "greater" or token.text.lower() == ">":
            jq_expression += ">"
        elif token.text.lower() == "less" or token.text.lower() == "<":
            jq_expression += "<"
        elif token.text.lower() == "equal" or token.text.lower() == "=":
            jq_expression += "=="
        elif token.text.lower() == "and":
            jq_expression += " and "
        elif token.text.lower() == "or":
            jq_expression += " or "
        elif token.text.lower() == "count":
            jq_expression = "length"
        elif token.text.lower() == "average":
            jq_expression = "map(.age) | add / length" # Example for age
        elif token.text.lower() == "sum":
            jq_expression = "map(.age) | add" # Example for age

    # Handle array access (e.g., "the second element")
    if "second" in natural_language_query.lower():
        jq_expression = ".[] | .[1]"

    if "third" in natural_language_query.lower():
        jq_expression = ".[] | .[2]"

    # Handle multiple levels of access
    if "of" in natural_language_query.lower():
        parts = natural_language_query.lower().split("of")
        jq_expression = "." + ".".join([part.strip() for part in parts])

    # Basic error handling
    if not jq_expression:
        return "Error: Could not translate the query."

    return jq_expression


def apply_jq(jq_expression, json_data):
    """
    Applies a jq expression to a JSON document.

    Args:
        jq_expression (str): The jq expression.
        json_data (str or dict): The JSON data as a string or a dictionary.

    Returns:
        str: The result of applying the jq expression, or None if there's an error.
    """
    try:
        import jq
    except ImportError:
        return "Error: jq library not installed.  Install with: pip install jq"

    if isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return "Error: Invalid JSON data."
    elif isinstance(json_data, dict):
        data = json_data
    else:
        return "Error: Invalid json_data type.  Must be string or dict."

    try:
        result = jq.compile(jq_expression).input(data).first()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error applying jq: {e}"


# Example Usage
if __name__ == "__main__":
    json_data = """
    [
      {
        "name": "Alice",
        "age": 30,
        "address": {
          "city": "New York",
          "country": "USA"
        }
      },
      {
        "name": "Bob",
        "age": 25,
        "address": {
          "city": "London",
          "country": "UK"
        }
      }
    ]
    """

    # Example queries
    queries = [
        "name",
        "age",
        "city",
        "country",
        "first",
        "last",
        "all",
        "filter where age > 28",
        "the second element",
        "name of address",
        "average age",
        "sum of age"
    ]

    for query in queries:
        jq_expression = generate_jq(query, json_data)
        print(f"Query: {query}")
        print(f"JQ Expression: {jq_expression}")

        if jq_expression:
            result = apply_jq(jq_expression, json_data)
            print(f"Result:\n{result}\n")
        else:
            print("Translation failed.\n")