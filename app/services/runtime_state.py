from app.core.config import settings
from app.services.cache_service import CacheService

query_cache = CacheService(ttl_seconds=settings.cache_ttl_seconds)
