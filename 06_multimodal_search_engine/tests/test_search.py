from app.vectorstore.math import cosine_similarity


def test_cosine_similarity_ranks_matching_vectors():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) > cosine_similarity(
        [1.0, 0.0],
        [0.0, 1.0],
    )
