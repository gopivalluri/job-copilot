"""
AI Content Generation Service
Uses Anthropic Claude API to:
1. Tailor resume bullets to a specific job
2. Generate a targeted cover letter
3. Identify key skill matches and gaps
"""
from typing import Dict, List, Optional, Tuple
import anthropic
import json
import re

from app.core.config import settings


def _get_client() -> Optional[anthropic.Anthropic]:
    if not settings.ANTHROPIC_API_KEY:
        return None
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _build_tailor_prompt(
    resume_text: str,
    job_title: str,
    company: str,
    job_description: str,
    generate_cover_letter: bool = True,
) -> str:
    cover_letter_instruction = """
4. A compelling cover letter (3-4 paragraphs) specifically for this role.
""" if generate_cover_letter else ""

    return f"""You are an expert technical resume writer and career coach.

Given a candidate's resume and a job posting, provide:
1. 5-7 tailored resume bullet points that highlight relevant experience for THIS specific role
2. A list of key skills/technologies that match between the resume and job
3. 2-3 actionable suggestions to strengthen the application
{cover_letter_instruction}

RESUME:
{resume_text[:3000]}

JOB TITLE: {job_title}
COMPANY: {company}

JOB DESCRIPTION:
{job_description[:2000]}

Respond ONLY with a JSON object in this exact format:
{{
  "tailored_bullets": [
    "• Led development of high-throughput data pipeline processing 10M+ events/day using Python and Kafka",
    "• Architected and deployed RESTful microservices on AWS ECS reducing latency by 40%"
  ],
  "key_matches": ["Python", "AWS", "microservices", "REST APIs"],
  "suggestions": [
    "Add specific metrics to your current role's impact statements",
    "Highlight your Kubernetes experience more prominently"
  ],
  "cover_letter": "Dear Hiring Manager,\\n\\n[Letter content here]\\n\\nBest regards,\\n[Your Name]"
}}"""


def tailor_resume_mock(
    resume_text: str,
    job_title: str,
    company: str,
    job_description: str,
    generate_cover_letter: bool = True,
) -> Tuple[str, Optional[str], List[str], List[str]]:
    """
    Mock tailoring for when no API key is configured.
    Returns (tailored_resume_text, cover_letter, key_matches, suggestions)
    """
    # Extract skills from job description for demo
    tech_pattern = re.compile(
        r'\b(python|java|javascript|typescript|react|node|sql|docker|kubernetes|aws|gcp|azure|'
        r'fastapi|django|kafka|redis|postgresql|graphql|microservices|ci\/cd|terraform)\b',
        re.IGNORECASE
    )
    matches = list(set(m.group(0) for m in tech_pattern.finditer(job_description)))[:6]

    tailored = f"""TAILORED HIGHLIGHTS FOR {job_title.upper()} AT {company.upper()}

• Developed and maintained production {matches[0] if matches else 'Python'} services handling 1M+ daily requests with 99.9% uptime
• Designed scalable microservices architecture on {'AWS' if 'aws' in job_description.lower() else 'cloud'} reducing infrastructure costs by 35%
• Collaborated with cross-functional teams using Agile/Scrum to deliver features 20% ahead of schedule
• Built automated CI/CD pipelines reducing deployment time from 2 hours to 15 minutes
• Mentored 3 junior engineers and led technical design review process for new features
• Implemented comprehensive test suites achieving 90%+ code coverage across critical services

[Original resume content preserved below]
{resume_text[:500]}...
"""

    cover_letter = None
    if generate_cover_letter:
        cover_letter = f"""Dear Hiring Manager,

I am excited to apply for the {job_title} position at {company}. With my background in software engineering and hands-on experience with {', '.join(matches[:3]) if matches else 'modern technologies'}, I am confident I can make an immediate impact on your team.

In my current role, I have successfully architected and delivered high-performance backend systems that scaled to millions of users. I bring strong expertise in distributed systems, cloud infrastructure, and collaborative engineering culture that aligns well with {company}'s engineering values.

I am particularly drawn to this opportunity because it combines technical depth with meaningful impact. I look forward to contributing to your team's mission and growing alongside world-class engineers.

Thank you for considering my application. I would love to discuss how my experience can benefit {company}.

Best regards,
[Your Name]"""

    suggestions = [
        f"Add specific metrics (throughput, latency, cost savings) to each bullet point",
        f"Highlight your {matches[0] if matches else 'primary language'} expertise earlier in your resume",
        "Include a brief technical summary at the top tailored to this role",
    ]

    return tailored, cover_letter, matches, suggestions


async def generate_tailored_content(
    resume_text: str,
    job_title: str,
    company: str,
    job_description: str,
    generate_cover_letter: bool = True,
) -> Tuple[str, Optional[str], List[str], List[str]]:
    """
    Main entry point: returns (tailored_resume, cover_letter, key_matches, suggestions)
    Falls back to mock if no API key.
    """
    client = _get_client()

    if client is None:
        # No API key - use mock
        return tailor_resume_mock(
            resume_text, job_title, company, job_description, generate_cover_letter
        )

    prompt = _build_tailor_prompt(
        resume_text, job_title, company, job_description, generate_cover_letter
    )

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        content = message.content[0].text

        # Strip JSON fences if present
        content = re.sub(r'^```json\s*', '', content.strip())
        content = re.sub(r'\s*```$', '', content)

        data = json.loads(content)

        tailored_bullets = "\n".join(data.get("tailored_bullets", []))
        tailored_resume = f"TAILORED FOR: {job_title} at {company}\n\n{tailored_bullets}\n\n---\n{resume_text[:1000]}"
        cover_letter = data.get("cover_letter") if generate_cover_letter else None
        key_matches = data.get("key_matches", [])
        suggestions = data.get("suggestions", [])

        return tailored_resume, cover_letter, key_matches, suggestions

    except Exception as e:
        # Graceful fallback
        print(f"AI generation error: {e}, falling back to mock")
        return tailor_resume_mock(
            resume_text, job_title, company, job_description, generate_cover_letter
        )
