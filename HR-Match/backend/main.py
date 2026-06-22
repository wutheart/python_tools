import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import Job, Resume, Match
from schemas import JobCreate, JobResponse, MatchResponse
from agent.coordinator import run_pipeline
from llm_client import chat
from prompts import JD_PROMPT
import json as json_module

app = FastAPI(title="HR-Match")


@app.on_event("startup")
def startup():
    init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/jobs")
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    req = data.requirements
    if isinstance(req, str):
        try:
            req = json_module.loads(req)
        except (json_module.JSONDecodeError, TypeError):
            response = chat(JD_PROMPT, f"<jd>\n{req}\n</jd>")
            text = response.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                text = "\n".join(lines)
            req = json_module.loads(text)

    job = Job(title=data.title, requirements=req, weights=data.weights, preferences=data.preferences)
    db.add(job)
    db.commit()
    return {"id": job.id, "message": "岗位创建成功"}


@app.get("/api/jobs")
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).all()


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return job


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    db.delete(job)
    db.commit()
    return {"message": "岗位已删除"}


@app.delete("/api/jobs/{job_id}/resumes")
def clear_resumes(job_id: int, db: Session = Depends(get_db)):
    db.query(Resume).filter_by(job_id=job_id).delete()
    db.commit()
    return {"message": "候选人已清空"}


@app.post("/api/jobs/{job_id}/upload")
def upload_resume(job_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    content = file.file.read()
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    parsed = run_pipeline(file_path, job.requirements, job.weights, job.preferences)
    if not parsed["success"]:
        raise HTTPException(status_code=500, detail=parsed.get("error", "分析失败"))

    resume = Resume(job_id=job_id, filename=file.filename, raw_text="", parsed_data=parsed["report"])
    db.add(resume)
    db.commit()
    return {"resume_id": resume.id, "filename": file.filename}


@app.get("/api/jobs/{job_id}/ranking")
def get_ranking(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    resumes = db.query(Resume).filter_by(job_id=job_id).all()
    result = []
    for r in resumes:
        result.append({"resume_id": r.id, "filename": r.filename, "parsed": r.parsed_data})
    return sorted(result, key=lambda x: x["parsed"].get("overall_score", 0), reverse=True)


@app.put("/api/jobs/{job_id}/weights")
def update_weights(job_id: int, weights: dict, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    job.weights = weights
    db.commit()
    return {"message": "权重已更新"}


@app.post("/api/jobs/{job_id}/preferences")
def update_preferences(job_id: int, data: dict, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    job.preferences = data.get("text", "")
    db.commit()
    return {"message": "偏好已保存"}
