from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from app.models.resume import AIRequest
from app.services.ai_service import get_ai_suggestions, GROQ_MODEL

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

router = APIRouter()

@router.post("/improve")
async def improve_content(request: AIRequest):
    """Improve resume content using AI"""
    result = get_ai_suggestions(request.content, request.context, "improve")
    return result

@router.post("/keywords")
async def suggest_keywords(request: AIRequest):
    """Suggest keywords based on job description"""
    result = get_ai_suggestions(request.content, request.context, "keywords")
    return result

@router.post("/bullet-points")
async def improve_bullets(request: AIRequest):
    """Improve bullet points with action verbs and metrics"""
    result = get_ai_suggestions(request.content, request.context, "bullets")
    return result


class CoverLetterRequest(BaseModel):
    resume_data: dict
    job_title: str
    company: Optional[str] = ""
    tone: Optional[str] = "professional"   # professional | enthusiastic | concise


@router.post("/cover-letter")
async def generate_cover_letter(req: CoverLetterRequest):
    """Generate a tailored cover letter from resume data."""
    personal = req.resume_data.get("personal", {})
    name = personal.get("full_name", "the applicant")
    email = personal.get("email", "")
    phone = personal.get("phone", "")
    summary = personal.get("summary", "")

    experiences = req.resume_data.get("experience", [])
    exp_text = ""
    for exp in experiences[:3]:
        role = exp.get("role", exp.get("title", ""))
        company = exp.get("company", "")
        duration = f"{exp.get('start_date', '')} – {exp.get('end_date', 'Present')}"
        desc = exp.get("description", "")
        if role or company:
            exp_text += f"\n- {role} at {company} ({duration}): {desc[:200]}"

    skills = req.resume_data.get("skills", [])
    skills_text = ", ".join(
        [s.get("name", s) if isinstance(s, dict) else str(s) for s in skills[:12]]
    )

    tone_instruction = {
        "professional": "Write in a formal, polished, professional tone.",
        "enthusiastic": "Write in an energetic, enthusiastic, and passionate tone that conveys genuine excitement about the role.",
        "concise": "Write in a brief, clear, and direct tone — keep the letter under 250 words.",
    }.get(req.tone, "Write in a professional tone.")

    company_line = f" at {req.company}" if req.company else ""

    system_prompt = (
        "You are an expert career coach and professional cover letter writer. "
        "Generate polished, tailored cover letters that stand out to hiring managers."
    )

    user_prompt = f"""Write a complete, ready-to-send cover letter for {name} applying for the position of {req.job_title}{company_line}.

Applicant background:
- Summary: {summary or 'Not provided'}
- Experience: {exp_text or 'Not provided'}
- Skills: {skills_text or 'Not provided'}
- Contact: {email}, {phone}

Tone instruction: {tone_instruction}

Requirements:
- Include today's date at the top
- Address the hiring manager professionally (use "Hiring Manager" if company name is unknown)
- 3-4 focused paragraphs: opening hook, relevant experience, passion/fit, call to action
- End with a professional sign-off using the applicant's name
- Do NOT add any commentary or explanation outside the letter itself
- Output ONLY the cover letter text, nothing else
"""

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=900,
            temperature=0.72,
        )
        letter = response.choices[0].message.content.strip()
        return {"cover_letter": letter}
    except Exception as e:
        return {"error": str(e), "cover_letter": ""}
