from app.core.config import settings
from app.providers.embeddings.hosted_provider import HostedEmbeddingProvider
from app.providers.embeddings.local_provider import LocalEmbeddingProvider
from app.providers.reranker.heuristic_provider import HeuristicRerankerProvider
from app.providers.llm.local_provider import LocalLLMProvider


def get_embedding_provider():
    if settings.embedding_provider == "local":
        return LocalEmbeddingProvider()
    elif settings.embedding_provider == "hosted":
        return HostedEmbeddingProvider()
    else:
        raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {settings.embedding_provider}")

def get_llm_provider():
    if settings.llm_provider == "local":
        return LocalLLMProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")

def get_reranking_provider():
    if settings.reranker_provider == "heuristic":
        return HeuristicRerankerProvider()
    raise ValueError(f"Unsupported RERANKING_PROVIDER: {settings.reranking_provider}")
