class CitationVerifier:
    """
    Handles citation extraction, evidence extraction,
    and confidence estimation.
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

    def extract_evidence(self, chunks):
        """
        Extract the retrieved text along with its source and page.
        """

        evidence = []

        seen = set()

        for chunk in chunks[:3]:

            source = chunk.get("source", "Unknown Document")
            page = chunk.get("page")
            text = chunk.get("text", "").strip()

            citation = f"{source} — Page {page}"

            if citation in seen:
                continue

            if not text:
                continue

            evidence.append({
                "source": source,
                "page": page,
                "text": text,
            })

            seen.add(citation)

        return evidence

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