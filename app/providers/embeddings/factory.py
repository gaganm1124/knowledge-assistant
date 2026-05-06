from app.core.config import settings
from app.providers.embeddings.hosted_provider import HostedEmbeddingProvider
from app.providers.embeddings.local_provider import LocalEmbeddingProvider


def get_embedding_provider():
    if settings.embedding_provider == "local":
        return LocalEmbeddingProvider()
    elif settings.embedding_provider == "hosted":
        return HostedEmbeddingProvider()
    else:
        raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {settings.embedding_provider}")
