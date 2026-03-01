import io
from app.models.resume import ResumeData
from app.services.template_renderer import render_template

def generate_pdf(resume_data: ResumeData) -> bytes:
    """Generate a PDF from resume data using xhtml2pdf (no system deps required)."""
    try:
        from xhtml2pdf import pisa
    except ImportError:
        raise RuntimeError("PDF generation not available in this environment. Use the Download PDF button in the browser instead.")
    html_content = render_template(resume_data)
    # Add A4 page style wrapper
    full_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
    <style>@page {{ size: A4; margin: 15mm 15mm 15mm 15mm; }}</style>
    </head><body>{html_content}</body></html>"""
    output = io.BytesIO()
    result = pisa.CreatePDF(io.StringIO(full_html), dest=output)
    if result.err:
        raise RuntimeError(f"PDF generation failed: {result.err}")
    return output.getvalue()
