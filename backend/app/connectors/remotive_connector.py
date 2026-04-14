"""
Job Connector - Multiple free APIs for real job postings
1. Arbeitnow.com - free, no auth, reliable
2. Remotive.com - free remote jobs
"""
import httpx, re
from typing import List, Dict, Any

def _clean(html):
    text = re.sub(r'<[^>]+>', ' ', html)
    return re.sub(r'\s+', ' ', text).strip().replace('&amp;','&').replace('&nbsp;',' ').replace('&#39;',"'")

async def fetch_arbeitnow_jobs(limit=50):
    jobs = []
    tech = ["software","engineer","developer","python","backend","frontend","fullstack","data","devops","ml","cloud","platform"]
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for page in range(1, 4):
                r = await client.get("https://arbeitnow.com/api/job-board-api", params={"page": page})
                if r.status_code != 200: break
                for job in r.json().get("data", []):
                    title = job.get("title","").lower()
                    if not any(k in title for k in tech): continue
                    jobs.append({"id":str(job.get("slug",title[:20])),"source":"arbeitnow","title":job.get("title",""),"company":job.get("company_name",""),"location":job.get("location","Remote"),"description":_clean(job.get("description","")),"url":job.get("url",""),"source_url":job.get("url",""),"published_at":job.get("created_at","")})
                    if len(jobs) >= limit: break
                if len(jobs) >= limit: break
    except Exception as e:
        print(f"Arbeitnow error: {e}")
    return jobs[:limit]

async def fetch_remotive_jobs(limit=30):
    jobs, seen = [], set()
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            for q in ["software engineer","python developer","backend engineer"]:
                try:
                    r = await client.get("https://remotive.com/api/remote-jobs", params={"search":q,"limit":15})
                    if r.status_code != 200: continue
                    for job in r.json().get("jobs",[]):
                        jid = str(job.get("id",""))
                        if jid in seen: continue
                        seen.add(jid)
                        jobs.append({"id":jid,"source":"remotive","title":job.get("title",""),"company":job.get("company_name",""),"location":job.get("candidate_required_location","Remote"),"description":_clean(job.get("description","")),"url":job.get("url",""),"source_url":job.get("url",""),"published_at":job.get("publication_date","")})
                        if len(jobs) >= limit: break
                except: continue
                if len(jobs) >= limit: break
    except Exception as e:
        print(f"Remotive error: {e}")
    return jobs[:limit]

async def fetch_all_real_jobs(limit=50):
    jobs = []
    arb = await fetch_arbeitnow_jobs(limit=40)
    jobs.extend(arb)
    print(f"Arbeitnow: {len(arb)} jobs")
    if len(jobs) < limit:
        rem = await fetch_remotive_jobs(limit=20)
        jobs.extend(rem)
        print(f"Remotive: {len(rem)} jobs")
    return jobs[:limit]
