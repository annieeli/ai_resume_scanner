FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 \
    && pip install --no-cache-dir -r requirements.txt

COPY ResumeAnalyze.py .
COPY CompatibilityAnalyzer.py .

CMD ["python", "-u", "ResumeAnalyze.py"]