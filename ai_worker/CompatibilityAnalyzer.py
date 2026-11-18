import json
import math
import os
from pathlib import Path
from typing import TypedDict

from openai import OpenAI


INSTRUCTIONS_PATH = Path(__file__).with_name("compatibility_instructions.txt")


class CompatibilityAnalysis(TypedDict):
    score: float
    matching_requirements: list[str]
    gaps_or_unverified_requirements: list[str]


def parse_analysis(output_text: str) -> CompatibilityAnalysis:

    #ensures it is valid JSON
    try:
        result = json.loads(output_text)
    except json.JSONDecodeError as error:
        raise ValueError("The AI response was not valid JSON.") from error

    #ensures expected fields
    expected_fields = {
        "score",
        "matching_requirements",
        "gaps_or_unverified_requirements",
    }
    if not isinstance(result, dict) or set(result) != expected_fields:
        raise ValueError("The AI response did not match the expected analysis shape.")

    #ensures the score is numeric and within range, and lists contain strings.
    score = result["score"]
    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(score)
        or not 0 <= score <= 100
    ):
        raise ValueError("The analysis score must be a number from 0 to 100.")

    string_lists: dict[str, list[str]] = {}
    for field in expected_fields - {"score"}:
        value = result[field]
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ValueError(f"The analysis field '{field}' must be a list of strings.")
        string_lists[field] = value

    return {
        "score": float(score),
        "matching_requirements": string_lists["matching_requirements"],
        "gaps_or_unverified_requirements": string_lists[
            "gaps_or_unverified_requirements"
        ],
    }


def analyze_compatibility(
    resume_text: str,
    job_description: str,
) -> CompatibilityAnalysis:

    #ensures both resume and job description are provided
    if not resume_text.strip() or not job_description.strip():
        raise ValueError("Both resume text and job description must be provided.")

    #ensures required environment variables are set for azure openai
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    if not endpoint or not deployment or not api_key:
        raise RuntimeError(
            "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, and "
            "AZURE_OPENAI_API_KEY must be configured."
        )

    #creates an openai client and sends a request to analyze the compatibility between the resume and job description
    client = OpenAI(
        api_key=api_key,
        base_url=f"{endpoint.rstrip('/')}/",
        timeout=120.0,
    )

    response = client.responses.create(
        model=deployment,
        instructions=INSTRUCTIONS_PATH.read_text(encoding="utf-8"),
        input=json.dumps(
            {
                "resume_text": resume_text,
                "job_description": job_description,
            },
            ensure_ascii=False,
        ),
        reasoning={"effort": "low"},
        text={"format": {"type": "json_object"}},
        #ensures the response is not too long
        max_output_tokens=4000,
    )

    if response.status != "completed" or not response.output_text.strip():
        raise ValueError(
            f"Incomplete AI response (status={response.status}, "
            f"details={response.incomplete_details})"
        )

    return parse_analysis(response.output_text)
