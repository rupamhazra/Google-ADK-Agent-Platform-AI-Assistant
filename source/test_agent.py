import vertexai
from vertexai import agent_engines

vertexai.init(project="c11bffff-09d9-480a-a53", location="us-central1")
resource_name = "projects/509933330289/locations/us-central1/reasoningEngines/6038057714129567744"
remote_agent = agent_engines.get(resource_name)

prompt = "Tell me about Google Cloud and calculate 18% GST on 25000"
print(f"Sending request: {prompt}...\n")

# 1. Use stream_query instead of query
# 2. Change 'input' to 'message' and add 'user_id'
events = remote_agent.stream_query(
    message=prompt,
    user_id="test-user-1" 
)

print("Response from Agent Platform:\n")
for event in events:
    if isinstance(event, dict):
        # Extract parts from the content dictionary
        content = event.get("content")
        if isinstance(content, dict):
            for part in content.get("parts", []):
                if isinstance(part, dict) and "text" in part:
                    print(part["text"], end="", flush=True)
        elif isinstance(content, str):
            print(content, end="", flush=True)

print("\n")