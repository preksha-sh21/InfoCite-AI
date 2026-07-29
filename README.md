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
- Local Llama 3.2 inference using Ollama
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
- Ollama

### Frontend

- Streamlit
- Custom CSS

### AI Models

| Component| Model |
|----------|-------|
| Embedding Model | all-MiniLM-L6-v2 |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| LLM | Llama 3.2 |

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
     Llama 3.2 (Ollama)
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
