# resume-cli

简历 PDF 解析、结构化抽取、JD 匹配评分。支持 **CLI** 和 **Web 拖拽平台**。

## 安装

```bash
pip install -e ".[dev]"
copy .env.example .env   # 填入 DeepSeek Key
```

Key 申请：https://platform.deepseek.com/api_keys

---

## 方式一：Web 平台（推荐）

```bash
resume-cli serve
```

浏览器打开：**http://127.0.0.1:8000**

- 拖拽 PDF 简历上传
- 粘贴 JD 岗位描述
- 点击「结构化抽取」或「JD 匹配评分」

指定端口：

```bash
resume-cli serve --port 8080
```

---

## 方式二：命令行

```bash
resume-cli check
resume-cli extract resume.pdf -o resume.json
resume-cli score resume.pdf --jd examples/jd.txt -o result.json
```

没 Key 时加 `--mock`。

| 命令 | 作用 |
|------|------|
| `serve` | 启动 Web 平台 |
| `check` | 检测 API |
| `parse` | 提取 PDF 文本 |
| `extract` | 抽取 JSON |
| `score` | JD 打分 |

## 测试

```bash
pytest -v
```
