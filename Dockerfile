FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY resume_cli/ ./resume_cli/
COPY pyproject.toml README.md ./

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["resume-cli"]
CMD ["--help"]
