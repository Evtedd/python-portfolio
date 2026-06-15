from app.validation import validate_row


def test_validation_reports_broken_key() -> None:
    error = validate_row({"sku": ""}, "sku", 3)

    assert error is not None
    assert error.row_number == 3
