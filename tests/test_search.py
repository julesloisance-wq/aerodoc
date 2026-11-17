from aerodoc.search import rrf, tokenize


def test_tokenize_keeps_identifiers_whole_and_split():
    tokens = tokenize("What does AD 2026-18-03 require on the A321-271NX?")
    assert "2026-18-03" in tokens and "2026" in tokens and "03" in tokens
    assert "a321-271nx" in tokens and "a321" in tokens
    assert "what" not in tokens and "the" not in tokens  # stopwords removed


def test_rrf_rewards_agreement_between_rankings():
    fused = rrf({"dense": [1, 2, 3], "bm25": [3, 4, 1]}, k=60)
    ids = [cid for cid, _ in fused]
    # Chunks 1 and 3 appear in both lists, so they beat chunks found by only one retriever.
    assert set(ids[:2]) == {1, 3}
    assert fused[0][1] == 1 / 61 + 1 / 63


def test_looks_french():
    from aerodoc.answer import looks_french

    assert looks_french("Quels avions sont concernés par l'AD 2026-18-03 ?")
    assert not looks_french("Which airplanes are affected by AD 2026-18-03?")
