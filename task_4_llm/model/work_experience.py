"""Pydantic model for work experience entries."""

from typing import Optional

from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    """A single work experience entry from a resume."""

    company: str = Field(description="Company or organization name")
    title: str = Field(description="Job title or role")
    start_date: Optional[str] = Field(
        default=None,
        description="Start date as written on resume",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date as written on resume, or 'Present'",
    )
    description: Optional[str] = Field(
        default=None,
        description="Brief summary of responsibilities and achievements",
    )
