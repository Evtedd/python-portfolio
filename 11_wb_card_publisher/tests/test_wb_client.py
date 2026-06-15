from app.wb_client import WBClient


def test_wb_error_parser_reads_common_shapes() -> None:
    errors = WBClient._extract_errors({"errors": [{"message": "limit exceeded"}], "errorText": "bad card"})

    assert errors == ["limit exceeded", "bad card"]
