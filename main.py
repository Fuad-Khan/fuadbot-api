from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import requests
import os

# Load .env for local dev
load_dotenv()

app = FastAPI(
    title="FuadBot API",
    description="Backend for FuadBot using Groq LLaMA 3",
    version="1.0.0",
)

# CORS (allow all for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class ErrorResponse(BaseModel):
    error: str


def debug_log(*args):
    if os.getenv("ENV", "development") != "production":
        print(*args)


# Load system prompt
BASE_DIR = Path(__file__).resolve().parent
system_prompt_path = BASE_DIR / "prompt" / "systemPrompt.txt"

try:
    SYSTEM_PROMPT = system_prompt_path.read_text(encoding="utf-8")
except FileNotFoundError:
    print("⚠️ systemPrompt.txt not found, using fallback system prompt.")
    SYSTEM_PROMPT = "You are a helpful, concise AI assistant."


GROQ_API_KEY = os.getenv("GROQ_API_KEY")


@app.get("/")
def root():
    return {"message": "FuadBot API is running 🚀"}


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
def chat(body: ChatRequest):
    if not body.message or len(body.message) > 2000:
        raise HTTPException(status_code=400, detail="Invalid or too long message input.")

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Server misconfigured: GROQ_API_KEY missing.")

    user_message = body.message.strip()
    clean_msg = user_message.lower()
    debug_log("🛎️ Received message:", user_message)

    # Special case
    if "tell about me" in clean_msg:
        return ChatResponse(
            reply="Do you want me to tell you about Fuad Khan or about yourself? I can only provide info about Fuad Khan."
        )

    today = datetime.now().strftime("%d %B %Y")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": f"{SYSTEM_PROMPT}\n\n📅 Today's Date: {today}",
            },
            {
                "role": "user",
                "content": f"{user_message} (Answer briefly and only what is asked.)",
            },
        ],
        "max_tokens": 400,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request timed out.")
    except requests.exceptions.RequestException as e:
        debug_log("🔥 Groq API call failed:", str(e))
        raise HTTPException(status_code=500, detail="Groq API call failed.")

    if not resp.ok:
        try:
            error_data = resp.json()
        except ValueError:
            error_data = {}

        debug_log("❌ API Error Response:", error_data)
        err_msg = (error_data.get("error") or {}).get("message", "")

        if "rate limit" in err_msg.lower():
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

        raise HTTPException(status_code=500, detail=err_msg or "API error.")

    data = resp.json()
    debug_log("✅ API response:", data)

    choices = data.get("choices") or []
    if not choices:
        raise HTTPException(status_code=500, detail="No reply from model.")

    reply_text = choices[0]["message"]["content"]
    return ChatResponse(reply=reply_text)


@app.post("/reset")
def reset():
    print("🔄 Manual reset triggered.")
    return "Reset done"
