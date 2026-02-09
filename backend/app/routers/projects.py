from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.models.models import Project, ProjectCreate, ProjectRead, ProjectVersion, ProjectVersionCreate, ProjectVersionRead, ProjectVersionUpdate

router = APIRouter()

# --- Projects ---

@router.post("/projects/", response_model=ProjectRead)
def create_project(project: ProjectCreate, session: Session = Depends(get_session)):
    db_project = Project.from_orm(project)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

@router.get("/projects/", response_model=List[ProjectRead])
def read_projects(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    projects = session.exec(select(Project).offset(offset).limit(limit)).all()
    return projects

@router.get("/projects/{project_id}", response_model=ProjectRead)
def read_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return {"ok": True}

# --- Versions ---

@router.post("/projects/{project_id}/versions", response_model=ProjectVersionRead)
def create_project_version(project_id: int, version: ProjectVersionCreate, session: Session = Depends(get_session)):
    # Verify project exists
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create DB object manually to include project_id
    db_version = ProjectVersion(**version.dict(), project_id=project_id)
    session.add(db_version)
    session.commit()
    session.refresh(db_version)
    return db_version

@router.get("/projects/{project_id}/versions", response_model=List[ProjectVersionRead])
def read_project_versions(project_id: int, session: Session = Depends(get_session)):
    versions = session.exec(select(ProjectVersion).where(ProjectVersion.project_id == project_id)).all()
    return versions

@router.put("/versions/{version_id}", response_model=ProjectVersionRead)
def update_version(version_id: int, version_update: ProjectVersionUpdate, session: Session = Depends(get_session)):
    db_version = session.get(ProjectVersion, version_id)
    if not db_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    version_data = version_update.dict(exclude_unset=True)
    for key, value in version_data.items():
        setattr(db_version, key, value)
        
    session.add(db_version)
    session.commit()
    session.refresh(db_version)
    return db_version

@router.delete("/versions/{version_id}")
def delete_version(version_id: int, session: Session = Depends(get_session)):
    version = session.get(ProjectVersion, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    session.delete(version)
    session.commit()
    return {"ok": True}
