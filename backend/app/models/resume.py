from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: str
    gpa: Optional[str] = None
    description: Optional[str] = None

class Experience(BaseModel):
    company: str
    position: str
    location: str
    start_date: str
    end_date: str
    is_current: bool = False
    description: str
    achievements: List[str] = []

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = []
    link: Optional[str] = None

class Certification(BaseModel):
    name: str
    issuer: str
    date: str
    link: Optional[str] = None

class ResumeData(BaseModel):
    # Personal Info
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    summary: Optional[str] = None
    
    # Sections
    education: List[Education] = []
    experience: List[Experience] = []
    skills: List[str] = []
    projects: List[Project] = []
    certifications: List[Certification] = []
    languages: List[str] = []
    
    # Template settings
    template: str = "modern"
    primary_color: str = "#2563eb"

class ATSCheckRequest(BaseModel):
    resume_data: ResumeData
    job_description: str

class AIRequest(BaseModel):
    content: str
    context: str = "resume"
    action: str = "improve"  # improve, suggest_keywords, fix_grammar
