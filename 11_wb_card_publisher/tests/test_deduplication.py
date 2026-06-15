from app.service import _chunks
from app.wb_client import WBProductCard


def test_chunks_keep_batch_size() -> None:
    cards = [
        WBProductCard(
            vendorCode=str(index),
            subjectID=1,
            subjectName="A",
            brand="B",
            title="T",
            description="D",
            characteristics=[],
            sizes=[],
        )
        for index in range(5)
    ]

    assert [len(chunk) for chunk in _chunks(cards, 2)] == [2, 2, 1]
