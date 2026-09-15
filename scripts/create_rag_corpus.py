# scripts/create_rag_corpus.py
import sys
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-02-41b7e175b609"
LOCATION = "us-central1"  # Serverless RAG mode is us-central1 only
GCS_PATH = "gs://plottwist-assets-41b7e175b609/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, herbs, medical uses, and descriptions in this text. "
    "Ignore and omit all metadata, boilerplate, and legal notices. "
    "Output clean, self-contained prose."
)

def create_and_import_corpus():
    print(f"Initializing Vertex AI RAG in {LOCATION} for project {PROJECT_ID}...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 1. Configure serverless mode for the region
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    try:
        rag.update_rag_engine_config(
            rag_engine_config=rag.RagEngineConfig(
                name=cfg,
                rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
            )
        )
        print("Updated RAG engine config to serverless mode.")
    except Exception as e:
        print(f"Note on update_rag_engine_config: {e}")

    # 2. Create serverless RAG corpus
    print("Creating RAG corpus 'complete-herbal-corpus'...")
    corpus = rag.create_corpus(
        display_name="complete-herbal-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    print(f"RAG Corpus created successfully: {corpus.name}")

    # 3. Import, parse, chunk, and embed source file
    print(f"Importing and indexing file from {GCS_PATH} into corpus...")
    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print(f"Import complete! Imported files count: {getattr(resp, 'imported_rag_files_count', 'OK')}")
    print(f"\nSaved Corpus Resource Name:\n{corpus.name}")
    return corpus.name

if __name__ == "__main__":
    corpus_name = create_and_import_corpus()
