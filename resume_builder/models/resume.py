"""Pydantic models for resume data structures."""

from pydantic import BaseModel


class JobHistory(BaseModel):
    """Model for work experience entries."""
    title: str
    dates: str
    company: str
    description: str | None = None


class Education(BaseModel):
    """Model for education entries."""
    institution: str
    dates: str | None = None
    field_of_study: str | None = None


class Publications(BaseModel):
    """Model for publication entries."""
    organization: str
    dates: str
    description: str | None = None


class ResumeProcessing(BaseModel):
    """Complete resume data model."""
    name: str
    phone: str
    address: str
    work_history: list[JobHistory]
    skills: list[str] | None = None
    education: list[Education] | None = None
    introduction: str | None = None
    publications: list[Publications] | None = None
    volunteering: list[JobHistory] | None = None
