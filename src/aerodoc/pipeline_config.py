"""Typed loader for the versioned YAML configuration (`configs/*.yaml`)."""

from pathlib import Path

import yaml
from pydantic import BaseModel

DEFAULT_CONFIG = Path("configs/default.yaml")


class EmbeddingConfig(BaseModel):
    model: str
    dimension: int
    query_prefix: str = ""
    batch_size: int = 32


class ChunkingConfig(BaseModel):
    max_words: int = 250
    overlap_words: int = 40
    min_words: int = 80
    skip_sections: list[str] = []


class RetrievalConfig(BaseModel):
    top_k: int = 5


class PipelineConfig(BaseModel):
    embedding: EmbeddingConfig
    chunking: ChunkingConfig = ChunkingConfig()
    retrieval: RetrievalConfig = RetrievalConfig()


def load_config(path: Path = DEFAULT_CONFIG) -> PipelineConfig:
    return PipelineConfig.model_validate(yaml.safe_load(Path(path).read_text()))
