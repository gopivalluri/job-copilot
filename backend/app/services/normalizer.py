"""
Job Normalization Service
Converts raw job data (from connectors or ingestion) into normalized Job model fields.
"""
import re
from typing import Dict, Any, List, Optional, Tuple

from app.models.models import EmploymentType, WorkMode, ExperienceLevel
from app.services.sponsorship_engine import detect_sponsorship


def normalize_employment_type(text: str) -> Optional[EmploymentType]:
    """Infer employment type from title/description text."""
    t = text.lower()
    if re.search(r'\bfull[\s\-]?time\b', t):
        return EmploymentType.full_time
    if re.search(r'\bcontract\b|\bcontractor\b|\bc2c\b|\bc2h\b', t):
        return EmploymentType.contract
    if re.search(r'\bpart[\s\-]?time\b', t):
        return EmploymentType.part_time
    if re.search(r'\bintern\b|\binternship\b', t):
        return EmploymentType.internship
    return None


def normalize_work_mode(location: str, description: str) -> Optional[WorkMode]:
    """Infer work mode from location string and description."""
    combined = (location + " " + description).lower()
    if re.search(r'\bfully\s+remote\b|\b100%\s+remote\b', combined):
        return WorkMode.remote
    if re.search(r'\bhybrid\b', combined):
        return WorkMode.hybrid
    if re.search(r'\bremote\b', combined):
        return WorkMode.remote
    if re.search(r'\bonsite\b|\bon[\s\-]?site\b|\bin[\s\-]?office\b', combined):
        return WorkMode.onsite
    return None


def normalize_experience_level(title: str, description: str) -> Optional[ExperienceLevel]:
    """Infer seniority from title and description text."""
    combined = (title + " " + description).lower()
    if re.search(r'\bstaff\s+engineer\b|\bprincipal\b', combined):
        return ExperienceLevel.staff
    if re.search(r'\blead\s+(?:engineer|developer)\b|\btechnical\s+lead\b', combined):
        return ExperienceLevel.lead
    if re.search(r'\bsenior\b|\bsr\.\b', combined):
        return ExperienceLevel.senior
    if re.search(r'\bjunior\b|\bjr\.\b|\bentry[\s\-]?level\b|\b0[\s\-]?[–\-]?\s*2\s+years?\b', combined):
        return ExperienceLevel.entry
    return ExperienceLevel.mid  # default


def extract_salary(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract salary range from description text."""
    # Patterns: $120k-$160k, $120,000 - $160,000, 120000-160000
    patterns = [
        r'\$(\d{1,3})[kK]\s*[-–]\s*\$?(\d{1,3})[kK]',             # $120k - $160k
        r'\$(\d{2,3}),?000\s*[-–]\s*\$?(\d{2,3}),?000',            # $120,000 - $160,000
        r'(\d{2,3})[kK]\s*[-–]\s*(\d{2,3})[kK]',                   # 120k-160k
        r'salary[:\s]+\$?(\d{2,3}),?000\+?',                        # Salary: $120,000+
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                low = int(groups[0].replace(',', ''))
                high = int(groups[1].replace(',', ''))
                if low < 1000:
                    low *= 1000
                if high < 1000:
                    high *= 1000
                return low, high
            elif len(groups) == 1:
                val = int(groups[0].replace(',', ''))
                if val < 1000:
                    val *= 1000
                return val, None
    return None, None


def extract_skills_from_description(description: str) -> List[str]:
    """Extract tech keywords from job description."""
    TECH_VOCAB = [
        "python", "java", "javascript", "typescript", "golang", "go", "rust", "scala",
        "react", "vue", "angular", "node.js", "next.js",
        "fastapi", "django", "flask", "spring", "express",
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka",
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
        "graphql", "rest", "grpc", "microservices",
        "machine learning", "pytorch", "tensorflow", "spark",
        "ci/cd", "git", "linux", "agile",
    ]
    desc_lower = description.lower()
    return [skill for skill in TECH_VOCAB if re.search(r'\b' + re.escape(skill) + r'\b', desc_lower)]


def normalize_job(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a raw job dict (from connector or manual ingest) into
    a dict suitable for creating/updating a Job model.
    """
    title = raw.get("title", "")
    company = raw.get("company", "")
    description = raw.get("description", "")
    location = raw.get("location", "")
    candidate_required_location = raw.get("candidate_required_location", location)

    combined_text = f"{title} {description}"

    # Sponsorship detection
    sponsorship_status, sponsorship_notes = detect_sponsorship(description)

    # Salary
    salary_min = raw.get("salary_min")
    salary_max = raw.get("salary_max")
    if salary_min is None:
        salary_min, salary_max = extract_salary(description)

    # Skills
    skills = raw.get("skills_required") or extract_skills_from_description(description)

    return {
        "external_id":        str(raw.get("id", raw.get("external_id", ""))),
        "source":             raw.get("source", "manual"),
        "source_url":         raw.get("url", raw.get("source_url", "")),
        "title":              title,
        "company":            company,
        "location":           candidate_required_location or location,
        "description":        description,
        "employment_type":    normalize_employment_type(combined_text),
        "work_mode":          normalize_work_mode(location, description),
        "experience_level":   normalize_experience_level(title, description),
        "skills_required":    skills,
        "salary_min":         salary_min,
        "salary_max":         salary_max,
        "sponsorship_status": sponsorship_status,
        "sponsorship_notes":  sponsorship_notes,
    }
