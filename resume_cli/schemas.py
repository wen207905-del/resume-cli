"""Pydantic schemas for resume extraction and scoring."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EducationItem(BaseModel):
    school: str = ""
    degree: str = ""
    major: str = ""
    start_date: str = ""
    end_date: str = ""


class WorkExperienceItem(BaseModel):
    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class ProjectItem(BaseModel):
    name: str = ""
    role: str = ""
    description: str = ""
    tech_stack: list[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    education: list[EducationItem] = Field(default_factory=list)
    work_experience: list[WorkExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, v: object) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v  # type: ignore[return-value]


class ScoreResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    skill_score: int = Field(ge=0, le=30)
    experience_score: int = Field(ge=0, le=30)
    relevance_score: int = Field(ge=0, le=25)
    completeness_score: int = Field(ge=0, le=15)
    risk_points: list[str] = Field(default_factory=list)
    interview_suggestions: list[str] = Field(default_factory=list)
    summary: str = ""

    @field_validator(
        "overall_score",
        "skill_score",
        "experience_score",
        "relevance_score",
        "completeness_score",
        mode="before",
    )
    @classmethod
    def clamp_score(cls, v: object) -> int:
        if v is None:
            return 0
        try:
            return max(0, min(100, int(float(v))))
        except (TypeError, ValueError):
            return 0


class ExtractResult(BaseModel):
    """Combined extraction + optional scoring output."""

    resume: ResumeData
    score: Optional[ScoreResult] = None
