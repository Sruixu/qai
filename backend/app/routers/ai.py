from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.llm_service import llm_service

router = APIRouter()

class AIConfig(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = "deepseek-chat"

class AnalyzeRequest(AIConfig):
    requirement_content: str

class ScenarioRequest(AIConfig):
    requirement_content: str
    module: str

class CaseRequest(AIConfig):
    requirement_content: str
    module: str
    scenario: str

class ScriptRequest(AIConfig):
    test_case: Dict[str, Any]

@router.post("/analyze_modules")
def analyze_modules(req: AnalyzeRequest):
    return llm_service.analyze_modules(req.requirement_content, req.api_key, req.base_url, req.model)

@router.post("/generate_scenarios")
def generate_scenarios(req: ScenarioRequest):
    return llm_service.generate_scenarios(req.requirement_content, req.module, req.api_key, req.base_url, req.model)

@router.post("/generate_cases")
def generate_cases(req: CaseRequest):
    return llm_service.generate_test_cases_rag(
        req.requirement_content, req.module, req.scenario, 
        req.api_key, req.base_url, req.model
    )

@router.post("/generate_script")
def generate_script(req: ScriptRequest):
    return {"script": llm_service.generate_automation_script(req.test_case, req.api_key, req.base_url, req.model)}
