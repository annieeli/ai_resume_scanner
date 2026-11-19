FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY ResumeAnalyze.py .
COPY JobStatus.py .
COPY CompatibilityAnalyzer.py .
COPY compatibility_instructions.txt .

CMD ["python", "-u", "ResumeAnalyze.py"]