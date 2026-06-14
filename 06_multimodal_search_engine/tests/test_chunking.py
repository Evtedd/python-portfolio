from app.chunking.text import chunk_words


def test_chunk_words_keeps_overlap():
    text = " ".join(str(index) for index in range(8))

    chunks = chunk_words(text, size=4, overlap=1)

    assert [chunk.text for chunk in chunks] == ["0 1 2 3", "3 4 5 6", "6 7"]
