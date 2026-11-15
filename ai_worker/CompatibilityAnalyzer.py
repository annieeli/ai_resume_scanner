from functools import lru_cache

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_keyword_model() -> KeyBERT:
    return KeyBERT(model=get_model())


def analyze_compatibility(
    resume_text: str,
    job_description: str,
) -> dict[str, float | list[str]]:
    if not resume_text.strip() or not job_description.strip():
        raise ValueError("Both resume text and job description must be provided.")

    embeddings = get_model().encode(
        [resume_text, job_description],
        convert_to_tensor=True,
        normalize_embeddings=True,
    )
    similarity = float(util.cos_sim(embeddings[0], embeddings[1]).item())

    keyword_model = get_keyword_model()
    job_keywords = {
        keyword.casefold()
        for keyword, _ in keyword_model.extract_keywords(
            job_description,
            keyphrase_ngram_range=(1, 2),
            stop_words="english",
            top_n=10,
        )
    }
    resume_keywords = {
        keyword.casefold()
        for keyword, _ in keyword_model.extract_keywords(
            resume_text,
            keyphrase_ngram_range=(1, 2),
            stop_words="english",
            top_n=10,
        )
    }

    return {
        "semantic_similarity": similarity,
        "job_keywords": sorted(job_keywords),
        "resume_keywords": sorted(resume_keywords),
        "job_keywords_not_found_in_resume": sorted(job_keywords - resume_keywords),
    }