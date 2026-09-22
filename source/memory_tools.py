from google.adk.tools import ToolContext


def save_preference(
    key: str,
    value: str,
    tool_context: ToolContext,
) -> dict:
    """
    Store user preference.
    """

    tool_context.state[key] = value

    return {
        "status": "success",
        "key": key,
        "value": value
    }


def get_preference(
    key: str,
    tool_context: ToolContext,
) -> dict:
    """
    Retrieve stored preference.
    """

    value = tool_context.state.get(key)

    return {
        "status": "success",
        "key": key,
        "value": value
    }


def get_all_preferences(
    tool_context: ToolContext,
) -> dict:
    """
    Return complete memory.
    """

    return {
        "status": "success",
        "memory": dict(tool_context.state)
    }