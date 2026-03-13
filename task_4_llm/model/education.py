"""Pydantic model for education entries."""

from typing import Optional

from pydantic import BaseModel, Field


class Education(BaseModel):
    """A single education entry from a resume."""

    institution: str = Field(description="Name of the educational institution")
    degree: Optional[str] = Field(
        default=None,
        description="Degree type (e.g., B.Sc., M.A., Ph.D.)",
    )
    field_of_study: Optional[str] = Field(
        default=None,
        description="Major or field of study",
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date as written on resume",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date as written on resume, or 'Present'",
    )
