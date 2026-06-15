from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class ProductArrivalIn(BaseModel):
    product_id: str
    name: str
    url: HttpUrl
    image_urls: list[HttpUrl] = Field(default_factory=list)
    price: int | None = None
    brand: str | None = None
    category: str | None = None
    description: str | None = None


class PostContent(BaseModel):
    caption: str
    hashtags: list[str]
    image_urls: list[str]
    product_url: str


class PublishRequest(BaseModel):
    product_id: str
    platform: str
    content: PostContent


class PublishResult(BaseModel):
    platform: str
    external_id: str
    dry_run: bool = False


class JobView(BaseModel):
    id: int
    product_id: str
    platform: str
    status: str
    scheduled_at: datetime
    attempts: int
    error: str | None = None
