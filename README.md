# resume-cli

简历 PDF 解析、结构化抽取、JD 匹配评分的命令行工具。

## 安装

```bash
pip install -e ".[dev]"
cp .env.example .env   # 填入 DeepSeek API Key
```

默认走 [DeepSeek](https://platform.deepseek.com) OpenAI 兼容接口，新用户有免费额度。Key 在控制台 → API Keys 申请。

`.env` 示例：

```env
OPENAI_API_KEY=sk-你的deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

## 用法

```bash
resume-cli parse resume.pdf
resume-cli extract resume.pdf          # 需 .env 里配 DeepSeek Key
resume-cli score resume.pdf --jd examples/jd.txt -o result.json
```

| 命令 | 作用 |
|------|------|
| `parse` | 提取 PDF 文本 |
| `extract` | 抽取姓名、经历、技能等 JSON |
| `score` | 按 JD 打分 |

`--mock` 不调用 API，本地看输出格式。`--output` / `-o` 写文件。

## 评分

总分 100，四块：技能 30、经验 30、岗位相关 25、完整度 15。模型出分后还会跑一轮规则（关键词、必填字段、年限）。

## 目录

```
resume_cli/     主代码
tests/          pytest
examples/jd.txt 示例 JD
```

## 测试 & Docker

```bash
pytest -v
docker build -t resume-cli .
```
