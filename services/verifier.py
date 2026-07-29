class CitationVerifier:
    """
    Handles citation extraction and confidence estimation.
    """

    def extract_pages(self, chunks):
        """
        Extract source document names and page numbers from the
        top-ranked chunks.
        """

        citations = []

        seen = set()

        for chunk in chunks[:3]:

            source = chunk.get("source", "Unknown Document")
            page = chunk.get("page")

            citation = f"{source} — Page {page}"

            if citation not in seen:
                citations.append(citation)
                seen.add(citation)

        return citations

    def format_citations(self, chunks):
        citations = self.extract_pages(chunks)

        if not citations:
            return "Sources: None"

        lines = [f"• {citation}" for citation in citations]

        return "Sources:\n" + "\n".join(lines)

    def confidence(self, chunks):

        if not chunks:
            return "Low"

        score = chunks[0]["cross_score"]

        if score >= 9:
            return "High"

        if score >= 6:
            return "Medium"

        return "Low"