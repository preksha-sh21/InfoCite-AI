class CitationVerifier:
    """
    Handles citation extraction and confidence estimation.
    """

    def extract_pages(self, chunks):

        pages = {
            chunk.get("page")
            for chunk in chunks
            if chunk.get("page") is not None
        }

        return sorted(pages)

    def format_citations(self, chunks):

        pages = self.extract_pages(chunks)

        if not pages:
            return "Sources: None"

        lines = [f"• Page {page}" for page in pages]

        return "Sources:\n" + "\n".join(lines)

    def confidence(self, chunks):
        """
        Estimate confidence from the top CrossEncoder score.
        """

        if not chunks:
            return "Low"

        score = chunks[0]["cross_score"]

        if score >= 9:
            return "High"

        if score >= 6:
            return "Medium"

        return "Low"