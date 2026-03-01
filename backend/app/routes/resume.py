from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from app.models.resume import ResumeData
from app.services.pdf_generator import generate_pdf
from app.services.template_renderer import render_template
import io

router = APIRouter()

@router.post("/generate")
async def generate_resume(resume_data: ResumeData):
    """Generate resume HTML preview"""
    html_content = render_template(resume_data)
    return {"html": html_content}

@router.post("/download/pdf")
async def download_pdf(resume_data: ResumeData):
    """Generate and download PDF"""
    pdf_bytes = generate_pdf(resume_data)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={resume_data.full_name.replace(' ', '_')}_resume.pdf"
        }
    )

@router.get("/templates")
async def get_templates():
    """Get available resume templates"""
    return {
        "templates": [
            {"id": "modern",    "name": "Modern Sidebar",     "description": "Two-column with a coloured sidebar",       "category": "professional"},
            {"id": "classic",   "name": "Classic Professional","description": "Traditional single-column serif layout",   "category": "professional"},
            {"id": "minimal",   "name": "Minimal Clean",       "description": "Simple Helvetica with pill skill tags",    "category": "minimal"},
            {"id": "creative",  "name": "Creative Bold",       "description": "Vibrant header with skill progress bars",  "category": "creative"},
            {"id": "executive", "name": "Executive",           "description": "Formal serif with horizontal rule dividers","category": "professional"},
            {"id": "tech",      "name": "Tech Dark",           "description": "Dark theme with neon accent for devs",     "category": "creative"},
            {"id": "elegant",   "name": "Elegant Serif",       "description": "Warm tones, ornamental dividers",          "category": "minimal"},
            {"id": "compact",   "name": "Compact",             "description": "Space-efficient two-column layout",        "category": "professional"},
        ]
    }
