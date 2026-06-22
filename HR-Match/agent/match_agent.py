import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from prompts import MATCH_AGENT_PROMPT, MATCH_FEWSHOT_EXAMPLE
from llm_client import chat


def match_score(jd: dict, candidate: dict, weights: dict, preferences: str):
    user_prompt = (
        f"<jd>\n{json.dumps(jd, ensure_ascii=False)}\n</jd>\n"
        f"<candidate>\n{json.dumps(candidate, ensure_ascii=False)}\n</candidate>\n"
        f"<weights>\n{json.dumps(weights, ensure_ascii=False)}\n</weights>\n"
        f"<preferences>\n{preferences or '无'}\n</preferences>"
    )
    full_prompt = user_prompt + "\n\n" + MATCH_FEWSHOT_EXAMPLE

    for attempt in range(3):
        response = chat(MATCH_AGENT_PROMPT, full_prompt)
        text = response.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines)
        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError:
            if attempt < 2:
                continue
            return {"overall_score": 0, "error": "LLM 返回格式错误（重试3次失败）"}
    return {"overall_score": 0, "error": "LLM 返回格式错误"}
