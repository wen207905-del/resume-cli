"""Mock data for --mock mode, no API call needed."""

from resume_cli.schemas import (
    EducationItem,
    ProjectItem,
    ResumeData,
    ScoreResult,
    WorkExperienceItem,
)

MOCK_RESUME = ResumeData(
    name="张明",
    phone="13800138000",
    email="zhangming@example.com",
    education=[
        EducationItem(
            school="某某大学",
            degree="本科",
            major="软件工程",
            start_date="2015",
            end_date="2019",
        )
    ],
    work_experience=[
        WorkExperienceItem(
            company="某某科技",
            title="后端开发工程师",
            start_date="2019",
            end_date="2022",
            description="负责业务后端接口开发与维护，参与微服务拆分。",
        ),
        WorkExperienceItem(
            company="某某互联网",
            title="Python 开发工程师",
            start_date="2022",
            end_date="至今",
            description="参与内部工具链和文档处理模块，对接 OpenAI API 做文本结构化。",
        ),
    ],
    projects=[
        ProjectItem(
            name="文档解析服务",
            role="开发",
            description="PDF/Word 文本提取，接 LLM 做字段抽取，输出 JSON。",
            tech_stack=["Python", "FastAPI", "PyMuPDF"],
        ),
    ],
    skills=["Python", "FastAPI", "PyMuPDF", "OpenAI API", "Docker"],
)

MOCK_SCORE = ScoreResult(
    overall_score=78,
    skill_score=24,
    experience_score=22,
    relevance_score=20,
    completeness_score=12,
    risk_points=["项目描述偏简略，建议补充量化结果"],
    interview_suggestions=[
        "确认 Python 后端实际负责模块",
        "了解 LLM 接入时的异常处理和成本控制",
    ],
    summary="技能栈与 JD 基本匹配，有相关文档处理和 API 对接经验。",
)
