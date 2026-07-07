import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl, field_validator
from dotenv import load_dotenv
from supabase import create_client, Client

from analyzer import analyze_url
from gemini_client import get_ai_explanation

load_dotenv()

app = FastAPI(title="GhostNet Backend", version="1.0.0")

# Setup CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
supabase_client: Optional[Client] = None
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "your_supabase_url_here" and SUPABASE_KEY != "your_supabase_anon_key_here":
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully connected to Supabase database.")
    except Exception as e:
        print(f"Failed to connect to Supabase: {str(e)}. Falling back to in-memory store.")
else:
    print("Supabase credentials not configured. Scans will be stored in-memory.")

# In-memory history fallback database
in_memory_scans = []

@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>GhostNet Template Missing</h1>", status_code=404)

class ScanRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        # Quick check for protocol, prepend if missing
        if not (v.startswith("http://") or v.startswith("https://")):
            # Simple check if there's at least a dot
            if "." not in v:
                raise ValueError("Invalid URL format")
        return v

class ConsequenceStep(BaseModel):
    step: str
    description: str
    risk: str

class ScanReport(BaseModel):
    id: str
    url: str
    domain: str
    trust_score: int
    risk_level: str
    domain_age_days: Optional[int]
    registrar: str
    https_enabled: bool
    suspicious_patterns: List[str]
    ghost_summary: str
    ghost_summary_en: Optional[str] = None
    ai_explanation: str
    recommendations: List[str]
    consequences: List[ConsequenceStep]
    created_at: str
    crawled_page_content: Optional[Dict] = None

@app.post("/api/scan", response_model=ScanReport)
async def scan_website(request: ScanRequest):
    input_url = request.url
    
    # 1. Perform technical analysis checks
    try:
        analysis = await analyze_url(input_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Technical analysis failed: {str(e)}")
        
    # 2. Get AI-powered explanation and final scoring from Gemini
    try:
        ai_response = await get_ai_explanation(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
        
    # 3. Assemble complete report
    report_id = str(uuid.uuid4())
    created_at_str = datetime.now(timezone.utc).isoformat()
    
    report_data = {
        "id": report_id,
        "url": analysis["url"],
        "domain": analysis["domain"],
        "trust_score": ai_response.get("trust_score", analysis["base_trust_score"]),
        "risk_level": ai_response.get("risk_level", "Medium Risk"),
        "domain_age_days": analysis["domain_age_days"],
        "registrar": analysis["registrar"],
        "https_enabled": analysis["https_enabled"],
        "suspicious_patterns": analysis["suspicious_patterns"],
        "ghost_summary": ai_response.get("ghost_summary", ""),
        "ghost_summary_en": ai_response.get("ghost_summary_en", ""),
        "ai_explanation": ai_response.get("ai_explanation", ""),
        "recommendations": ai_response.get("recommendations", []),
        "consequences": ai_response.get("consequences", []),
        "created_at": created_at_str,
        "crawled_page_content": analysis.get("crawled_page_content")
    }
    
    # 4. Save to Database (Supabase or In-Memory)
    if supabase_client:
        try:
            # Try inserting with ghost_summary_en first
            supabase_client.table("scans").insert({
                "id": report_data["id"],
                "url": report_data["url"],
                "domain": report_data["domain"],
                "trust_score": report_data["trust_score"],
                "risk_level": report_data["risk_level"],
                "domain_age_days": report_data["domain_age_days"],
                "registrar": report_data["registrar"],
                "https_enabled": report_data["https_enabled"],
                "suspicious_patterns": report_data["suspicious_patterns"],
                "ghost_summary": report_data["ghost_summary"],
                "ghost_summary_en": report_data["ghost_summary_en"],
                "ai_explanation": report_data["ai_explanation"],
                "recommendations": report_data["recommendations"],
                "consequences": report_data["consequences"]
            }).execute()
        except Exception as e:
            # If that fails (e.g. missing column in postgres table), retry without ghost_summary_en
            try:
                supabase_client.table("scans").insert({
                    "id": report_data["id"],
                    "url": report_data["url"],
                    "domain": report_data["domain"],
                    "trust_score": report_data["trust_score"],
                    "risk_level": report_data["risk_level"],
                    "domain_age_days": report_data["domain_age_days"],
                    "registrar": report_data["registrar"],
                    "https_enabled": report_data["https_enabled"],
                    "suspicious_patterns": report_data["suspicious_patterns"],
                    "ghost_summary": report_data["ghost_summary"],
                    "ai_explanation": report_data["ai_explanation"],
                    "recommendations": report_data["recommendations"],
                    "consequences": report_data["consequences"]
                }).execute()
            except Exception as e_inner:
                print(f"Supabase completely failed: {str(e_inner)}. Appending to in-memory fallback.")
                in_memory_scans.append(report_data)
    else:
        in_memory_scans.append(report_data)
        
    return report_data

@app.get("/api/history", response_model=List[ScanReport])
async def get_history():
    # Retrieve scan records
    history_records = []
    
    if supabase_client:
        try:
            response = supabase_client.table("scans").select("*").order("created_at", desc=True).limit(20).execute()
            data_rows = response.data or []
            
            for row in data_rows:
                # Convert database format to match ScanReport schema
                history_records.append({
                    "id": str(row["id"]),
                    "url": row["url"],
                    "domain": row["domain"],
                    "trust_score": row["trust_score"],
                    "risk_level": row["risk_level"],
                    "domain_age_days": row["domain_age_days"],
                    "registrar": row["registrar"],
                    "https_enabled": row["https_enabled"],
                    "suspicious_patterns": row.get("suspicious_patterns") or [],
                    "ghost_summary": row["ghost_summary"],
                    "ghost_summary_en": row.get("ghost_summary_en", ""),
                    "ai_explanation": row["ai_explanation"],
                    "recommendations": row.get("recommendations") or [],
                    "consequences": row.get("consequences") or [],
                    "created_at": row["created_at"],
                    "crawled_page_content": row.get("crawled_page_content")
                })
        except Exception as e:
            print(f"Supabase read failed: {str(e)}. Using in-memory fallback.")
            history_records = in_memory_scans.copy()
    else:
        history_records = in_memory_scans.copy()
        
    # Sort history records desc by date in case in-memory was used
    history_records.sort(key=lambda x: x["created_at"], reverse=True)
    return history_records[:20]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
