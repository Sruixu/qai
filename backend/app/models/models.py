from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class ProjectBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    versions: List["ProjectVersion"] = Relationship(back_populates="project", cascade_delete=True)

class ProjectVersionBase(SQLModel):
    version: str
    description: Optional[str] = None
    project_id: int = Field(foreign_key="project.id")
    created_at: datetime = Field(default_factory=datetime.now)

class ProjectVersion(ProjectVersionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project: Optional[Project] = Relationship(back_populates="versions")
    requirements: List["Requirement"] = Relationship(back_populates="version")

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: int

class ProjectVersionCreate(SQLModel):
    version: str
    description: Optional[str] = None

class ProjectVersionRead(ProjectVersionBase):
    id: int

class ProjectVersionUpdate(SQLModel):
    version: Optional[str] = None
    description: Optional[str] = None

class KnowledgeItemBase(SQLModel):
    category: str = Field(index=True) # 业务规则, 测试模式, 历史踩坑, 风险场景
    content: str
    tags: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class KnowledgeItem(KnowledgeItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class KnowledgeItemCreate(KnowledgeItemBase):
    pass

class KnowledgeItemRead(KnowledgeItemBase):
    id: int

class RequirementBase(SQLModel):
    title: str
    content: str
    version_id: Optional[int] = Field(default=None, foreign_key="projectversion.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Requirement(RequirementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    version: Optional[ProjectVersion] = Relationship(back_populates="requirements")
    test_cases: List["TestCase"] = Relationship(back_populates="requirement", cascade_delete=True)

class RequirementCreate(RequirementBase):
    pass

class RequirementRead(RequirementBase):
    id: int
    version: Optional[ProjectVersionRead] = None

class RequirementUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    version_id: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.now)

class TestCaseBase(SQLModel):
    module: Optional[str] = None
    title: str
    precondition: Optional[str] = None
    steps: str
    expected_result: str
    priority: str = Field(default="P1") # P0, P1, P2, P3
    actual_result: Optional[str] = None
    remark: Optional[str] = None
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")

class TestCase(TestCaseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement: Optional[Requirement] = Relationship(back_populates="test_cases")

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseRead(TestCaseBase):
    id: int

class TestCaseUpdate(SQLModel):
    module: Optional[str] = None
    title: Optional[str] = None
    precondition: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    priority: Optional[str] = None
    actual_result: Optional[str] = None
    remark: Optional[str] = None
