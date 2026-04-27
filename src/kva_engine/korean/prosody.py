from __future__ import annotations

import re

from kva_engine.schemas import SpeechPhrase


SENTENCE_SPLIT_RE = re.compile(r"([^.!?。！？\n]+[.!?。！？]?)")


def split_phrases(text: str, *, max_chars: int = 34) -> list[SpeechPhrase]:
    phrases: list[SpeechPhrase] = []
    for sentence_match in SENTENCE_SPLIT_RE.finditer(text):
        sentence = sentence_match.group(1).strip()
        if not sentence:
            continue
        phrases.extend(_split_long_sentence(sentence, max_chars=max_chars))
    if not phrases and text.strip():
        phrases.append(SpeechPhrase(text=text.strip(), pause_after_sec=0.25))
    return phrases


def _split_long_sentence(sentence: str, *, max_chars: int) -> list[SpeechPhrase]:
    if len(sentence) <= max_chars:
        return [SpeechPhrase(text=sentence, pause_after_sec=_pause_for_sentence(sentence))]

    chunks: list[SpeechPhrase] = []
    current: list[str] = []
    for word in sentence.split():
        current.append(word)
        candidate = " ".join(current)
        if len(candidate) >= max_chars or word.endswith((",", "，", ";", "；")):
            chunks.append(SpeechPhrase(text=candidate.rstrip(","), pause_after_sec=0.18))
            current = []
    if current:
        chunks.append(SpeechPhrase(text=" ".join(current), pause_after_sec=_pause_for_sentence(sentence)))
    return chunks


def _pause_for_sentence(sentence: str) -> float:
    if sentence.endswith(("?", "？")):
        return 0.32
    if sentence.endswith(("!", "！")):
        return 0.28
    return 0.35

