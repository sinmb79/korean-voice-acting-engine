from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class NormalizationTrace:
    source: str
    output: str
    rule: str
    kind: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SpeechToken:
    text: str
    source: str | None = None
    kind: str = "text"
    emphasis: float = 0.0
    pause_after_sec: float = 0.0
    say_as: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: value for key, value in data.items() if value not in (None, 0.0)}


@dataclass(slots=True)
class SpeechPhrase:
    text: str
    pause_after_sec: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SpeechScript:
    display_text: str
    speech_text: str
    phoneme_text: str
    language: str = "ko"
    tokens: list[SpeechToken] = field(default_factory=list)
    phrases: list[SpeechPhrase] = field(default_factory=list)
    normalization_trace: list[NormalizationTrace] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "display_text": self.display_text,
            "speech_text": self.speech_text,
            "phoneme_text": self.phoneme_text,
            "language": self.language,
            "tokens": [token.to_dict() for token in self.tokens],
            "phrases": [phrase.to_dict() for phrase in self.phrases],
            "normalization_trace": [trace.to_dict() for trace in self.normalization_trace],
            "warnings": self.warnings,
        }


@dataclass(slots=True)
class VoiceActingPlan:
    role: str
    emotion: str
    identity_strength: float
    role_strength: float
    pitch_shift: float
    pitch_variance: float
    speed: float
    breathiness: float
    articulation_strength: float
    pause_scale: float
    ending_style: str
    formality: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

