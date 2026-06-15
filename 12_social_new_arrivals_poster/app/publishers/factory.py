from app.config import Settings
from app.publishers.base import Publisher
from app.publishers.instagram import InstagramPublisher
from app.publishers.pinterest import PinterestPublisher


def build_publishers(settings: Settings) -> dict[str, Publisher]:
    publishers = [InstagramPublisher(settings), PinterestPublisher(settings)]
    return {publisher.platform: publisher for publisher in publishers}
