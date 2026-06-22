import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from extractor import extract_file
from llm_client import chat
from prompts import RESUME_AGENT_PROMPT


def parse_resume(file_path: str):
    extracted = extract_file(file_path)
    if not extracted["success"]:
        return {"success": False, "error": extracted["error"]}
    user_prompt = f"<resume>\n{extracted['text']}\n</resume>"
    response = chat(RESUME_AGENT_PROMPT, user_prompt)
    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        text = "\n".join(lines)
    try:
        result = json.loads(text)
        result["success"] = True
        return result
    except json.JSONDecodeError:
        return {"success": False, "error": "LLM 返回格式错误", "raw": response}
