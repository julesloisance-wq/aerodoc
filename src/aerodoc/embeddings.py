"""Turn texts into vectors with a sentence-transformers model (runs on CPU)."""

from functools import lru_cache

import numpy as np

from aerodoc.pipeline_config import EmbeddingConfig


@lru_cache(maxsize=2)
def _model(name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(name, device="cpu")


def embed_passages(texts: list[str], cfg: EmbeddingConfig, show_progress: bool = False):
    model = _model(cfg.model)
    return model.encode(
        texts,
        batch_size=cfg.batch_size,
        normalize_embeddings=True,  # unit vectors: cosine similarity = dot product
        show_progress_bar=show_progress,
        convert_to_numpy=True,
    ).astype(np.float32)


def embed_query(query: str, cfg: EmbeddingConfig):
    return embed_passages([cfg.query_prefix + query], cfg)[0]
