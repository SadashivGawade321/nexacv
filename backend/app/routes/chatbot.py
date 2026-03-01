from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

GROQ_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"


class ChatMessage(BaseModel):
    role: str          # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    resume_context: Optional[str] = ""   # optional serialised resume data


SYSTEM_PROMPT = """You are NexaCV Assistant — a smart, friendly career coach and resume expert built into the NexaCV AI Resume Builder platform.

Your capabilities:
- Help users write, improve, and tailor their resumes
- Give ATS optimisation tips specific to a job description
- Advise on career transitions, interview preparation, and job search strategy
- Explain resume sections (summary, experience, skills, education, certifications, projects)
- Suggest strong action verbs, quantified achievements, and impactful phrasing
- Review or critique resume content shared in the chat

Personality:
- Concise, professional, and encouraging
- Use bullet points and short paragraphs for readability
- If the user shares their resume content you can suggest improvements inline
- Always stay on-topic (career, resumes, job search)
- If asked something unrelated, politely redirect to career topics

Never make up job titles, companies, or certifications. If you don't know something, say so."""


@router.post("/message")
async def chat(req: ChatRequest):
    if not GROQ_KEY or GROQ_KEY == "your-groq-api-key-here":
        raise HTTPException(status_code=503, detail="Groq API key not configured.")

    try:
        client = Groq(api_key=GROQ_KEY)

        system_content = SYSTEM_PROMPT
        if req.resume_context and len(req.resume_context.strip()) > 10:
            system_content += f"\n\nThe user's current resume data (JSON):\n{req.resume_context[:3000]}"

        messages = [{"role": "system", "content": system_content}]

        # Append conversation history (last 10 turns to stay within token limits)
        for msg in (req.history or [])[-10:]:
            messages.append({"role": msg.role, "content": msg.content})

        # Append the new user message
        messages.append({"role": "user", "content": req.message})

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=600,
        )

        reply = response.choices[0].message.content.strip()
        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
