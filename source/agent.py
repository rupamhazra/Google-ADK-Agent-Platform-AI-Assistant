from google.adk.agents import Agent
from tools import (
    search_topic,
    calculator,
    request_human_approval
)

# --------------------------------------------------
# RESEARCH AGENT
# --------------------------------------------------
research_agent = Agent(
    name="research_agent",
    model="gemini-2.5-flash",
    description="Research specialist",
    instruction="""
    You are a research specialist. Focus exclusively on researching topics, explaining concepts, and summarizing information.

    Your mandatory workflow:
    1. Use the search_topic tool to gather external knowledge for the user's query.
    2. Write a detailed text summary of your findings based on the tool's output.
    3. Use the transfer_to_agent tool to transfer control back to the coordinator_agent.
    """,
    tools=[
        search_topic
    ]
)

# --------------------------------------------------
# ANALYTICS AGENT
# --------------------------------------------------
analytics_agent = Agent(
    name="analytics_agent",
    model="gemini-2.5-flash",
    description="Analytics specialist",
    instruction="""
    You are an analytics and mathematics specialist. Focus exclusively on numerical equations and data processing.

    Your mandatory workflow:
    1. Use the calculator tool to evaluate mathematical expressions.
    2. Write a clear text explanation of the calculated result.
    3. Use the transfer_to_agent tool to transfer control back to the coordinator_agent.
    """,
    tools=[
        calculator
    ]
)

# --------------------------------------------------
# APPROVAL AGENT
# --------------------------------------------------
approval_agent = Agent(
    model="gemini-2.5-flash",
    name="approval_agent",
    description="Handles human approval workflows.",
    instruction="""
    Request human approval before executing actions that impact systems, finances, or external users. Wait for explicit confirmation before proceeding.
    """,
    tools=[
        request_human_approval
    ]
)

# --------------------------------------------------
# ROOT COORDINATOR
# --------------------------------------------------
root_agent = Agent(
    name="coordinator_agent",
    model="gemini-2.5-flash",
    description="Main orchestration agent",
    instruction="""
    You are the central orchestration coordinator. Process user requests by delegating tasks to your specialist sub-agents.

    For single-topic queries:
    - Transfer research questions to the research_agent.
    - Transfer math questions to the analytics_agent.

    For multi-part queries (e.g., both research and calculation):
    Process the tasks sequentially to ensure all specialists contribute:
    1. First, transfer the research portion to the research_agent.
    2. Wait for the research_agent to return control to you.
    3. Second, transfer the calculation portion to the analytics_agent.
    4. Wait for the analytics_agent to return control to you.
    5. Finally, combine all findings into a complete, formatted response for the user.
    """,
    sub_agents=[
        research_agent,
        analytics_agent,
        approval_agent
    ]
)