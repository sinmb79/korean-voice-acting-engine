from __future__ import annotations

from html import escape

from kva_engine.schemas import SpeechScript


def speech_script_to_ssml(script: SpeechScript) -> str:
    parts = ["<speak>"]
    for phrase in script.phrases:
        parts.append(escape(phrase.text))
        if phrase.pause_after_sec > 0:
            parts.append(f'<break time="{int(phrase.pause_after_sec * 1000)}ms"/>')
    if not script.phrases:
        parts.append(escape(script.speech_text))
    parts.append("</speak>")
    return "".join(parts)
