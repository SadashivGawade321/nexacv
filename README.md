# Resume Builder - Quick Start

## Step 1: Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend will run at: http://localhost:8000
API Docs at: http://localhost:8000/docs

## Step 2: Frontend
Simply open in your browser:
- `frontend/login.html`   → Login / Register page (Three.js 3D)
- `frontend/index.html`   → Resume Builder dashboard

## Step 3: Optional — AI Features
Add your OpenAI key in `backend/.env`:
```
OPENAI_API_KEY=sk-your-key-here
```
Without the key, rule-based suggestions still work.

## Project Structure
```
resumebuilder/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point
│   │   ├── models/resume.py     ← Pydantic models
│   │   ├── routes/
│   │   │   ├── auth.py          ← Login/Register endpoints
│   │   │   ├── resume.py        ← Generate/Download endpoints
│   │   │   ├── ats.py           ← ATS Score endpoints
│   │   │   └── ai_suggestions.py← AI improvement endpoints
│   │   ├── services/
│   │   │   ├── auth_service.py  ← JWT + bcrypt auth
│   │   │   ├── ats_scorer.py    ← ATS scoring logic
│   │   │   ├── ai_service.py    ← OpenAI + fallback AI
│   │   │   ├── pdf_generator.py ← WeasyPrint PDF export
│   │   │   └── template_renderer.py
│   │   └── templates/
│   │       ├── modern.html      ← Sidebar template
│   │       ├── classic.html     ← Traditional template
│   │       └── minimal.html     ← Clean minimal template
│   ├── .env
│   └── requirements.txt
└── frontend/
    ├── login.html               ← Three.js 3D login page
    └── index.html               ← Full resume builder UI
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login + JWT |
| POST | /api/resume/generate | Get HTML preview |
| POST | /api/resume/download/pdf | Download PDF |
| GET  | /api/resume/templates | List templates |
| POST | /api/ats/check | ATS score |
| POST | /api/ats/analyze | Detailed ATS analysis |
| POST | /api/ai/improve | Improve text |
| POST | /api/ai/bullet-points | Rewrite bullets |
| POST | /api/ai/keywords | Extract keywords |
