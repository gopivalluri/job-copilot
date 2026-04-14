"""
Mock Job Connector
Generates realistic sample jobs for development/demo purposes.
In production, swap with real API connectors (Remotive, LinkedIn unofficial, etc.)
These mock jobs cover a range of sponsorship statuses, locations, and employment types.
"""
from typing import List, Dict, Any
import random


MOCK_JOBS: List[Dict[str, Any]] = [
    {
        "id": "mock-001",
        "source": "mock",
        "title": "Senior Backend Engineer",
        "company": "Stripe",
        "location": "Remote, USA",
        "url": "https://stripe.com/jobs/mock-001",
        "description": """We are looking for a Senior Backend Engineer to join our Payments Infrastructure team.

We offer H1B visa sponsorship and H1B transfers for qualified candidates.

Responsibilities:
- Design and build highly available distributed systems processing billions of transactions
- Work closely with product teams to define and implement new payment features
- Contribute to our open-source libraries and internal tooling

Requirements:
- 5+ years of backend engineering experience
- Strong proficiency in Python or Go
- Experience with distributed systems, microservices
- PostgreSQL, Redis, Kafka experience preferred
- AWS or GCP cloud infrastructure knowledge

Compensation: $180,000 - $240,000 base + equity + benefits
Work arrangement: Remote-first, flexible hours
Visa sponsorship: Available including H1B transfer""",
    },
    {
        "id": "mock-002",
        "source": "mock",
        "title": "Python Developer - Data Platform",
        "company": "Databricks",
        "location": "San Francisco, CA / Remote",
        "url": "https://databricks.com/jobs/mock-002",
        "description": """Databricks is hiring a Python Developer for our Data Platform team.

We support visa sponsorship for this role.

About the role:
- Build and maintain our core data processing pipelines
- Work with Apache Spark, Delta Lake, and Python
- Design APIs consumed by thousands of enterprise customers
- Collaborate with ML engineers on feature engineering systems

Required skills:
- Python (expert level), SQL
- Apache Spark, PySpark
- Docker, Kubernetes
- REST API design
- Experience with distributed computing

Salary range: $160,000 - $210,000
Immigration support provided. Open to all work authorizations.""",
    },
    {
        "id": "mock-003",
        "source": "mock",
        "title": "Software Engineer II - Platform",
        "company": "Coinbase",
        "location": "Remote - US",
        "url": "https://coinbase.com/jobs/mock-003",
        "description": """Coinbase is looking for a Software Engineer II to join our Platform Infrastructure team.

Note: Applicants must be authorized to work in the United States without sponsorship.
We are unable to sponsor or take over sponsorship of an employment visa at this time.

Responsibilities:
- Build internal developer platforms and tooling
- Maintain and improve our Kubernetes-based infrastructure
- Write Go and Python services
- Participate in on-call rotation

Requirements:
- 3+ years software engineering experience
- Go or Python proficiency
- Kubernetes, Docker experience
- AWS knowledge preferred

Salary: $140,000 - $175,000""",
    },
    {
        "id": "mock-004",
        "source": "mock",
        "title": "Senior Software Engineer - Backend",
        "company": "Figma",
        "location": "San Francisco, CA or New York, NY",
        "url": "https://figma.com/jobs/mock-004",
        "description": """Figma is hiring a Senior Software Engineer to work on our real-time collaboration backend.

Visa sponsorship available for the right candidate. H1B transfers welcome.

You will:
- Build systems that power real-time collaborative editing at scale
- Work with TypeScript/Node.js backend services
- Optimize performance for millions of concurrent users
- Mentor junior engineers

Requirements:
- 5+ years backend engineering
- TypeScript or Node.js proficiency
- Distributed systems experience
- Experience with WebSockets or real-time systems a plus

Total compensation: $200,000 - $280,000 (base + equity)
Hybrid work: 2 days/week in office preferred""",
    },
    {
        "id": "mock-005",
        "source": "mock",
        "title": "Machine Learning Engineer",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "url": "https://openai.com/jobs/mock-005",
        "description": """OpenAI is seeking a Machine Learning Engineer to work on our foundation models team.

Sponsorship for work authorization is available.

Responsibilities:
- Implement and optimize ML training pipelines
- Work with Python, PyTorch at massive scale
- Collaborate with researchers on production deployment
- Build tooling for model evaluation and safety

Requirements:
- 4+ years ML engineering experience
- PyTorch or TensorFlow expertise
- Python, CUDA knowledge
- Experience with large-scale distributed training

Compensation: $250,000 - $370,000 total compensation
On-site in San Francisco (relocation assistance provided)""",
    },
    {
        "id": "mock-006",
        "source": "mock",
        "title": "Backend Engineer - Contract",
        "company": "Scale AI",
        "location": "Remote",
        "url": "https://scale.com/jobs/mock-006",
        "description": """Scale AI is looking for a contract Backend Engineer to join our data labeling platform team.

This is a 6-month contract with potential for full-time conversion.
We do not offer visa sponsorship for contract positions.

Responsibilities:
- Build and maintain Python/FastAPI microservices
- Integrate third-party data labeling tools
- Work with PostgreSQL and Redis

Requirements:
- 3+ years Python backend experience
- FastAPI or Django experience
- PostgreSQL proficiency
- Docker familiarity

Rate: $80 - $100/hour
Remote position""",
    },
    {
        "id": "mock-007",
        "source": "mock",
        "title": "Staff Software Engineer",
        "company": "Airbnb",
        "location": "Remote, USA",
        "url": "https://airbnb.com/jobs/mock-007",
        "description": """Airbnb is hiring a Staff Software Engineer for our Payments team.

Visa sponsorship available including H1B transfer.

As a Staff Engineer you will:
- Define technical direction for critical infrastructure
- Lead cross-team technical initiatives
- Mentor senior engineers
- Drive architecture decisions for systems processing $billions annually

Requirements:
- 8+ years engineering, 3+ at senior/staff level
- Python and Java expertise
- Distributed systems at scale
- Strong system design skills

Compensation: $280,000 - $380,000 total
Remote-first with quarterly team gatherings""",
    },
    {
        "id": "mock-008",
        "source": "mock",
        "title": "Software Engineer - Defense Systems",
        "company": "Palantir",
        "location": "Washington, DC",
        "url": "https://palantir.com/jobs/mock-008",
        "description": """Palantir is seeking a Software Engineer for our Government division.

IMPORTANT: This role requires an active TS/SCI security clearance.
US citizenship is required. We cannot sponsor visas for this position.

Responsibilities:
- Build data integration pipelines for government clients
- Work with classified data in secure environments
- Python, Java backend development

Requirements:
- Active TS/SCI clearance required
- US Citizen only
- 3+ years software engineering experience
- Python expertise

Salary: $150,000 - $200,000""",
    },
    {
        "id": "mock-009",
        "source": "mock",
        "title": "Senior Python Engineer - FinTech",
        "company": "Robinhood",
        "location": "Menlo Park, CA / New York, NY / Remote",
        "url": "https://robinhood.com/jobs/mock-009",
        "description": """Robinhood is growing its engineering team and looking for a Senior Python Engineer.

Open to all work authorizations. Immigration support provided.

You will work on:
- High-performance trading and brokerage backend services
- Real-time market data processing systems
- Regulatory compliance systems
- Internal tooling and developer experience

Tech stack: Python, Django, PostgreSQL, Redis, Kafka, AWS

Requirements:
- 4+ years Python experience
- Experience with high-throughput systems
- SQL expertise
- AWS preferred

Compensation: $175,000 - $225,000 + equity
Flexible remote/hybrid work""",
    },
    {
        "id": "mock-010",
        "source": "mock",
        "title": "Backend Engineer - Infrastructure",
        "company": "Vercel",
        "location": "Remote (Global)",
        "url": "https://vercel.com/jobs/mock-010",
        "description": """Vercel is hiring a Backend Engineer to work on our Edge Network infrastructure.

This role is open to candidates worldwide. We support work visas and immigration where possible.

Responsibilities:
- Build and scale our global CDN and serverless infrastructure
- Work with Go, TypeScript, and Rust
- Design low-latency systems serving millions of developers
- Contribute to open-source projects (Next.js ecosystem)

Requirements:
- 3+ years backend engineering
- Go or Rust experience preferred
- Understanding of CDN/networking concepts
- Distributed systems knowledge

Salary: $140,000 - $190,000 (US range)
Fully remote""",
    },
    {
        "id": "mock-011",
        "source": "mock",
        "title": "Full Stack Engineer",
        "company": "Linear",
        "location": "Remote - USA/Canada",
        "url": "https://linear.app/jobs/mock-011",
        "description": """Linear is a small team building the best software project management tool.

We are a tight-knit team and can offer visa sponsorship for exceptional candidates.

You will:
- Build full-stack features in TypeScript/React
- Work on our Node.js backend
- Optimize for performance and developer experience
- Have a large impact on a small team

Stack: TypeScript, React, Node.js, PostgreSQL, GraphQL

Requirements:
- Strong TypeScript/JavaScript skills
- React and Node.js experience
- Product sense and attention to UX detail
- 3+ years full-stack experience

Compensation: $160,000 - $200,000 + meaningful equity
Remote-first""",
    },
    {
        "id": "mock-012",
        "source": "mock",
        "title": "Senior Data Engineer",
        "company": "Snowflake",
        "location": "Austin, TX / Remote",
        "url": "https://snowflake.com/jobs/mock-012",
        "description": """Snowflake is hiring a Senior Data Engineer for our Cloud Data Platform team in Texas.

Visa sponsorship available. H1B transfers accepted.

Responsibilities:
- Design and optimize data pipelines at petabyte scale
- Build Python/SQL data transformation workflows
- Work with Snowflake, dbt, Airflow
- Enable analytics for enterprise customers

Requirements:
- 5+ years data engineering experience
- Python and SQL expertise
- Experience with modern data stack (dbt, Airflow, Spark)
- Snowflake or similar cloud DW experience

Salary: $165,000 - $220,000
Austin TX preferred, remote considered""",
    },
    {
        "id": "mock-013",
        "source": "mock",
        "title": "Software Engineer - Entry Level",
        "company": "Meta",
        "location": "Menlo Park, CA",
        "url": "https://meta.com/jobs/mock-013",
        "description": """Meta is hiring entry-level Software Engineers for our Infrastructure teams.

We support visa sponsorship for new graduates and early career engineers.

Program overview:
- 2-year structured rotational program
- Mentorship from senior engineers
- Work on real production systems from day one

Requirements:
- 0-2 years experience or recent graduate
- Proficiency in Python, Java, or C++
- Strong CS fundamentals (algorithms, data structures)
- Interest in distributed systems

Compensation: $170,000 - $190,000 (base + bonus + RSU) for new grads
On-site in Menlo Park""",
    },
    {
        "id": "mock-014",
        "source": "mock",
        "title": "DevOps / Platform Engineer",
        "company": "HashiCorp",
        "location": "Remote, USA",
        "url": "https://hashicorp.com/jobs/mock-014",
        "description": """HashiCorp is seeking a Platform Engineer to join our internal infrastructure team.

Work authorization sponsorship not available for this role.
Must be legally authorized to work in the United States.

Responsibilities:
- Manage and improve our Kubernetes-based developer platform
- Build Terraform modules for cloud infrastructure
- Support CI/CD pipelines with GitHub Actions
- Work with Vault, Consul, and Nomad in production

Requirements:
- 3+ years DevOps/Platform engineering
- Strong Terraform experience
- Kubernetes (EKS/GKE) proficiency
- Go or Python for tooling

Salary: $150,000 - $190,000
Remote""",
    },
    {
        "id": "mock-015",
        "source": "mock",
        "title": "Senior Software Engineer - Backend APIs",
        "company": "Plaid",
        "location": "San Francisco, CA / New York, NY",
        "url": "https://plaid.com/jobs/mock-015",
        "description": """Plaid is looking for a Senior Software Engineer to build our financial data APIs.

We offer immigration assistance and visa sponsorship for this role.

About the role:
- Build and maintain our bank connectivity and financial data APIs
- Python and Go backend services processing millions of API calls
- Work closely with fintech customers to expand our API capabilities
- Design for security, reliability, and compliance

Requirements:
- 5+ years backend engineering
- Python or Go proficiency
- API design expertise
- Financial services or security experience a plus

Compensation: $195,000 - $260,000
Hybrid in SF or NYC (2-3 days/week)""",
    },
]


def fetch_mock_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Return mock job listings. In production, replace with real API calls.
    Respects platform TOS - no scraping or restricted automation.
    """
    jobs = MOCK_JOBS.copy()
    # Shuffle to simulate "new" results each fetch
    random.shuffle(jobs)
    return jobs[:limit]
