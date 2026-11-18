"""Streamlit web interface. Run with: streamlit run src/aerodoc/ui.py

It only talks to the API (AERODOC_API_URL), like any other client would.
"""

from __future__ import annotations

import os
import re

import httpx
import streamlit as st

API_URL = os.environ.get("AERODOC_API_URL", "http://localhost:8000")

EXAMPLES = [
    "Which airplanes are affected by AD 2026-18-03 and what is the unsafe condition?",
    "How should a portable fire extinguisher be inspected?",
    "What problem was found on the ATR 72 nose landing gear drag brace panels?",
    "Quels avions sont concernés par l'AD 2024-08-02 ?",
    "What is the maximum takeoff weight of the Airbus A350-1000?",
]

st.set_page_config(page_title="AeroDoc", page_icon="✈️", layout="wide")


@st.cache_data(ttl=300)
def _fetch_stats() -> dict:
    # Raises on failure: Streamlit does not cache exceptions, so a failed check made while
    # the API is still indexing is retried on the next page load instead of being kept.
    response = httpx.get(f"{API_URL}/stats", timeout=10)
    response.raise_for_status()
    return response.json()


def get_stats() -> dict | None:
    try:
        return _fetch_stats()
    except httpx.HTTPError:
        return None


def ask(question: str) -> dict:
    response = httpx.post(f"{API_URL}/ask", json={"question": question}, timeout=180)
    if response.status_code != 200:
        raise RuntimeError(response.json().get("detail", response.text))
    return response.json()


def link_citations(answer: str) -> str:
    """Bold the citation markers ([2] or [1][4]) that match the numbered sources below."""
    return re.sub(r"((?:\[\d+\])+)", r"**\1**", answer)


# --------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("✈️ AeroDoc")
    st.caption(
        "Cited answers over FAA airworthiness directives and the FAA Aviation Maintenance "
        "Technician Handbook. Answers come only from these documents; when the information "
        "is not there, AeroDoc says so."
    )
    stats = get_stats()
    if stats:
        st.metric("Airworthiness directives", stats["documents"].get("directive", 0))
        st.metric("Indexed passages", stats["chunks"])
        st.caption("Aircraft: " + ", ".join(f"{k} ({v})" for k, v in stats["families"].items()))
    else:
        st.warning(f"API not reachable at {API_URL}. Is it still indexing?")
    st.divider()
    st.caption(
        "Search: semantic (bge-small) + keyword (BM25), fused with RRF, reranked by a "
        "cross-encoder; LLM: Gemini. Not a substitute for the official FAA documents."
    )

# --------------------------------------------------------------------------- main
st.header("Ask a question about aircraft maintenance documents")
if "question" not in st.session_state:
    st.session_state.question = ""

cols = st.columns(len(EXAMPLES))
for col, example in zip(cols, EXAMPLES, strict=True):
    if col.button(example[:38] + "…", help=example, use_container_width=True):
        st.session_state.question = example

question = st.text_input(
    "Question", key="question", placeholder="e.g. What does AD 2025-24-51 require?"
)

if question:
    with st.spinner("Searching the documents and writing the answer…"):
        try:
            result = ask(question)
        except (RuntimeError, httpx.HTTPError) as exc:
            st.error(f"The assistant is not available: {exc}")
            st.stop()

    if result["abstained"]:
        st.warning("**I don't know based on the available documents.** " + result["answer"])
    else:
        st.markdown(link_citations(result["answer"]))

    total = sum(result["timings_ms"].values()) / 1000
    st.caption(f"{result['model']} · {total:.1f} s · {result['tokens']} tokens")

    cited = [p for p in result["passages"] if p["cited"]]
    others = [p for p in result["passages"] if not p["cited"]]

    if cited:
        st.subheader("Sources")
        for p in cited:
            with st.expander(f"[{p['number']}] {p['citation']}"):
                st.markdown(f"[Open the original document ↗]({p['source_url']})")
                st.write(p["text"])
    with st.expander(f"Other passages retrieved ({len(others)}) and how they were found"):
        for p in result["passages"]:
            found = ", ".join(f"{k} #{v}" for k, v in p["found_by"].items()) or "AD number match"
            st.markdown(
                f"**[{p['number']}] {p['citation']}**  \n"
                f"reranker score {p['score']:.2f} · found by {found}"
                + (" · **cited**" if p["cited"] else "")
            )
            st.caption(p["text"][:500] + "…")
