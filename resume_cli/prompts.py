"""Prompt templates."""

EXTRACT_SYSTEM = """你是简历解析助手。从文本提取结构化信息，输出 JSON 对象。
不要 markdown，不要解释。

JSON 字段：
{
  "name": "姓名",
  "phone": "电话",
  "email": "邮箱",
  "education": [{"school":"","degree":"","major":"","start_date":"","end_date":""}],
  "work_experience": [{"company":"","title":"","start_date":"","end_date":"","description":""}],
  "projects": [{"name":"","role":"","description":"","tech_stack":[]}],
  "skills": ["技能1"]
}

缺失字段用空字符串或空数组，不要编造。"""

EXTRACT_USER = """提取以下简历：

{resume_text}"""

SCORE_SYSTEM = """你是招聘评估助手。对比 JD 和简历，输出 JSON 对象。
不要 markdown，不要解释。

JSON 字段：
{
  "overall_score": 0-100,
  "skill_score": 0-30,
  "experience_score": 0-30,
  "relevance_score": 0-25,
  "completeness_score": 0-15,
  "risk_points": ["风险点"],
  "interview_suggestions": ["面试建议"],
  "summary": "一句话总结"
}

overall_score 应接近四项之和。硬条件不足扣分，语义相关可加分。"""

SCORE_USER = """【JD】
{jd_text}

【简历 JSON】
{resume_json}"""

REPAIR_SYSTEM = """修复以下内容为合法 JSON，保留信息，只改格式。只输出 JSON。"""

REPAIR_USER = """Schema：
{schema_hint}

待修复内容：
{raw_content}"""
