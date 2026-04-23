"""
AI Service Layer
================
Encapsulates all LLM, embedding, and RAG logic.
Uses OpenAI for chat/embeddings and FAISS for vector storage.
"""

import os
import logging

from django.conf import settings
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OpenAI client (singleton)
# ---------------------------------------------------------------------------
_openai_client = None


def get_openai_client():
    """Return a shared OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


# ---------------------------------------------------------------------------
# Embeddings & FAISS helpers
# ---------------------------------------------------------------------------
def _get_embeddings():
    """Return an OpenAI embeddings instance."""
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
    )


def _get_faiss_store():
    """
    Load the persisted FAISS index from disk.
    Returns None if no index exists yet.
    """
    index_path = settings.FAISS_INDEX_DIR
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        return FAISS.load_local(
            index_path,
            _get_embeddings(),
            allow_dangerous_deserialization=True,
        )
    return None


def _save_faiss_store(store):
    """Persist the FAISS index to disk."""
    os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
    store.save_local(settings.FAISS_INDEX_DIR)
    logger.info("FAISS index saved to %s", settings.FAISS_INDEX_DIR)


# ---------------------------------------------------------------------------
# 1.  ask_ai  –  Direct LLM Q&A with prompt template
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Answer clearly and concisely."
)


def ask_ai(question: str) -> str:
    """
    Send a question directly to the LLM (no retrieval).
    Returns the assistant's answer as a string.
    """
    client = get_openai_client()
    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
        )
        return completion.choices[0].message.content
    except Exception as exc:
        logger.error("OpenAI API error in ask_ai: %s", exc)
        raise


# ---------------------------------------------------------------------------
# 2.  ingest_document  –  Read file → chunk → embed → store in FAISS
# ---------------------------------------------------------------------------
def _read_file_content(file_path: str) -> str:
    """Read text content from a .txt or .pdf file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    # Default: treat as plain text
    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def ingest_document(file_path: str, doc_id: int) -> int:
    """
    Ingest a document into the FAISS vector store.

    1. Read the file content.
    2. Split into chunks (1 000 chars, 200 overlap).
    3. Embed and add to the FAISS index.

    Returns the number of chunks created.
    """
    content = _read_file_content(file_path)
    if not content.strip():
        logger.warning("Document %s has no extractable text.", doc_id)
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_text(content)

    # Build metadata for each chunk
    metadatas = [
        {"doc_id": str(doc_id), "chunk_index": i}
        for i in range(len(chunks))
    ]

    embeddings = _get_embeddings()
    existing_store = _get_faiss_store()

    if existing_store is not None:
        # Merge new chunks into the existing index
        new_store = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)
        existing_store.merge_from(new_store)
        _save_faiss_store(existing_store)
    else:
        # First-time creation
        store = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)
        _save_faiss_store(store)

    logger.info(
        "Ingested document %s: %d chunks stored in FAISS.", doc_id, len(chunks)
    )
    return len(chunks)


# ---------------------------------------------------------------------------
# 3.  rag_query  –  Retrieve relevant chunks then answer with LLM
# ---------------------------------------------------------------------------
RAG_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Answer the user's question based ONLY "
    "on the provided context. If the context does not contain enough "
    "information, say so."
)

RAG_USER_TEMPLATE = (
    "Context:\n{context}\n\n---\nQuestion: {question}\n\nAnswer:"
)


def rag_query(question: str, top_k: int = 4) -> dict:
    """
    RAG pipeline:
      1. Retrieve the top-k most relevant chunks from FAISS.
      2. Build an augmented prompt with the retrieved context.
      3. Call the LLM and return the answer + source metadata.

    Returns {"answer": str, "sources": list[dict]}.
    """
    store = _get_faiss_store()
    if store is None:
        return {
            "answer": "No documents have been ingested yet. "
                      "Please ingest documents first using /api/ingest-doc/.",
            "sources": [],
        }

    # Retrieve relevant documents
    results = store.similarity_search_with_score(question, k=top_k)

    # Build context string and collect source metadata
    context_parts = []
    sources = []
    for doc, score in results:
        context_parts.append(doc.page_content)
        sources.append({
            "doc_id": doc.metadata.get("doc_id"),
            "chunk_index": doc.metadata.get("chunk_index"),
            "score": round(float(score), 4),
            "snippet": doc.page_content[:200],
        })

    context = "\n\n".join(context_parts)

    # Call LLM with augmented prompt
    client = get_openai_client()
    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": RAG_USER_TEMPLATE.format(
                        context=context, question=question
                    ),
                },
            ],
        )
        answer = completion.choices[0].message.content
    except Exception as exc:
        logger.error("OpenAI API error in rag_query: %s", exc)
        raise

    return {"answer": answer, "sources": sources}
