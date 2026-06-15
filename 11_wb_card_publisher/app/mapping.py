from app.sources import RawProduct
from app.wb_client import WBCharacteristic, WBProductCard, WBSize


def product_to_card(product: RawProduct) -> WBProductCard:
    characteristics = [
        WBCharacteristic(id=14177449, name="Цвет", value=product.color),
        WBCharacteristic(id=14177451, name="Страна производства", value=product.country),
    ]
    for index, (name, value) in enumerate(product.extra_characteristics.items(), start=900000):
        characteristics.append(WBCharacteristic(id=index, name=name, value=value))
    return WBProductCard(
        vendorCode=product.vendor_code,
        subjectID=product.subject_id,
        subjectName=product.subject_name,
        brand=product.brand,
        title=build_title(product),
        description=build_description(product),
        characteristics=characteristics,
        sizes=[WBSize(techSize=product.size, price=product.price, skus=[product.barcode])],
        media_urls=product.media_urls,
    )


def build_title(product: RawProduct) -> str:
    title = product.title or product.name
    if product.brand.lower() not in title.lower():
        title = f"{product.brand} {title}"
    return title[:60].strip()


def build_description(product: RawProduct) -> str:
    base = product.description or product.name
    color_part = f" Цвет: {product.color}." if product.color else ""
    return f"{base.strip()}{color_part}".strip()[:2000]
