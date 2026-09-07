# InfoCite AI

InfoCite AI is a Retrieval-Augmented Generation (RAG) application that allows users to upload multiple PDF documents and ask questions in natural language. Instead of relying only on the language model, the system first retrieves relevant information from the uploaded documents and then generates answers with supporting citations.

This project was built to explore how modern RAG systems work by combining semantic search, keyword search, reranking, and local LLM inference into one application.

---

## Features

- Upload up to 3 PDF documents
- Automatic PDF parsing and text chunking
- Semantic search using sentence embeddings
- BM25 keyword-based retrieval
- Hybrid retrieval combining semantic and keyword search
- Cross-Encoder reranking for better retrieval quality
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
- Sentence Transformers
- Rank-BM25
- CrossEncoder
- Ollama or an OpenAI-compatible hosted LLM API

### Frontend

- Streamlit
- Custom CSS

### AI Models

| Component| Model |
|----------|-------|
| Embedding Model | all-MiniLM-L6-v2 |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
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
 CrossEncoder Reranker
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

---

## Example

**Question**

```
Do you find the name Shreyas in the campus hiring list?
```

**Answer**

```
Yes. The name "Shreyas" appears twice in the campus hiring list.
```

**Sources**

```
PESU 2026 Campus Hiring - Test Shortlisting.pdf — Page 3

PESU 2026 Campus Hiring - Test Shortlisting.pdf — Page 7
```

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

## Future Improvements

Some ideas for extending the project:

- Support larger document collections
- OCR for scanned PDFs
- Docker deployment
- Metadata-based filtering
- Conversation history

---

## Acknowledgements

This project was built using:

- FastAPI
- Streamlit
- ChromaDB
- Sentence Transformers
- Ollama
- Hugging Face Transformers

---
