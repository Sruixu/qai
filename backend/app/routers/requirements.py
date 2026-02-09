import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_session
from app.core.vector_store import vector_store
from app.models.models import Requirement, RequirementCreate, RequirementRead, RequirementUpdate, TestCase, TestCaseRead, KnowledgeItem
from app.services.llm_service import llm_service
from datetime import datetime
import json
import io

router = APIRouter()

class GenerateRequest(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = "deepseek-chat"

@router.post("/requirements/import_file")
async def import_requirements_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Import requirements from uploaded Markdown file.
    Splits by '【' or '#' to identify requirements.
    """
    if not file.filename.endswith('.md'):
         raise HTTPException(status_code=400, detail="Only .md files are supported")
         
    content_bytes = await file.read()
    try:
        content = content_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = content_bytes.decode('gbk')
        except:
            raise HTTPException(status_code=400, detail="Could not decode file. Please use UTF-8 or GBK.")

    # Simple splitting logic: Split by empty lines or specific markers
    sections = content.split('\n\n')
    imported_count = 0
    
    current_title = f"导入需求-{datetime.now().strftime('%Y%m%d%H%M')}"
    current_content = ""
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Heuristic: If line starts with 【 or #, treat as title
        if section.startswith("【") or section.startswith("#"):
            if current_content:
                # Save previous
                req = Requirement(title=current_title, content=current_content)
                session.add(req)
                imported_count += 1
            
            lines = section.split('\n')
            current_title = lines[0].strip()[:50].replace('#', '').strip() # Limit title length and clean
            current_content = section
        else:
            current_content += "\n\n" + section

    # Save last one
    if current_content:
        req = Requirement(title=current_title, content=current_content)
        session.add(req)
        imported_count += 1
        
    session.commit()
    return {"message": f"Successfully imported {imported_count} requirements"}

@router.post("/requirements/{requirement_id}/sync_kb")
def sync_requirement_to_knowledge_base(requirement_id: int, session: Session = Depends(get_session)):
    requirement = session.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Get associated test cases
    cases = session.exec(select(TestCase).where(TestCase.requirement_id == requirement_id)).all()
    
    # Convert cases to JSON string for metadata
    cases_data = []
    for c in cases:
        cases_data.append({
            "title": c.title,
            "steps": c.steps,
            "expected": c.expected_result
        })
    
    cases_json = json.dumps(cases_data, ensure_ascii=False)
    
    # Add to Vector Store
    # Doc ID = req_{id}
    vector_store.add_document(
        doc_id=f"req_{requirement.id}",
        text=requirement.content,
        metadata={
            "title": requirement.title,
            "cases_json": cases_json,
            "source": "qai_db"
        }
    )
    
    # Also sync to KnowledgeItem SQL table for visibility
    # Check if exists to avoid duplicates
    kb_content = f"【历史需求】{requirement.title}\n{requirement.content[:500]}..."
    
    existing_item = session.exec(select(KnowledgeItem).where(KnowledgeItem.content == kb_content)).first()
    if existing_item:
        return {"message": "已存在于知识库，无需重复同步"}

    kb_item = KnowledgeItem(
        category="业务规则", # Default category or maybe "历史需求"
        content=kb_content,
        tags="自动同步,需求归档"
    )
    session.add(kb_item)
    session.commit()
    
    return {"message": "同步至知识库成功 (Vector + SQL)"}

@router.post("/requirements/", response_model=RequirementRead)
def create_requirement(requirement: RequirementCreate, session: Session = Depends(get_session)):
    db_requirement = Requirement.from_orm(requirement)
    session.add(db_requirement)
    session.commit()
    session.refresh(db_requirement)
    return db_requirement

@router.get("/requirements/", response_model=List[RequirementRead])
def read_requirements(
    version_id: Optional[int] = None,
    offset: int = 0, 
    limit: int = 100, 
    session: Session = Depends(get_session)
):
    query = select(Requirement)
    if version_id:
        query = query.where(Requirement.version_id == version_id)
        
    query = query.offset(offset).limit(limit)
    requirements = session.exec(query).all()
    return requirements

@router.get("/requirements/{requirement_id}", response_model=RequirementRead)
def read_requirement(requirement_id: int, session: Session = Depends(get_session)):
    requirement = session.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement

@router.put("/requirements/{requirement_id}", response_model=RequirementRead)
def update_requirement(requirement_id: int, requirement: RequirementUpdate, session: Session = Depends(get_session)):
    db_requirement = session.get(Requirement, requirement_id)
    if not db_requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    requirement_data = requirement.dict(exclude_unset=True)
    for key, value in requirement_data.items():
        setattr(db_requirement, key, value)
    
    db_requirement.updated_at = datetime.now()
    session.add(db_requirement)
    session.commit()
    session.refresh(db_requirement)
    return db_requirement

@router.delete("/requirements/{requirement_id}")
def delete_requirement(requirement_id: int, session: Session = Depends(get_session)):
    requirement = session.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    session.delete(requirement)
    session.commit()
    return {"ok": True}

@router.post("/requirements/{requirement_id}/generate_cases", response_model=List[TestCaseRead])
def generate_cases_for_requirement(
    requirement_id: int, 
    gen_config: GenerateRequest,
    session: Session = Depends(get_session)
):
    requirement = session.get(Requirement, requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Call AI Service with dynamic config
    generated_data = llm_service.generate_test_cases(
        requirement_content=requirement.content,
        api_key=gen_config.api_key,
        base_url=gen_config.base_url,
        model=gen_config.model
    )
    
    created_cases = []
    for case_data in generated_data:
        test_case = TestCase(
            module=case_data.get("module", "默认模块"),
            title=case_data["title"],
            precondition=case_data.get("precondition"),
            steps=case_data["steps"],
            expected_result=case_data["expected_result"],
            priority=case_data.get("priority", "P2"),
            requirement_id=requirement.id
        )
        session.add(test_case)
        created_cases.append(test_case)
    
    session.commit()
    
    for case in created_cases:
        session.refresh(case)
        
    return created_cases
