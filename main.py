print("🚀 JusticeBot FastAPI server started!")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend URL
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

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Change to "gpt-4" if needed
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )

        full_response = response.choices[0].message["content"]

        return JSONResponse(
            content={"answer": full_response.strip()},
            media_type="application/json; charset=utf-8"
        )

    except Exception as e:
        print("🔥 OpenAI ERROR:", e)
        return JSONResponse(
            content={"answer": f"❌ Error: {str(e)}"},
            media_type="application/json"
        )
