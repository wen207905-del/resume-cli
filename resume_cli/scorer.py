"""Rule-based + AI hybrid JD matching scorer."""

from __future__ import annotations

import json
import re

from resume_cli.ai_client import AIClient
from resume_cli.mock_data import MOCK_SCORE
from resume_cli.prompts import SCORE_SYSTEM, SCORE_USER
from resume_cli.schemas import ResumeData, ScoreResult


def _keyword_bonus(resume: ResumeData, jd_text: str) -> tuple[int, list[str]]:
    """Rule-based keyword matching for skill hints."""
    jd_lower = jd_text.lower()
    skills_lower = [s.lower() for s in resume.skills]
    bonus = 0
    matched: list[str] = []

    keyword_groups = [
        (["python"], "Python"),
        (["agent", "智能体"], "Agent"),
        (["rag", "知识库"], "RAG"),
        (["llm", "大模型", "gpt"], "LLM"),
        (["fastapi", "后端"], "后端"),
        (["docker"], "Docker"),
    ]

    for keywords, label in keyword_groups:
        jd_hit = any(k in jd_lower for k in keywords)
        resume_hit = any(
            any(k in skill for k in keywords) for skill in skills_lower
        ) or any(
            any(k in (p.description + " ".join(p.tech_stack)).lower() for k in keywords)
            for p in resume.projects
        )
        if jd_hit and resume_hit:
            bonus += 2
            matched.append(label)

    return min(bonus, 10), matched


def _rule_adjustments(resume: ResumeData, jd_text: str, score: ScoreResult) -> ScoreResult:
    """Apply deterministic rule adjustments on top of AI scores."""
    data = score.model_dump()
    risks = list(data.get("risk_points") or [])

    if not resume.name or not resume.phone:
        data["completeness_score"] = max(0, data["completeness_score"] - 5)
        risks.append("基础联系信息不完整")

    if not resume.work_experience:
        data["experience_score"] = max(0, data["experience_score"] - 10)
        risks.append("缺少工作经历")

    if not resume.skills:
        data["skill_score"] = max(0, data["skill_score"] - 8)
        risks.append("技能栈未明确列出")

    years_pattern = re.search(r"(\d+)\s*年", jd_text)
    if years_pattern:
        required_years = int(years_pattern.group(1))
        exp_count = len(resume.work_experience)
        if exp_count < required_years // 2:
            data["experience_score"] = max(0, data["experience_score"] - 5)
            risks.append(f"JD 要求约 {required_years} 年经验，简历经历偏少")

    keyword_bonus, matched = _keyword_bonus(resume, jd_text)
    if matched:
        data["skill_score"] = min(30, data["skill_score"] + min(keyword_bonus, 5))

    data["risk_points"] = list(dict.fromkeys(risks))
    data["overall_score"] = min(
        100,
        data["skill_score"]
        + data["experience_score"]
        + data["relevance_score"]
        + data["completeness_score"],
    )
    return ScoreResult.model_validate(data)


def score_resume(resume: ResumeData, jd_text: str, client: AIClient) -> ScoreResult:
    if client.mock:
        return MOCK_SCORE.model_copy(deep=True)

    user_prompt = SCORE_USER.format(
        jd_text=jd_text,
        resume_json=json.dumps(resume.model_dump(), ensure_ascii=False, indent=2),
    )
    ai_score = client.parse_structured(
        ScoreResult,
        SCORE_SYSTEM,
        user_prompt,
        schema_hint=ScoreResult.model_json_schema(),
    )
    return _rule_adjustments(resume, jd_text, ai_score)
