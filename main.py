print("Script started!")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import json

app = FastAPI()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question", "").strip()

    if not question:
        return JSONResponse(
            content={"answer": "❌ Please provide a valid legal question."},
            status_code=400
        )

    system_prompt = (
        "You are JusticeBot — a modern legal assistant for Indian citizens. "
        "Only provide legal guidance based on current Indian law, including:\n"
        "1. Bharatiya Nyaya Sanhita (BNS), 2023\n"
        "2. Bharatiya Nagarik Suraksha Sanhita\n"
        "3. Bharatiya Sakshya Adhiniyam\n\n"
        "Do not refer to outdated laws like IPC or ancient texts unless explicitly asked. "
        "Avoid Hinglish or mixed-language replies. Keep it clear, formal, and legally accurate."
    )

    # Payload for LLaMA3 via Ollama
    payload = {
        "model": "llama3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    }

    try:
        res = requests.post("http://localhost:11434/api/chat", json=payload, stream=True)
        full_response = ""

        for line in res.iter_lines():
            if line:
                try:
                    json_data = json.loads(line.decode("utf-8"))
                    full_response += json_data.get("message", {}).get("content", "")
                except json.JSONDecodeError:
                    continue  # skip malformed chunks

        return JSONResponse(
            content={"answer": full_response.strip()},
            media_type="application/json; charset=utf-8"
        )

    except Exception as e:
        print("🔥 Ollama ERROR:", e)
        return JSONResponse(
            content={"answer": f"❌ Error: {str(e)}"},
            media_type="application/json"
        )
