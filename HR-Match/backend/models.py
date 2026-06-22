from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    requirements = Column(JSON, nullable=False)
    weights = Column(JSON, nullable=False)
    preferences = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    filename = Column(String(200))
    raw_text = Column(Text)
    parsed_data = Column(JSON)
    quality_notes = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)


class Match(Base):
    __tablename__ = "match_records"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    overall_score = Column(Float)
    report = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
