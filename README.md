# InfoCite AI

InfoCite AI is a Retrieval-Augmented Generation (RAG) application that allows users to upload multiple PDF documents and ask questions in natural language. Instead of relying only on the language model, the system first retrieves relevant information from the uploaded documents and then generates answers with supporting citations.

This project explores retrieval-augmented generation by combining semantic search, BM25 keyword search, reciprocal-rank fusion, lightweight lexical reranking, and local or hosted LLM inference.

---

## Features

- Upload up to 3 PDF documents
- Automatic PDF parsing and text chunking
- Semantic search using sentence embeddings
- BM25 keyword-based retrieval
- Hybrid retrieval combining semantic and keyword search
- Lightweight lexical reranking based on query term coverage
- Configurable local Ollama or hosted LLM inference
- Answers with page-level citations
- FastAPI backend
- Streamlit frontend with a custom neon-inspired interface

---

## Tech Stack

### Backend

- Python 3.9
- FastAPI
- ChromaDB
- ONNX Runtime and Hugging Face Hub
- Rank-BM25
- Ollama or an OpenAI-compatible hosted LLM API

### Frontend

- Streamlit
- Custom CSS

### AI Models

| Component| Model |
|----------|-------|
| Embedding Model | sentence-transformers/all-MiniLM-L6-v2 (ONNX inference) |
| Reranker | Query term coverage (lexical heuristic; not a neural cross-encoder) |
| LLM | Llama 3.2 locally, or the configured hosted model |

---

## How It Works

```
          User
            │
            ▼
     Streamlit Frontend
            │
            ▼
        FastAPI Backend
            │
            ▼
        RAG Pipeline
            │
     ┌──────┴──────┐
     ▼             ▼
Semantic Search   BM25 Search
     │             │
     └──────┬──────┘
            ▼
     Hybrid Retrieval
            │
            ▼
 Lexical Reranker
            │
            ▼
       Configured LLM provider
            │
            ▼
 Answer + Source Citations
```

---


## Using the Application

1. Upload one or more PDF documents.
2. Click **Index Documents**.
3. Wait for indexing to complete.
4. Ask a question related to the uploaded documents.
5. The application retrieves the most relevant information and generates an answer with citations.

## Run Locally

Use Python 3.9 or newer. In one terminal, install dependencies and start the API:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull llama3.2:3b
uvicorn api.main:app --reload
```

In a second terminal, start the Streamlit interface:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```

The first indexing request downloads the embedding model from Hugging Face. For hosted inference, set `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` as described below.

---

## Project Structure

```
InfoCite_AI
│
├── api/
├── core/
├── frontend/
├── models/
├── services/
├── scripts/
├── data/
├── chroma_db/
├── uploaded_pdfs/
├── requirements.txt
├── README.md
└── .gitignore
```

---

## LLM Configuration

Ollama remains the default provider for local development. Install and start
Ollama, then make sure the local model is available:

```powershell
ollama pull llama3.2:3b
$env:LLM_PROVIDER = "ollama"
$env:LLM_MODEL = "llama3.2:3b"
```

For Render, select the hosted OpenAI-compatible provider. Set these environment
variables in the Render service settings. Keep the API key in Render's secret
environment variable storage; do not commit it to this repository.

```text
LLM_PROVIDER=hosted
LLM_API_KEY=<your-hosted-provider-api-key>
LLM_BASE_URL=<your-provider-openai-compatible-base-url>
LLM_MODEL=<your-provider-model-name>
```

`LLM_BASE_URL` should be the provider's OpenAI-compatible API base, without the
`/chat/completions` suffix. The application appends that path automatically.

The hosted provider uses the existing `requests` dependency, so no additional
package is required. The RAG retrieval and response pipeline is unchanged.

---

## Current Limitations

- The lexical reranker and `evidence_match` label are heuristics, not a trained relevance model or calibrated answer-confidence estimate.
- PDF text extraction does not currently perform OCR, so image-only scans may produce no usable text.
- The upload limit is three PDFs and indexes are held by the running API process.

## Roadmap

- Add a labeled retrieval benchmark and report Recall@K / MRR.
- Replace the lexical heuristic with an evaluated neural reranker.
- Add OCR for scanned PDFs.
- Support larger document collections
- Docker deployment
- Metadata-based filtering
- Conversation history

---

## Acknowledgements

This project uses:

- FastAPI
- Streamlit
- ChromaDB
- ONNX Runtime
- Hugging Face Hub
- Ollama

---
