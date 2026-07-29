from services.rag_pipeline import RAGPipeline


def main():

    pipeline = RAGPipeline()

    while True:

        question = input("\nQuestion: ")

        if question.lower() == "exit":
            break

        result = pipeline.ask(question)

        print("\nANSWER")
        print("=" * 80)
        print(result["answer"])

        print("\nSources:")
        for page in result["sources"]:
            print(f"• Page {page}")

        print(f"\nConfidence: {result['confidence']}")


if __name__ == "__main__":
    main()