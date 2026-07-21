"""Response generation helpers for the RAG flow."""

from __future__ import annotations

from typing import Sequence


def generate_answer(query: str, documents: Sequence[str]) -> str:
    """Create a simple answer from the supplied context snippets."""
    if not documents:
        return f"I could not find relevant context for: {query}"

    context = "\n\n".join(documents)
    return f"Based on the retrieved context, here is a draft answer to '{query}':\n\n{context}"
