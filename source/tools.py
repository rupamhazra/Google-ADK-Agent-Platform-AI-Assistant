import requests
import math
from datetime import datetime
# Tell me about Google Cloud and calculate 18% GST on 25000

def search_topic(topic: str) -> dict:
    """
    Search information about a topic.
    """

    try:
        url = "https://en.wikipedia.org/w/api.php"
        
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": topic,
            "redirects": "1",
        }
    
        response = requests.get(
            url,
            params=params,
            headers={
                "User-Agent": "ADK-Agent/1.0"
            }
        )
    
        data = response.json()
    
        page = next(iter(data["query"]["pages"].values()))
    
        return {
            "status": "success",
            "title": page.get("title"),
            "summary": page.get("extract")
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def calculator(expression: str) -> dict:
    """
    Evaluate a mathematical expression.
    """

    try:
        result = eval(
            expression,
            {
                "__builtins__": {},
                "math": math
            }
        )

        return {
            "status": "success",
            "result": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def current_time() -> dict:
    """
    Return current system time.
    """

    return {
        "status": "success",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# tools.py

def request_human_approval(action: str) -> dict:
    """
    Creates an approval request.
    """

    return {
        "status": "pending_approval",
        "action": action,
        "message": f"Human approval required for: {action}"
    }