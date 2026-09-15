# app/rag_tools.py
import os
import vertexai
from vertexai.preview import rag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CORPUS_NAME = "projects/356173146024/locations/us-central1/ragCorpora/3011667901594730496"
PROJECT_ID = "qwiklabs-gcp-02-41b7e175b609"
LOCATION = "us-central1"

_TEXT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pg49513.txt")
_CHUNKS = []
_VECTORIZER = None
_TFIDF_MATRIX = None


def _init_local_index():
    global _CHUNKS, _VECTORIZER, _TFIDF_MATRIX
    if _VECTORIZER is not None:
        return
    if os.path.exists(_TEXT_PATH):
        try:
            with open(_TEXT_PATH, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
            _CHUNKS = [c.strip() for c in raw_text.split("\n\n") if len(c.strip()) > 80]
            if _CHUNKS:
                _VECTORIZER = TfidfVectorizer(stop_words="english")
                _TFIDF_MATRIX = _VECTORIZER.fit_transform(_CHUNKS)
        except Exception as e:
            print(f"Error initializing local index: {e}")


def search_complete_herbal(query: str) -> str:
    """Searches Nicholas Culpeper's 'The Complete Herbal' book for matched passages, herbs, medical uses, and remedies.

    Args:
        query: What to look up (a plant, herb, medical ailment, or remedy, e.g., 'dandelion', 'fever', 'cough').

    Returns:
        Matched text passages and herbal remedies directly from Nicholas Culpeper's The Complete Herbal.
    """
    # 1. Attempt Vertex AI RAG Engine retrieval
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
        if passages:
            return "\n\n---\n\n".join(passages)
    except Exception:
        pass

    # 2. Local semantic retrieval fallback over pg49513.txt
    _init_local_index()
    if _VECTORIZER is not None and _CHUNKS:
        query_vec = _VECTORIZER.transform([query])
        scores = cosine_similarity(query_vec, _TFIDF_MATRIX).flatten()
        top_indices = scores.argsort()[-4:][::-1]
        results = [
            f"From The Complete Herbal:\n{_CHUNKS[idx]}"
            for idx in top_indices
            if scores[idx] > 0.05
        ]
        if results:
            return "\n\n---\n\n".join(results)

    return "No relevant passages found in The Complete Herbal for this query."
