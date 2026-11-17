"""Typed loader for the versioned YAML configuration (`configs/*.yaml`)."""

from pathlib import Path
from typing import Literal

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
    mode: Literal["dense", "bm25", "hybrid"] = "hybrid"
    candidates: int = 30  # chunks taken from each retriever before fusion
    rrf_k: int = 60
    rerank: bool = True
    rerank_top_n: int = 20  # fused candidates re-scored by the cross-encoder
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L6-v2"


class LLMConfig(BaseModel):
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    models: list[str] = ["gemini-3.1-flash-lite", "gemini-3.8-flash"]
    temperature: float = 0.0
    max_tokens: int = 1024
    timeout_s: float = 60
    retries: int = 2


class PipelineConfig(BaseModel):
    embedding: EmbeddingConfig
    chunking: ChunkingConfig = ChunkingConfig()
    retrieval: RetrievalConfig = RetrievalConfig()
    llm: LLMConfig = LLMConfig()


def load_config(path: Path = DEFAULT_CONFIG) -> PipelineConfig:
    return PipelineConfig.model_validate(yaml.safe_load(Path(path).read_text()))
