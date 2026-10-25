class CitationVerifier:
    """
    Handles citation extraction, evidence extraction,
    and heuristic evidence-match labeling.
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

    def evidence_match(self, chunks):
        """Return a rough evidence-match label, not answer confidence."""

        if not chunks:
            return "Low"

        score = chunks[0].get("lexical_score", 0.0)

        if score >= 0.7:
            return "High"

        if score >= 0.4:
            return "Medium"

        return "Low"
