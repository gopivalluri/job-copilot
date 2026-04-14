"""
Resume Parser Service
Extracts structured data from resume text using pattern matching + heuristics.
In production, swap the _extract_with_ai() path for a real LLM call.
"""
import re
from typing import Any, Dict, List, Optional
import os


# ─── Common tech skills vocabulary ────────────────────────────────────────────
TECH_SKILLS = {
    # Languages
    "python", "java", "javascript", "typescript", "go", "golang", "rust", "c++",
    "c#", "ruby", "scala", "kotlin", "swift", "r", "matlab", "bash", "shell",
    # Web
    "react", "vue", "angular", "next.js", "nextjs", "node.js", "nodejs",
    "html", "css", "tailwind", "sass",
    # Backend
    "fastapi", "django", "flask", "spring", "express", "graphql", "rest", "grpc",
    # Data
    "sql", "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "kafka", "rabbitmq", "spark", "hadoop", "airflow", "dbt",
    # Cloud / Infra
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform",
    "ci/cd", "jenkins", "github actions", "ansible",
    # AI/ML
    "machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn",
    "pandas", "numpy", "llm", "openai", "langchain",
    # Other
    "git", "linux", "agile", "scrum", "microservices", "api",
}

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.s.", "m.s.", "b.e.", "m.e.", "computer science",
    "software engineering", "information technology", "electrical engineering",
]

JOB_TITLE_PATTERNS = [
    r"(?:software|backend|frontend|full[\s\-]stack|senior|lead|staff|principal)\s+engineer",
    r"software developer",
    r"data engineer",
    r"machine learning engineer",
    r"devops engineer",
    r"platform engineer",
    r"engineering manager",
]


def extract_skills(text: str) -> List[str]:
    """Extract tech skills by matching against known vocabulary."""
    text_lower = text.lower()
    found = []
    for skill in TECH_SKILLS:
        # Use word boundary matching where possible
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_experience_years(text: str) -> Optional[float]:
    """Try to extract years of experience from text."""
    patterns = [
        r'(\d+)\+?\s+years?\s+(?:of\s+)?(?:professional\s+)?experience',
        r'(\d+)\+?\s+years?\s+(?:in\s+)?(?:software|engineering|development)',
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def extract_current_title(text: str) -> Optional[str]:
    """Extract most likely current job title."""
    for pattern in JOB_TITLE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip().title()
    return None


def extract_education(text: str) -> List[Dict[str, str]]:
    """Extract education entries."""
    results = []
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in EDUCATION_KEYWORDS):
            cleaned = line.strip()
            if 10 < len(cleaned) < 200:
                results.append({"raw": cleaned})
    return results[:3]


def extract_experience_sections(text: str) -> List[Dict[str, Any]]:
    """
    Rough extraction of work experience blocks.
    Returns a simplified list; real parsing would use NLP.
    """
    entries = []
    # Look for date ranges as section markers
    date_pattern = re.compile(
        r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4})'
        r'\s*[-–—to]+\s*'
        r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|present|current)',
        re.IGNORECASE
    )
    for match in date_pattern.finditer(text):
        start = match.group(1)
        end = match.group(2)
        # Get surrounding context (title / company)
        surrounding = text[max(0, match.start()-100):match.start()].strip()
        last_line = surrounding.split('\n')[-1].strip() if surrounding else ""
        entries.append({
            "period": f"{start} - {end}",
            "context": last_line[:100] if last_line else "",
        })
    return entries[:5]


def parse_resume_text(raw_text: str) -> Dict[str, Any]:
    """
    Main parser: returns structured dict from raw resume text.
    """
    parsed: Dict[str, Any] = {
        "skills": extract_skills(raw_text),
        "experience_years": extract_experience_years(raw_text),
        "current_title": extract_current_title(raw_text),
        "education": extract_education(raw_text),
        "experience": extract_experience_sections(raw_text),
        "summary": _extract_summary(raw_text),
        "word_count": len(raw_text.split()),
    }
    return parsed


def _extract_summary(text: str) -> Optional[str]:
    """Extract first substantive paragraph as summary."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    for para in paragraphs:
        if 50 < len(para) < 600 and not any(
            kw in para.lower() for kw in ["education", "experience", "skills", "@", "phone"]
        ):
            return para
    return None


async def extract_text_from_upload(file_path: str, content_type: str) -> str:
    """
    Extract raw text from uploaded file.
    Supports .txt and (stubbed) .pdf/.docx.
    In production: use pdfminer / python-docx.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if content_type in ("text/plain",) or file_path.endswith(".txt"):
        with open(file_path, "r", errors="ignore") as f:
            return f.read()

    if file_path.endswith(".pdf"):
        # In production: use pdfminer.six
        # from pdfminer.high_level import extract_text
        # return extract_text(file_path)
        # Fallback: read raw bytes and decode printable chars
        with open(file_path, "rb") as f:
            raw = f.read()
        # Very rough text extraction for demo purposes
        text = raw.decode("latin-1", errors="ignore")
        text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
        return text

    # .docx fallback
    with open(file_path, "rb") as f:
        raw = f.read()
    return raw.decode("latin-1", errors="ignore")
