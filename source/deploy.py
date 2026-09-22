import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp

# Import your agent instance from your agent.py file
from agent import root_agent as agent # <-- Ensure the variable name matches your agent in agent.py

# Using the project ID visible in your terminal
vertexai.init(
    project="project-c11bffff-09d9-480a-a53", 
    location="us-central1",
    staging_bucket="gs://adk-agent-staging-c11bffff"
    )

# Wrap the agent for deployment
app = AdkApp(agent=agent,enable_tracing=True)

telemetry_env_vars = {
                "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
                "OTEL_SEMCONV_STABILITY_OPT_IN": (
                "gen_ai_latest_experimental"
                ),
                "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": (
                "EVENT_ONLY"
                ),
            }

# Deploy to Agent Platform
agent_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-adk",
        "google-cloud-aiplatform[agent_engines,adk]",
        "requests",
        "cloudpickle",
        "google-cloud-logging",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-exporter-otlp-proto-grpc",
    ],
    extra_packages=["tools.py"],
    display_name="Corporate-AI-Assistant-v1",
    description=(
        "Tracing-enabled corporate multi-agent assistant "
        "with sub-agents and tools."
    ),
    env_vars=telemetry_env_vars,
    
)
print(f"Deployed Agent: {agent_app.resource_name}")

