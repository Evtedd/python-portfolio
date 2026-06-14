from app.llm.prompt import build_rag_prompt
from app.retrieval.search import SearchResult


def test_build_rag_prompt_contains_sources_and_question():
    prompt = build_rag_prompt(
        "How to reset password?",
        [
            SearchResult(
                chunk_id=1,
                document="faq.md",
                index=2,
                page=None,
                text="Open profile settings and choose reset password.",
                score=0.9,
            ),
        ],
    )

    assert "faq.md" in prompt
    assert "How to reset password?" in prompt
