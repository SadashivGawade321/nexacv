import os
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"


def get_ai_suggestions(content: str, context: str = "resume", action: str = "improve") -> dict:
    """
    Get AI suggestions using Groq API (llama3-8b-8192).
    Falls back to rule-based suggestions if no API key is set.
    """
    if GROQ_KEY and GROQ_KEY != "your-groq-api-key-here":
        return _groq_suggestions(content, context, action)
    return _rule_based_suggestions(content, action)


def _groq_suggestions(content: str, context: str, action: str) -> dict:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_KEY)

        prompts = {
            "improve": f"""You are an expert resume writer and career coach.
Improve the following resume content to make it more impactful, professional, and ATS-friendly.
Use strong action verbs, quantify achievements where possible, and be concise.

Content: {content}

Return ONLY valid JSON (no markdown, no code fences) with:
- "improved": the rewritten content
- "tips": list of 3 specific tips applied
""",
            "bullets": f"""You are an expert resume writer.
Rewrite the following experience description into 3-5 powerful bullet points.
Each bullet must start with a strong action verb and include quantifiable results.

Description: {content}

Return ONLY valid JSON (no markdown, no code fences) with:
- "bullets": list of improved bullet point strings
- "tips": list of 2 tips
""",
            "keywords": f"""You are an ATS and recruitment expert.
Given this job description or content, extract the top 15 most important ATS keywords.

Content: {content}

Return ONLY valid JSON (no markdown, no code fences) with:
- "keywords": list of 15 keyword strings
- "categories": dict grouping keywords by type (technical, soft_skills, tools, etc.)
""",
        }

        prompt = prompts.get(action, prompts["improve"])
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=700,
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        return json.loads(raw)

    except json.JSONDecodeError:
        return _rule_based_suggestions(content, action)
    except Exception as e:
        return {"error": str(e), **_rule_based_suggestions(content, action)}


def _rule_based_suggestions(content: str, action: str) -> dict:
    """Fallback rule-based suggestions when no Groq key is set."""
    WEAK_VERBS   = ["did", "made", "worked", "helped", "was responsible for", "assisted"]
    STRONG_VERBS = ["Engineered", "Spearheaded", "Architected", "Delivered",
                    "Optimized", "Accelerated", "Transformed", "Championed",
                    "Scaled", "Automated", "Reduced", "Increased"]
    TIPS = [
        "Start each bullet with a strong action verb (Led, Built, Increased, Reduced).",
        "Quantify results — e.g., 'Reduced load time by 40%' instead of vague claims.",
        "Mirror keywords directly from the job description.",
        "Keep each bullet under 2 lines for ATS readability.",
        "Use industry-specific terminology relevant to the role.",
    ]

    if action == "keywords":
        import re
        words = list(dict.fromkeys(re.findall(r'\b[a-zA-Z]{5,}\b', content)))[:15]
        return {
            "keywords": words,
            "categories": {"general": words},
            "note": "Set GROQ_API_KEY in .env for smarter keyword extraction."
        }

    if action == "bullets":
        sentences = [s.strip() for s in content.replace('\n', '.').split('.') if len(s.strip()) > 10]
        bullets = []
        for i, s in enumerate(sentences[:5]):
            verb = STRONG_VERBS[i % len(STRONG_VERBS)]
            bullets.append(f"{verb} {s.lstrip('- \u2022').strip()}")
        if not bullets:
            bullets = [
                "Delivered key initiatives that improved team productivity by 20%.",
                "Automated workflows, reducing manual processing time by 35%.",
                "Optimised existing systems, cutting operational costs significantly.",
            ]
        return {"bullets": bullets, "tips": TIPS[:2]}

    # action == "improve"
    improved = content
    for wv in WEAK_VERBS:
        if wv.lower() in improved.lower():
            improved = improved.replace(wv, STRONG_VERBS[WEAK_VERBS.index(wv) % len(STRONG_VERBS)])
    return {
        "improved": improved,
        "tips": TIPS[:3],
        "note": "Set GROQ_API_KEY in .env for real AI suggestions."
    }
