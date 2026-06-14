from app.ingestion.chunker import chunk_text


def test_chunk_text_with_overlap():
    text = " ".join(f"word{i}" for i in range(10))

    chunks = chunk_text(text, chunk_size=4, overlap=1)

    assert [chunk.text for chunk in chunks] == [
        "word0 word1 word2 word3",
        "word3 word4 word5 word6",
        "word6 word7 word8 word9",
    ]
