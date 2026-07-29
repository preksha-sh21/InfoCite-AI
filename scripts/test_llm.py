from services.llm import LLMService


def main():
    llm = LLMService()

    chunks = [
    {
        "page": 163,
        "text": """
Warp scheduling is the mechanism used by a Streaming Multiprocessor (SM)
to select one of the ready warps for execution every clock cycle.

Each SM contains multiple warp schedulers.
Warp scheduling helps hide memory latency by switching
between ready warps whenever another warp stalls.
"""
    }
]

    query = "What is warp scheduling?"

    answer = llm.generate_answer(query, chunks)

    print("\nGenerated Answer:\n")
    print(answer)


if __name__ == "__main__":
    main()