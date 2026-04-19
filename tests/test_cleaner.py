from markdowner.cleaner import _chunks


def test_chunks_short_text_unchanged() -> None:
    text = "Short sentence. Another one."
    assert _chunks(text) == [text]


def test_chunks_splits_long_text() -> None:
    sentence = "This is a sentence. "
    text = sentence * 2000  # ~40k chars
    result = _chunks(text, size=15000)

    assert len(result) > 1
    assert all(len(c) <= 15500 for c in result)  # tolerate sentence-boundary overshoot
    assert "".join(result).count("This is a sentence") == 2000


def test_chunks_preserves_sentence_boundaries() -> None:
    sentences = [f"Sentence number {i}" for i in range(100)]
    text = ". ".join(sentences) + "."
    result = _chunks(text, size=500)

    joined = " ".join(result)
    for s in sentences:
        assert s in joined
