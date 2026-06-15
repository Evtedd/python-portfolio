from app.schemas import PostContent, ProductArrivalIn


class ContentBuilder:
    def build(self, product: ProductArrivalIn) -> PostContent:
        caption_parts = [product.name]
        if product.brand:
            caption_parts.append(f"Бренд: {product.brand}")
        if product.price:
            caption_parts.append(f"Цена: {product.price} руб.")
        if product.description:
            caption_parts.append(product.description[:300])
        return PostContent(
            caption="\n".join(caption_parts),
            hashtags=self._hashtags(product),
            image_urls=[str(url) for url in product.image_urls],
            product_url=str(product.url),
        )

    def _hashtags(self, product: ProductArrivalIn) -> list[str]:
        words = ["новинка"]
        if product.category:
            words.append(product.category)
        if product.brand:
            words.append(product.brand)
        clean = []
        for word in words:
            tag = "".join(char for char in word.lower() if char.isalnum() or char == "_")
            if tag:
                clean.append(f"#{tag}")
        return clean[:8]
