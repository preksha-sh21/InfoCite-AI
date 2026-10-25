# InfoCite AI

InfoCite AI is a Retrieval-Augmented Generation (RAG) application that allows users to upload multiple PDF documents and ask questions in natural language. Instead of relying only on the language model, the system first retrieves relevant information from the uploaded documents and then generates answers with supporting citations.

InfoCite AI is a document research workspace. It combines semantic search, BM25 keyword search, reciprocal-rank fusion, an ONNX cross-encoder, and local or hosted LLM inference to answer questions with page-level evidence.

---

## Features

- Upload up to 10 PDFs per workspace; add, replace, or remove documents
- Session-isolated document indexes, purged after 24 hours of inactivity
- Automatic PDF parsing and text chunking
- Best-effort extraction of bordered PDF tables into retrieval-friendly text
- Optional OCR for scanned PDFs (requires Tesseract)
- Semantic search using sentence embeddings
- BM25 keyword-based retrieval
- Hybrid retrieval combining semantic and keyword search
- Cross-encoder reranking with a quantized ONNX model
- Configurable local Ollama or hosted LLM inference
- Inline citation markers and page previews from the source PDF
- Follow-up questions with short conversation history
- Retrieval evaluation against a small labeled question set
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
| Reranker | cross-encoder/ms-marco-MiniLM-L6-v2 (quantized ONNX) |
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
 Cross-Encoder Reranker (ONNX)
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
5. The application retrieves and reranks relevant passages, then answers with numbered citations and page evidence.

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

The first question also downloads the reranker model. To OCR image-only pages, install Tesseract with English language data and set `PDF_OCR_ENABLED=true`. `PDF_OCR_LANGUAGE` and `PDF_OCR_DPI` configure the OCR language and resolution.

Table extraction is enabled by default through PyMuPDF and can be disabled with `PDF_TABLE_EXTRACTION_ENABLED=false`. Detection depends on how tables are drawn in the PDF; borderless or image-only tables may need OCR or manual processing.

## Evaluate Retrieval

Run the labeled CUDA guide benchmark:

```powershell
python scripts/evaluate_retrieval.py
```

The script compares hybrid retrieval with hybrid retrieval plus cross-encoder reranking. It reports Hit Rate@5, MRR@5, page Recall@5, and average retrieval/reranking time. The benchmark is small and intended for regression checks, not a claim of general RAG quality. It uses `data/raw/cuda_programming_guide.pdf` and a temporary Chroma collection that is removed after the run.

## Workspace Isolation

Each browser session receives a random workspace ID, and the API stores its PDFs and vectors separately. The ID is scoped to that browser session; the app does not currently provide account login or cross-device workspace recovery. Workspaces with no activity for 24 hours are purged the next time the API processes a request.

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
package is required. Local Ollama and hosted inference use the same retrieval
and citation pipeline.

---

## Current Limitations

- `evidence_match` remains a query-word overlap heuristic, not calibrated answer confidence.
- OCR is optional and requires Tesseract to be installed on the API host.
- Table extraction is best-effort; PyMuPDF's detector may miss tables without clear borders or table structure.
- Workspace isolation is anonymous session isolation, not user authentication; the API is intended for a controlled demo until authentication and rate limits are added.
- The current in-memory BM25 index is rebuilt from saved PDFs after an API restart. Run a single API instance for now.

## Roadmap

- Tune the abstention threshold using a larger answerable and unanswerable evaluation set.
- Add authenticated accounts and durable workspace recovery.
- Add background indexing jobs and progress reporting for large PDFs.
- Improve table extraction and add more document formats.
- Add deployment monitoring and rate limits.

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
