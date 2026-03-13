"""Pydantic model for the complete structured resume."""

from typing import List, Optional

from pydantic import BaseModel, Field

from task_4_llm.model.work_experience import WorkExperience
from task_4_llm.model.education import Education


class ResumeData(BaseModel):
    """Structured data extracted from a resume PDF."""

    name: Optional[str] = Field(
        default=None,
        description="Full name of the candidate",
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number as written on resume",
    )
    education: List[Education] = Field(
        default_factory=list,
        description="List of education entries",
    )
    work_experience: List[WorkExperience] = Field(
        default_factory=list,
        description="List of work experience entries, most recent first",
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of skills mentioned in the resume",
    )
