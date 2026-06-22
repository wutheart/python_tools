from pydantic import BaseModel
from typing import Optional, Union


class JobCreate(BaseModel):
    title: str
    requirements: Union[dict, str]
    weights: dict = {"skills": 50, "education": 20, "experience": 30}
    preferences: str = ""


class JobResponse(BaseModel):
    id: int
    title: str
    requirements: dict
    weights: dict
    preferences: str
    created_at: str


class MatchRequest(BaseModel):
    job_id: int
    resume_id: int


class MatchResponse(BaseModel):
    resume_id: int
    filename: str
    overall_score: float
    report: dict
