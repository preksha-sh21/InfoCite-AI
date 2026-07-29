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
- Answer using ONLY the provided context.
- Write the answer in your own words.
- Do NOT copy long sentences from the document.
- Be concise, clear, and technically accurate.
- If multiple context chunks are relevant, combine them into one coherent answer.
- If the answer cannot be found in the context, reply exactly:
  "I don't have enough information in the provided document."
- At the end, mention the page numbers used in this format:
  Sources: Page 64, Page 81

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