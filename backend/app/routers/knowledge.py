from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.models.models import KnowledgeItem, KnowledgeItemCreate, KnowledgeItemRead

router = APIRouter()

@router.post("/knowledge/", response_model=KnowledgeItemRead)
def create_knowledge_item(item: KnowledgeItemCreate, session: Session = Depends(get_session)):
    db_item = KnowledgeItem.from_orm(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/knowledge/", response_model=List[KnowledgeItemRead])
def read_knowledge_items(
    category: str = None, 
    offset: int = 0, 
    limit: int = 100, 
    session: Session = Depends(get_session)
):
    query = select(KnowledgeItem)
    if category:
        query = query.where(KnowledgeItem.category == category)
    items = session.exec(query.offset(offset).limit(limit)).all()
    return items

@router.delete("/knowledge/{item_id}")
def delete_knowledge_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(KnowledgeItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    session.delete(item)
    session.commit()
    return {"ok": True}
