"""Small public helper for querying an initialized hybrid retriever."""


def retrieve_documents(hybrid_retriever, query: str, top_k: int = 5):
    """Retrieve ranked document chunks using the configured hybrid retriever."""
    return hybrid_retriever.retrieve(query=query, top_k=top_k)


__all__ = ["retrieve_documents"]
