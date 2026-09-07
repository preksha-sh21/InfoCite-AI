from ollama import chat

from core.config import (
    LLM_MODEL,
    MAX_CONTEXT_CHUNKS,
    TEMPERATURE,
)


class LLMService:
    """
    Handles answer generation using a local Ollama model.
    """

    def __init__(self):
        self.model = LLM_MODEL
        self.temperature = TEMPERATURE

    def _build_context(self, chunks):
        """
        Convert retrieved chunks into a formatted context string.
        """

        context_parts = []

        for chunk in chunks[:MAX_CONTEXT_CHUNKS]:
            page = chunk.get("page", "Unknown")
            text = chunk.get("text", "")

            context_parts.append(
                f"""
Page {page}
{'-' * 60}
{text}
"""
            )

        return "\n".join(context_parts)

    def _generate_prompt(self, query, context):
        """
        Build the prompt sent to the LLM.
        """

        return f"""
You are InfoCite AI, an expert technical assistant.

Answer the user's question ONLY using the provided context.

Requirements:
- Use ONLY the provided context.
- Write the answer in your own words.
- Give a clear and sufficiently detailed answer based on the available context.
- Do not give an unnecessarily short one-sentence answer when the context contains more relevant information.
- Explain the main points rather than simply naming or pointing to them.
- Combine information from multiple context chunks when appropriate.
- Include relevant details from the context that directly help answer the question.
- For questions asking about a topic, provide a short explanatory paragraph.
- For questions asking about multiple items, use a short bullet list when appropriate.
- If the context contains several relevant details, include the important ones rather than mentioning only one.
- Do NOT copy long passages from the document.
- Do NOT invent, assume, or infer unsupported information.
- If only limited information is available, clearly state what can be determined from the context.
- Do NOT include page numbers.
- Do NOT include citations.
- Do NOT include a "Sources" section.
- Return ONLY the answer.
- If the answer cannot be found in the provided context, reply exactly:
    "I don't have enough information in the provided documents."

Context:
{context}

Question:
{query}

Answer:
"""

    def generate_answer(self, query, chunks):
        """
        Generate an answer using the retrieved context.
        """

        context = self._build_context(chunks)

        prompt = self._generate_prompt(
            query=query,
            context=context,
        )

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": self.temperature,
            },
        )

        return response["message"]["content"]