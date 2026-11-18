# AeroDoc image: API (FastAPI) and web interface (Streamlit) share it.
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    HF_HOME=/app/.hf \
    PATH=/app/.venv/bin:$PATH
WORKDIR /app

# Optional extra CA certificate (only needed behind a TLS-intercepting proxy):
#   docker build --secret id=ca,src=/path/to/ca.crt .
# Without the secret, the system certificates are used.
RUN --mount=type=secret,id=ca,required=false \
    if [ -f /run/secrets/ca ]; then export PIP_CERT=/run/secrets/ca; fi; \
    pip install --no-cache-dir uv==0.11.32

# Dependencies first (cached layer), CPU-only PyTorch as pinned in uv.lock.
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=secret,id=ca,required=false --mount=type=cache,target=/root/.cache/uv \
    if [ -f /run/secrets/ca ]; then export SSL_CERT_FILE=/run/secrets/ca UV_NATIVE_TLS=1; fi; \
    uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY configs ./configs
COPY .streamlit ./.streamlit
RUN --mount=type=secret,id=ca,required=false --mount=type=cache,target=/root/.cache/uv \
    if [ -f /run/secrets/ca ]; then export SSL_CERT_FILE=/run/secrets/ca UV_NATIVE_TLS=1; fi; \
    uv sync --frozen --no-dev

# Bake the embedding model and the reranker into the image (no download at runtime).
RUN --mount=type=secret,id=ca,required=false \
    if [ -f /run/secrets/ca ]; then export SSL_CERT_FILE=/run/secrets/ca REQUESTS_CA_BUNDLE=/run/secrets/ca; fi; \
    python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('BAAI/bge-small-en-v1.5'); CrossEncoder('cross-encoder/ms-marco-MiniLM-L6-v2')"


# Models are baked in: never try to reach Hugging Face at runtime.
ENV HF_HUB_OFFLINE=1

EXPOSE 8000 8501
CMD ["uvicorn", "aerodoc.api:app", "--host", "0.0.0.0", "--port", "8000"]
