import streamlit as st
import vertexai
from vertexai import agent_engines
import uuid
import json
import graphviz

# 1. Page Config
st.set_page_config(page_title="Corporate AI Assistant", layout="wide", initial_sidebar_state="collapsed")

# 2. Advanced Custom CSS for SVG Animations
custom_css = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stAppDeployButton {display: none;}
.stApp { background-color: #f8f9fa; }

.top-header {
    background-color: #ffffff;
    padding: 1rem 2rem;
    border-bottom: 1px solid #e5e7eb;
    margin-top: -4rem; 
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    color: #111827;
    font-weight: 600;
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.trace-header {
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e5e7eb;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.empty-state {
    text-align: center;
    padding: 6rem 2rem;
    color: #6b7280;
    background: #ffffff;
    border-radius: 12px;
    border: 1px dashed #d1d5db;
    margin-top: 2rem;
}

/* === ADK GRAPHVIZ ANIMATIONS === */
.stGraphVizChart svg .edge path {
    stroke-dasharray: 6;
    animation: flowData 0.8s linear infinite;
    stroke: #aecbfa !important;
    stroke-width: 1.5px;
}
@keyframes flowData {
    from { stroke-dashoffset: 12; }
    to { stroke-dashoffset: 0; }
}

.stGraphVizChart svg .node polygon[stroke-width="3"],
.stGraphVizChart svg .node path[stroke-width="3"] {
    animation: pulseActive 1.5s infinite;
}
@keyframes pulseActive {
    0% { filter: drop-shadow(0 0 2px rgba(66, 133, 244, 0.3)); }
    50% { filter: drop-shadow(0 0 12px rgba(66, 133, 244, 0.85)); }
    100% { filter: drop-shadow(0 0 2px rgba(66, 133, 244, 0.3)); }
}

.stGraphVizChart svg .node:hover polygon,
.stGraphVizChart svg .node:hover path {
    filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1));
    transform: translateY(-2px);
    transition: all 0.2s ease;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown('<div class="top-header">✦ Corporate AI Assistant</div>', unsafe_allow_html=True)

# 3. Dynamic Network Graph Builder (State-Machine Logic)
def build_trace_graph(trace_events, user_prompt="", is_generating=False):
    graph = graphviz.Digraph(engine="dot")
    graph.attr(rankdir="TB", bgcolor="transparent", nodesep="0.4", ranksep="0.5", margin="0")
    
    nodes = {}
    edges = []
    
    def add_node(n_id, label, fill, font, pw="1", border="#dadce0"):
        nodes[n_id] = {"label": label, "fillcolor": fill, "fontcolor": font, "penwidth": pw, "color": border}

    short_prompt = (user_prompt[:35] + '...') if len(user_prompt) > 35 else user_prompt
    add_node("User", f"👤 User Prompt\n'{short_prompt}'", "#f8f9fa", "#202124")
    add_node("coordinator_agent", "🤖 coordinator_agent", "#e8f0fe", "#1967d2")
    
    edges.append(("User", "coordinator_agent", "", "#bdc1c6"))
    
    current_node = "coordinator_agent"
    step = 1
    total_tokens = 0
    has_failed = False

    for event in trace_events:
        if not isinstance(event, dict): continue
        
        usage = event.get("usage_metadata") or event.get("usageMetadata")
        if usage:
            tokens = usage.get("totalTokenCount") or usage.get("total_token_count")
            if tokens: total_tokens = tokens
            
        if event.get("finish_reason") == "ERROR" or event.get("error"):
            has_failed = True

        author = event.get("author", "")
        
        # Intercept implicit author shifts to enforce Hub-and-Spoke routing
        if author and author != current_node and "agent" in author:
            if author not in nodes:
                add_node(author, f"🤖 {author}", "#e8f0fe", "#1967d2")
            
            edge_color = "#ea4335" if has_failed else "#bdc1c6"
            
            # If jumping from sub-agent to sub-agent, route through the coordinator visually
            if current_node != "coordinator_agent" and author != "coordinator_agent":
                edges.append((current_node, "coordinator_agent", f"Step {step}", edge_color))
                step += 1
                edges.append(("coordinator_agent", author, f"Step {step}", edge_color))
                step += 1
            else:
                edges.append((current_node, author, f"Step {step}", edge_color))
                step += 1
            current_node = author

        content = event.get("content", {})
        if isinstance(content, dict):
            for part in content.get("parts", []):
                if not isinstance(part, dict): continue
                
                if "function_call" in part:
                    func = part["function_call"]
                    name = func.get("name")
                    args = func.get("args", {})
                    
                    if name == "transfer_to_agent":
                        target = args.get("agent_name", "sub_agent")
                        if target not in nodes:
                            add_node(target, f"🤖 {target}", "#e8f0fe", "#1967d2")
                        
                        # Intercept explicit transfer tool calls to enforce Hub-and-Spoke routing
                        if current_node != "coordinator_agent" and target != "coordinator_agent":
                            edges.append((current_node, "coordinator_agent", f"Step {step}", "#bdc1c6"))
                            step += 1
                            edges.append(("coordinator_agent", target, f"Step {step}", "#bdc1c6"))
                            step += 1
                        else:
                            edges.append((current_node, target, f"Step {step}", "#bdc1c6"))
                            step += 1
                        current_node = target
                    else:
                        # Add the step counter to the ID so duplicate tool calls don't overlap in the graph
                        tool_id = f"tool_{name}_{step}"
                        args_str = str(args)
                        args_str = (args_str[:40] + '...') if len(args_str) > 40 else args_str
                        
                        add_node(tool_id, f"🛠️ Tool: {name}\n{args_str}", "#fef7e0", "#b06000")
                            
                        edge_color = "#ea4335" if has_failed else "#bdc1c6"
                        edges.append((current_node, tool_id, f"Step {step}", edge_color))
                        edges.append((tool_id, current_node, f"Step {step+1}", edge_color))
                        step += 2

    # Final Graph Lock Generation
    if not is_generating and trace_events:
        token_str = f"\nTotal Tokens: {total_tokens}" if total_tokens else ""
        status_str = "\n❌ FAILED" if has_failed else ""
        
        fill = "#fce8e6" if has_failed else "#e6f4ea"
        font = "#c5221f" if has_failed else "#137333"
        edge_color = "#ea4335" if has_failed else "#bdc1c6"
        
        # Ensure the final response ALWAYS originates from the coordinator node
        if current_node != "coordinator_agent":
            edges.append((current_node, "coordinator_agent", f"Step {step}", edge_color))
            step += 1
            current_node = "coordinator_agent"
        
        add_node("final_response", f"📝 Final Response{token_str}{status_str}", fill, font)
        edges.append((current_node, "final_response", f"Step {step}", edge_color))

    # Compile Graph
    for n_id, attrs in nodes.items():
        is_active = is_generating and (n_id == current_node)
        pw = "3" if is_active else attrs.get("penwidth", "1")
        border = "#4285F4" if is_active else attrs.get("color", "#dadce0")
        
        graph.node(n_id, attrs["label"], style="filled,rounded", shape="box",
                   fillcolor=attrs["fillcolor"], fontcolor=attrs["fontcolor"],
                   color=border, penwidth=pw, fontname="Arial, sans-serif", fontsize="12", margin="0.2,0.15")
        
    for e in edges:
        graph.edge(e[0], e[1], label=e[2], color=e[3], fontcolor="#9aa0a6", fontsize="10", arrowsize="0.6")
        
    return graph

# 4. Initialize Vertex AI
@st.cache_resource
def init_agent():
    vertexai.init(project="project-c11bffff-09d9-480a-a53", location="us-central1")
    resource = "projects/509933330289/locations/us-central1/reasoningEngines/4394707844046258176"
    return agent_engines.get(resource)

remote_agent = init_agent()

# --- AGENT ENGINE SESSION AND CHAT-HISTORY PERSISTENCE ---
def get_value(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def extract_session_id(session):
    session_id = get_value(session, "id") or get_value(session, "session_id")
    name = get_value(session, "name")
    if not session_id and name:
        session_id = str(name).rstrip("/").split("/")[-1]
    return session_id


def create_agent_session(user_id):
    created_session = remote_agent.create_session(user_id=user_id)
    created_session_id = extract_session_id(created_session)
    if not created_session_id:
        raise ValueError(f"Agent Engine returned no session ID: {created_session}")
    return created_session_id


def extract_session_events(session):
    return list(get_value(session, "events", []) or [])


def extract_text_from_content(content):
    if not content:
        return ""
    if isinstance(content, str):
        return content
    texts = []
    for part in get_value(content, "parts", []) or []:
        value = get_value(part, "text")
        if value:
            texts.append(str(value))
    return "".join(texts).strip()


def normalize_event_for_trace(event):
    if isinstance(event, dict):
        return event
    if hasattr(event, "model_dump"):
        return event.model_dump(mode="json", exclude_none=True)
    if hasattr(event, "to_dict"):
        return event.to_dict()
    content = get_value(event, "content")
    return {
        "author": get_value(event, "author", ""),
        "content": {
            "role": get_value(content, "role", ""),
            "parts": [{"text": extract_text_from_content(content)}],
        },
    }


def restore_messages_from_session(session):
    messages = []
    for raw_event in extract_session_events(session):
        event = normalize_event_for_trace(raw_event)
        content = event.get("content")
        text = extract_text_from_content(content)
        if not text:
            continue
        role = get_value(content, "role", "")
        author = event.get("author", "")
        if role == "user":
            chat_role = "user"
        elif role == "model" or author:
            chat_role = "assistant"
        else:
            continue
        if messages and chat_role == "assistant" and messages[-1]["role"] == "assistant":
            messages[-1]["content"] += text
        else:
            messages.append({"role": chat_role, "content": text})
    return messages


url_user_id = st.query_params.get("user_id")
url_session_id = st.query_params.get("session_id")
restored_agent_session = None

if "user_id" not in st.session_state:
    st.session_state.user_id = url_user_id or f"streamlit-user-{uuid.uuid4()}"

if "session_id" not in st.session_state:
    if url_user_id and url_session_id:
        try:
            restored_agent_session = remote_agent.get_session(
                user_id=st.session_state.user_id,
                session_id=url_session_id,
            )
            st.session_state.session_id = url_session_id
        except Exception as exc:
            print(f"Unable to restore URL session; creating a new one: {exc}")
            try:
                st.session_state.session_id = create_agent_session(st.session_state.user_id)
            except Exception as create_exc:
                st.error(f"Unable to create Agent Engine session: {create_exc}")
                st.stop()
    else:
        try:
            st.session_state.session_id = create_agent_session(st.session_state.user_id)
        except Exception as exc:
            st.error(f"Unable to create Agent Engine session: {exc}")
            st.stop()
elif "messages" not in st.session_state:
    try:
        restored_agent_session = remote_agent.get_session(
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
        )
    except Exception as exc:
        print(f"Unable to reload Agent Engine session: {exc}")

if "messages" not in st.session_state:
    st.session_state.messages = (
        restore_messages_from_session(restored_agent_session)
        if restored_agent_session else []
    )

if "trace_logs" not in st.session_state:
    restored_events = (
        [normalize_event_for_trace(e) for e in extract_session_events(restored_agent_session)]
        if restored_agent_session else []
    )
    st.session_state.trace_logs = [restored_events] if restored_events else []

st.query_params["user_id"] = st.session_state.user_id
st.query_params["session_id"] = st.session_state.session_id
# ---------------------------------------------------------

# 5. UI Layout
chat_col, gap, trace_col = st.columns([5, 0.5, 4])

with chat_col:
    if not st.session_state.messages:
        st.markdown(f'''
            <div class="empty-state">
                <h2>👋 Welcome to the Agent Workspace</h2>
                <p>Submit a query below to stream the response and view the cyclic execution trace.</p>
                <p style="font-size: 0.9em; color: #9ca3af;">
                    User ID: {st.session_state.user_id}<br>
                    Session ID: {st.session_state.session_id}
                </p>
            </div>
        ''', unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            avatar = "👤" if msg["role"] == "user" else "✨"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

with trace_col:
    st.markdown('<div class="trace-header">⚙️ Agent Flow Graph</div>', unsafe_allow_html=True)
    
    # Slightly reduced height to make room for the detailed log button below
    trace_container = st.container(height=580, border=True)
    graph_placeholder = trace_container.empty()
    
    # Placeholder for the button that opens the floating log window
    log_button_placeholder = st.empty()
    
    if st.session_state.trace_logs:
        last_prompt = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else "User Prompt"
        graph = build_trace_graph(st.session_state.trace_logs[-1], last_prompt, is_generating=False)
        graph_placeholder.graphviz_chart(graph, use_container_width=True)
        
        # Render the button for previous chat states
        with log_button_placeholder.popover("🔍 View Detailed Raw Logs", use_container_width=True):
            st.code(json.dumps(st.session_state.trace_logs[-1], indent=2, default=str), language="json")

# 6. Core Chat Logic
if prompt := st.chat_input("Ask a research or math question..."):
    # INSTANT CLEAR: Wipe the previous graph and button immediately
    graph_placeholder.empty()
    log_button_placeholder.empty()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with chat_col:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="✨"):
            message_placeholder = st.empty()
            full_response = ""
            current_trace = []
            
            with st.spinner("Agent network is reasoning and executing tools..."):
                events = remote_agent.stream_query(
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.session_id,
                    message=prompt,
                )

                for event in events:
                    normalized_event = normalize_event_for_trace(event)
                    current_trace.append(normalized_event)

                    with graph_placeholder:
                        graph = build_trace_graph(current_trace, prompt, is_generating=True)
                        st.graphviz_chart(graph, use_container_width=True)

                    chunk_text = ""
                    content = normalized_event.get("content")
                    if isinstance(content, dict):
                        for part in content.get("parts", []):
                            if isinstance(part, dict) and part.get("text"):
                                chunk_text += str(part["text"])
                    elif isinstance(content, str):
                        chunk_text += content

                    if not chunk_text and normalized_event.get("text"):
                        chunk_text += str(normalized_event["text"])

                    if chunk_text:
                        full_response += chunk_text
                        message_placeholder.markdown(full_response + "▌")

            if not full_response.strip():
                full_response = "*(Task completed. The agent executed its flow but did not return a final text summary. Please refer to the trace graph for execution details.)*"
                
            message_placeholder.markdown(full_response)
            
            with graph_placeholder:
                graph = build_trace_graph(current_trace, prompt, is_generating=False)
                st.graphviz_chart(graph, use_container_width=True)
                
            # Once generation is complete, generate the clickable popover button
            with log_button_placeholder.popover("🔍 View Detailed Raw Logs", use_container_width=True):
                st.code(json.dumps(current_trace, indent=2, default=str), language="json")
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.trace_logs.append(current_trace)