from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.resume import ATSCheckRequest
from app.services.ats_scorer import calculate_ats_score, calculate_ats_score_from_text
from app.services.resume_file_parser import extract_text_from_file

router = APIRouter()

@router.post("/check")
async def check_ats_score(request: ATSCheckRequest):
    """Calculate ATS score for resume against job description"""
    result = calculate_ats_score(request.resume_data, request.job_description)
    return result


@router.post("/check-uploaded")
async def check_uploaded_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Upload an existing resume file (PDF / DOCX / TXT) and get a
    high-accuracy ATS score powered by Groq AI semantic analysis.
    """
    allowed = {".pdf", ".docx", ".txt", ".doc"}
    filename = (file.filename or "").lower()
    if not any(filename.endswith(ext) for ext in allowed):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF, DOCX, or TXT file.",
        )

    resume_text = await extract_text_from_file(file)

    if not resume_text or len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Could not extract enough text from the file. "
                   "Try a different format or copy-paste your resume as text.",
        )

    result = calculate_ats_score_from_text(resume_text, job_description)
    result["resume_text_preview"] = resume_text[:500]   # handy for debugging
    return result


@router.post("/analyze")
async def analyze_resume(request: ATSCheckRequest):
    """Detailed ATS analysis with suggestions"""
    score_result = calculate_ats_score(request.resume_data, request.job_description)
    
    suggestions = []
    
    if score_result["keyword_match"] < 50:
        suggestions.append({
            "type": "keywords",
            "severity": "high",
            "message": "Your resume is missing many important keywords from the job description.",
            "action": "Add more relevant skills and keywords from the job posting."
        })
    
    if score_result["section_score"] < 80:
        suggestions.append({
            "type": "sections",
            "severity": "medium",
            "message": "Some important resume sections are incomplete.",
            "action": "Make sure to fill out all sections including summary, skills, and achievements."
        })
    
    if score_result["format_score"] < 90:
        suggestions.append({
            "type": "format",
            "severity": "low",
            "message": "Resume formatting could be improved for better ATS compatibility.",
            "action": "Use simple formatting without tables, graphics, or special characters."
        })
    
    return {
        **score_result,
        "suggestions": suggestions
    }
