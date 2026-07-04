# resume-cli

简历 PDF 解析、结构化抽取、JD 匹配评分的命令行工具。默认对接 DeepSeek API。

## 安装

```bash
pip install -e ".[dev]"
copy .env.example .env
```

编辑 `.env`，把 `OPENAI_API_KEY` 换成你的 DeepSeek Key：  
https://platform.deepseek.com/api_keys

## 使用流程

```bash
# 1. 检查 API 是否通
resume-cli check

# 2. 解析 PDF 文本（不调 API）
resume-cli parse resume.pdf

# 3. 结构化抽取
resume-cli extract resume.pdf -o resume.json

# 4. JD 匹配评分
resume-cli score resume.pdf --jd examples/jd.txt -o result.json
```

没 Key 时加 `--mock` 看输出格式。

| 命令 | 作用 |
|------|------|
| `check` | 检测 API 配置 |
| `parse` | 提取 PDF 文本 |
| `extract` | 抽取 JSON |
| `score` | JD 打分 |

## 配置说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENAI_API_KEY` | - | DeepSeek API Key |
| `OPENAI_BASE_URL` | `https://api.deepseek.com` | 接口地址 |
| `OPENAI_MODEL` | `deepseek-chat` | 模型名 |
| `API_TIMEOUT` | `60` | 请求超时（秒） |
| `MAX_RESUME_CHARS` | `15000` | 简历文本截断长度 |
| `JSON_MODE` | `true` | 强制 JSON 输出 |

## 测试

```bash
pytest -v
docker build -t resume-cli .
```
