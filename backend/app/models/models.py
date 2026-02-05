from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class RequirementBase(SQLModel):
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Requirement(RequirementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_cases: List["TestCase"] = Relationship(back_populates="requirement", cascade_delete=True)

class RequirementCreate(RequirementBase):
    pass

class RequirementRead(RequirementBase):
    id: int

class RequirementUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
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
