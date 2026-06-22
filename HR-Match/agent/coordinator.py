import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent))
from resume_agent import parse_resume
from match_agent import match_score


def run_pipeline(resume_path: str, jd: dict, weights: dict, preferences: str = "") -> dict:
    candidate = parse_resume(resume_path)
    if not candidate.get("success"):
        return {"success": False, "error": candidate.get("error", "简历解析失败")}
    report = match_score(jd, candidate, weights, preferences)
    report["candidate_name"] = candidate.get("name", "未知")
    report["candidate_skills"] = candidate.get("skills", [])
    return {"success": True, "report": report}
