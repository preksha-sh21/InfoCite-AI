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

        for chunk in chunks[:5]:

            source = chunk.get("source", "Unknown Document")
            page = chunk.get("page")

            citation_id = chunk.get("citation_id", len(citations) + 1)
            citation = f"[{citation_id}] {source} — Page {page}"

            if citation not in seen:
                citations.append(citation)
                seen.add(citation)

        return citations

    def assign_citation_ids(self, chunks):
        """Assign stable citation numbers to each unique document page."""
        citation_ids = {}
        for chunk in chunks:
            key = (chunk.get("source"), chunk.get("page"))
            if key not in citation_ids:
                citation_ids[key] = len(citation_ids) + 1
            chunk["citation_id"] = citation_ids[key]
        return chunks

    def extract_evidence(self, chunks):
        """
        Extract the retrieved text along with its source and page.
        """

        evidence = []

        seen = set()

        for chunk in chunks[:5]:

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
                "citation_id": chunk.get("citation_id"),
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
