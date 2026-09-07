import requests
from ollama import chat

from core.config import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_PROVIDER,
    MAX_CONTEXT_CHUNKS,
    TEMPERATURE,
)


class LLMService:
    """
    Handles answer generation using Ollama locally or a hosted
    OpenAI-compatible API for deployment.
    """

    def __init__(self):
        self.model = LLM_MODEL
        self.temperature = TEMPERATURE

    def _generate_with_hosted_provider(self, prompt):
        """
        Generate an answer through a hosted OpenAI-compatible API.

        Credentials and the endpoint must come from environment variables;
        no hosted provider secrets are stored in the repository.
        """

        if not LLM_API_KEY:
            raise ValueError(
                "LLM_API_KEY is required when LLM_PROVIDER=hosted."
            )

        if not LLM_BASE_URL:
            raise ValueError(
                "LLM_BASE_URL is required when LLM_PROVIDER=hosted."
            )

        try:
            response = requests.post(
                f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "temperature": self.temperature,
                },
                timeout=60,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
            detail = getattr(locals().get("response"), "text", str(exc))[:500]
            raise RuntimeError(
                f"Hosted LLM request failed: {detail}"
            ) from exc

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

        if LLM_PROVIDER == "hosted":
            return self._generate_with_hosted_provider(prompt)

        if LLM_PROVIDER != "ollama":
            raise ValueError(
                "Unsupported LLM_PROVIDER. Use 'ollama' or 'hosted'."
            )

        # Local development continues to use Ollama and llama3.2:3b by default.
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