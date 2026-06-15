from app.config import SyncTask
from app.transforms import map_row


def test_map_row_normalizes_values() -> None:
    task = SyncTask(
        name="products",
        spreadsheet_id="demo",
        range_name="A:Z",
        table_name="products",
        key_column="sku",
        columns={"SKU": "sku", "Price": "price"},
    )

    row = map_row(task, {"SKU": " A1 ", "Price": "1200"})

    assert row == {"sku": "A1", "price": 1200}
