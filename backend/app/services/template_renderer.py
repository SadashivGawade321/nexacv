from app.models.resume import ResumeData
from jinja2 import Environment, FileSystemLoader
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_template(resume_data: ResumeData) -> str:
    """Render resume HTML from chosen template."""
    template_name = f"{resume_data.template}.html"
    try:
        template = env.get_template(template_name)
    except Exception:
        template = env.get_template("modern.html")
    return template.render(r=resume_data)
