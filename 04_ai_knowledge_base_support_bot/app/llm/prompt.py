from app.retrieval.search import SearchResult


def build_rag_prompt(question: str, results: list[SearchResult]) -> str:
    context = "\n\n".join(
        f"[{index}] {result.document}, chunk {result.index}: {result.text}"
        for index, result in enumerate(results, start=1)
    )
    return (
        "Answer the user question using only the context below. "
        "If the context is not enough, say that the knowledge base has no answer.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
