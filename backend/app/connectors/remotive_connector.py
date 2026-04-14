import httpx, re
from typing import List, Dict, Any

REMOTIVE_API = "https://remotive.com/api/remote-jobs"
SEARCH_QUERIES = ["software engineer","backend engineer","python developer","full stack engineer"]

async def fetch_remotive_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    all_jobs, seen_ids = [], set()
    async with httpx.AsyncClient(timeout=30.0) as client:
        for query in SEARCH_QUERIES:
            try:
                resp = await client.get(REMOTIVE_API, params={"search": query, "limit": 20})
                if resp.status_code != 200: continue
                for job in resp.json().get("jobs", []):
                    job_id = str(job.get("id",""))
                    if job_id in seen_ids: continue
                    seen_ids.add(job_id)
                    desc = re.sub(r'\s+',' ',re.sub(r'<[^>]+',' ',job.get("description",""))).strip()
                    all_jobs.append({"id":job_id,"source":"remotive","title":job.get("title",""),"company":job.get("company_name",""),"location":job.get("candidate_required_location","Remote"),"description":desc,"url":job.get("url",""),"source_url":job.get("url",""),"published_at":job.get("publication_date","")})
                    if len(all_jobs) >= limit: break
            except Exception as e: print(f"Remotive error: {e}")
            if len(all_jobs) >= limit: break
    return all_jobs[:limit]
