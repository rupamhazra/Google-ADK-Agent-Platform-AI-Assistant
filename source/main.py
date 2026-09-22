import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent import root_agent

# ====================================================
# Load ENV
# ====================================================

load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("GOOGLE_API_KEY")

print(f"GOOGLE_API_KEY Loaded: {bool(api_key)}")

# ====================================================
# FastAPI
# ====================================================

app = FastAPI()

# ====================================================
# ADK Setup
# ====================================================

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name="fastapi-adk-app",
    session_service=session_service,
)


# ====================================================
# Models
# ====================================================

class ChatRequest(BaseModel):
    message: str


# ====================================================
# UI
# ====================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>

    <head>
        <title>ADK FastAPI Chat</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1000px;
                margin: 40px auto;
                padding: 20px;
            }

            h2 {
                margin-bottom: 20px;
            }

            textarea {
                width: 100%;
                height: 120px;
                padding: 10px;
                font-size: 16px;
            }

            button {
                margin-top: 15px;
                padding: 12px 24px;
                font-size: 16px;
                cursor: pointer;
            }

            #response {
                margin-top: 20px;
                border: 1px solid #ddd;
                background: #f5f5f5;
                padding: 15px;
                min-height: 100px;
                white-space: pre-wrap;
            }

            .error {
                color: red;
                font-weight: bold;
            }
        </style>

    </head>

    <body>

        <h2>ADK FastAPI Chat</h2>

        <textarea
            id="message"
            placeholder="Ask something..."></textarea>

        <br>

        <button onclick="sendMessage()">
            Send
        </button>

        <div id="response"></div>

        <script>

            async function sendMessage() {

                const message =
                    document.getElementById("message").value;

                const responseDiv =
                    document.getElementById("response");

                responseDiv.innerHTML = "Thinking...";

                try {

                    const response = await fetch("/chat", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            message: message
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        responseDiv.innerHTML = data.response;
                    }
                    else {
                        responseDiv.innerHTML =
                            `<div class="error">${data.error}</div>`;
                    }

                }
                catch (err) {

                    responseDiv.innerHTML =
                        `<div class="error">${err.message}</div>`;
                }
            }

        </script>

    </body>

    </html>
    """


# ====================================================
# Health Check
# ====================================================

@app.get("/health")
async def health():
    return {
        "api_key_loaded": bool(os.getenv("GOOGLE_API_KEY"))
    }


# ====================================================
# Chat API
# ====================================================

@app.post("/chat")
async def chat(req: ChatRequest):

    try:

        user_id = "user1"
        session_id = "session1"

        try:
            await session_service.create_session(
                app_name="fastapi-adk-app",
                user_id=user_id,
                session_id=session_id,
            )
        except Exception:
            pass

        content = types.Content(
            role="user",
            parts=[
                types.Part(text=req.message)
            ],
        )

        response_text = ""

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):

            if (
                hasattr(event, "content")
                and event.content
                and event.content.parts
            ):

                for part in event.content.parts:

                    if hasattr(part, "text") and part.text:
                        response_text += part.text

        if not response_text:
            response_text = "No response received from agent."

        return {
            "success": True,
            "response": response_text
        }

    except Exception as e:

        error_message = str(e)

        # Friendly Gemini quota message
        if "RESOURCE_EXHAUSTED" in error_message:
            error_message = (
                "🚫 Gemini API quota exceeded.\n\n"
                "Free-tier request limit reached.\n"
                "Please wait a few seconds/minutes and retry.\n"
                "Or upgrade your Gemini API billing plan."
            )

        elif "No API key was provided" in error_message:
            error_message = (
                "🚫 GOOGLE_API_KEY not found.\n"
                "Please check your .env file."
            )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": error_message
            },
        )


# ====================================================
# Run:
# uvicorn main:app --reload
# ====================================================