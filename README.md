# 🤖 Corporate AI Assistant

An enterprise-grade **Agentic AI Assistant** built with **Google Agent Development Kit (ADK)** and deployed on **Vertex AI Agent Platform**. The solution leverages a multi-agent architecture with specialized agents for research and analysis, provides conversational memory through **VertexAISessionService**, and is accessible through both a **Streamlit web application** and **Gemini Enterprise**.

---

## 🚀 Project Highlights

- Built using Google Agent Development Kit (ADK)
- Multi-agent architecture with Research Agent and Analytical Agent
- Integrated 2 custom ADK tools
- Deployed to Vertex AI Agent Platform
- Streamlit-based chatbot UI
- Frontend deployed on Cloud Run
- Chat history and session persistence using VertexAISessionService
- Registered with Gemini Enterprise for enterprise-wide access

---

## 🏗️ Architecture

```text
End User
   |
Streamlit UI (Cloud Run)
   |
Vertex AI Agent Platform
   |
Main Agent
   |------------------|
   |                  |
Research Agent   Analytical Agent
   |                  |
   +---------+--------+
             |
        Tool 1 & Tool 2
             |
VertexAISessionService
             |
    Gemini Enterprise
```

---

## 📂 Project Structure

```text
recovered-adk-agent/
│
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── source/
    ├── __init__.py
    ├── agent.py
    ├── main.py
    ├── deploy.py
    ├── tools.py
    ├── memory_tools.py
    ├── test_agent.py
    ├── Dockerfile
    └── requirements.txt
```

---

## 🤖 Multi-Agent Design

### Main Agent
- Routes user requests
- Selects the appropriate sub-agent
- Invokes tools
- Aggregates responses

### Research Agent
- Information gathering
- Knowledge discovery
- Context generation
- Research-oriented tasks

### Analytical Agent
- Reasoning and analysis
- Summarization
- Comparative insights
- Decision support

---

## ☁️ Deployment

### Vertex AI Agent Platform
- Managed hosting
- Auto-scaling
- Monitoring and observability
- Enterprise-grade security

### Cloud Run
- Hosts Streamlit UI
- Automatic scaling
- HTTPS access
- Cost-efficient deployment

---

## 💬 Session Management

Using **VertexAISessionService** to:
- Persist conversations
- Maintain chat history
- Support multi-turn interactions
- Enable context-aware responses

---

## 🌟 Gemini Enterprise Integration

The deployed agent is registered in Gemini Enterprise, enabling:
- Enterprise-wide access
- Agent discoverability
- Governance and security controls
- Centralized AI experience

---

## 🛠 Technology Stack

- Google ADK
- Gemini Models
- Vertex AI Agent Platform
- VertexAISessionService
- Streamlit
- Cloud Run
- Docker
- Python
- Google Cloud Platform (GCP)

---

## ✅ Key Achievements

- Built Corporate AI Assistant using Google ADK
- Implemented Research Agent and Analytical Agent
- Integrated 2 custom tools
- Deployed on Vertex AI Agent Platform
- Developed Streamlit UI and deployed on Cloud Run
- Implemented persistent chat memory
- Registered in Gemini Enterprise

---

## 📌 Summary

Corporate AI Assistant demonstrates an end-to-end Agentic AI implementation using Google ADK, Vertex AI Agent Platform, Cloud Run, VertexAISessionService, and Gemini Enterprise, providing a scalable and enterprise-ready AI assistant solution.
