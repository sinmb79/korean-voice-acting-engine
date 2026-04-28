from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path
from typing import Any


PROMPT_BANK: list[dict[str, Any]] = [
    {
        "category": "calibration",
        "text": "오늘은 깨끗한 한국어 목소리를 만들기 위해 천천히 또박또박 녹음합니다.",
        "tags": ["baseline", "clear"],
    },
    {
        "category": "numbers",
        "text": "2026년 4월 28일 오전 9시 30분, 참가자는 총 1,257명이었습니다.",
        "tags": ["date", "time", "number"],
    },
    {
        "category": "numbers",
        "text": "가격은 3만 9천 원이고, 할인율은 12.5퍼센트입니다.",
        "tags": ["price", "percentage"],
    },
    {
        "category": "english",
        "text": "AI, TTS, GPU, API 같은 영어 약어도 한국어 문장 안에서 자연스럽게 읽어야 합니다.",
        "tags": ["english", "abbreviation"],
    },
    {
        "category": "josa",
        "text": "사과는 맛있고, 배는 시원하며, 복숭아와 포도도 오늘 녹음에 포함됩니다.",
        "tags": ["particle", "josa"],
    },
    {
        "category": "ending",
        "text": "그렇게 생각했지만, 막상 들어보니 전혀 다른 감정이 숨어 있었습니다.",
        "tags": ["ending", "emotion"],
    },
    {
        "category": "narration",
        "text": "한밤중의 도시는 조용했지만, 골목 끝에서는 아주 작은 발소리가 들렸습니다.",
        "tags": ["narration", "pause"],
    },
    {
        "category": "teacher",
        "text": "여기서 중요한 점은 빠르게 말하는 것이 아니라, 듣는 사람이 이해하도록 말하는 것입니다.",
        "tags": ["teacher", "clarity"],
    },
    {
        "category": "news",
        "text": "정부는 오늘 오전 새 정책을 발표했고, 현장 반응은 지역별로 엇갈렸습니다.",
        "tags": ["news", "formal"],
    },
    {
        "category": "dialogue",
        "text": "정말 괜찮은 거야? 아니, 괜찮은 척하는 것뿐이야.",
        "tags": ["dialogue", "emotion"],
    },
    {
        "category": "child",
        "text": "나도 할 수 있어요. 조금 무섭지만, 그래도 한 번 해볼래요.",
        "tags": ["child", "bright"],
    },
    {
        "category": "elder",
        "text": "옛날에는 말이다, 비 오는 날이면 모두가 처마 밑에 모여 이야기를 나누곤 했지.",
        "tags": ["elder", "story"],
    },
    {
        "category": "villain",
        "text": "너는 아직 모른다. 이 조용한 방 안에서 이미 모든 것이 결정되었다는 사실을.",
        "tags": ["villain", "low"],
    },
    {
        "category": "creature",
        "text": "숲의 깊은 곳에서 낮은 울음이 번졌고, 숨소리는 점점 가까워졌습니다.",
        "tags": ["wolf", "monster", "dinosaur"],
    },
    {
        "category": "whisper",
        "text": "지금은 아주 작게 말해야 합니다. 그래야 저 문 너머의 소리를 들을 수 있습니다.",
        "tags": ["quiet", "breath"],
    },
    {
        "category": "emphasis",
        "text": "중요한 것은 단 하나입니다. 목소리는 기술이기 전에 사람의 흔적입니다.",
        "tags": ["philosophy", "emphasis"],
    },
]


STYLE_PASSES: list[dict[str, Any]] = [
    {
        "id": "neutral_clear",
        "direction": "평소 말투로, 발음을 또렷하게 유지합니다.",
        "speed_factor": 1.0,
    },
    {
        "id": "slow_story",
        "direction": "조금 느리게, 문장 사이의 쉼을 자연스럽게 둡니다.",
        "speed_factor": 1.18,
    },
    {
        "id": "bright_energy",
        "direction": "밝고 힘 있게 말하되 과장하지 않습니다.",
        "speed_factor": 0.95,
    },
    {
        "id": "low_character",
        "direction": "낮고 안정된 톤으로, 캐릭터 연기처럼 말합니다.",
        "speed_factor": 1.08,
    },
    {
        "id": "quiet_precise",
        "direction": "작지만 명확하게, 숨소리와 끝 발음을 정리합니다.",
        "speed_factor": 1.12,
    },
]


def generate_recording_session_plan(
    *,
    output_dir: str | Path,
    speaker_id: str | None = None,
    target_minutes: float = 30.0,
    prompt_count: int | None = None,
) -> dict[str, Any]:
    if target_minutes <= 0:
        raise ValueError("target_minutes must be greater than zero.")
    if prompt_count is not None and prompt_count <= 0:
        raise ValueError("prompt_count must be greater than zero.")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    target_seconds = target_minutes * 60
    prompts: list[dict[str, Any]] = []
    total_seconds = 0.0
    index = 0
    max_iterations = max(prompt_count or 0, 2500)
    while _should_add_prompt(
        prompts=prompts,
        total_seconds=total_seconds,
        target_seconds=target_seconds,
        prompt_count=prompt_count,
    ):
        if index >= max_iterations:
            break
        seed = PROMPT_BANK[index % len(PROMPT_BANK)]
        style = STYLE_PASSES[(index // len(PROMPT_BANK)) % len(STYLE_PASSES)]
        round_index = index // (len(PROMPT_BANK) * len(STYLE_PASSES)) + 1
        duration_sec = _estimate_prompt_duration(seed["text"], speed_factor=float(style["speed_factor"]))
        prompt = {
            "id": f"rec-{len(prompts) + 1:04d}",
            "round": round_index,
            "category": seed["category"],
            "style": style["id"],
            "text": seed["text"],
            "acting_direction": style["direction"],
            "tags": list(seed["tags"]) + [style["id"]],
            "estimated_duration_sec": duration_sec,
        }
        prompts.append(prompt)
        total_seconds += duration_sec
        index += 1

    created_at = dt.datetime.now(dt.UTC).isoformat()
    plan = {
        "schema_version": "kva.recording_session_plan.v1",
        "created_at": created_at,
        "speaker_id": speaker_id,
        "target_minutes": target_minutes,
        "estimated_total_duration_sec": round(total_seconds, 3),
        "prompt_count": len(prompts),
        "prompt_bank_size": len(PROMPT_BANK),
        "style_passes": STYLE_PASSES,
        "prompts": prompts,
        "safety": {
            "privacy": "private-voice-data-stays-local",
            "public_repo_rule": "Commit scripts and schemas only; do not commit private recordings.",
        },
        "next_steps": [
            "Record in WAV format with low noise and no background music.",
            "Run kva recording-check on each long session.",
            "Run kva split-recording with the reviewed transcript.",
            "Correct transcripts before train/validation/test split.",
        ],
    }

    json_path = destination / "recording_session_plan.json"
    script_path = destination / "recording_script.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    script_path.write_text(_recording_script_markdown(plan), encoding="utf-8")
    plan["plan_path"] = str(json_path)
    plan["script_path"] = str(script_path)
    return plan


def build_dataset_split(
    *,
    manifest_path: str | Path,
    output_path: str | Path,
    train_ratio: float = 0.8,
    validation_ratio: float = 0.1,
    require_transcript: bool = False,
) -> dict[str, Any]:
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1.")
    if not 0 <= validation_ratio < 1:
        raise ValueError("validation_ratio must be between 0 and 1.")
    if train_ratio + validation_ratio >= 1:
        raise ValueError("train_ratio + validation_ratio must be less than 1.")

    source = Path(manifest_path)
    manifest = json.loads(source.read_text(encoding="utf-8"))
    segments = list(manifest.get("segments", []))
    eligible: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for segment in segments:
        transcript = segment.get("transcript")
        if require_transcript and not transcript:
            skipped.append({"index": segment.get("index"), "reason": "missing_transcript"})
            continue
        eligible.append(segment)

    ordered = sorted(eligible, key=_segment_sort_key)
    counts = _split_counts(
        len(ordered),
        train_ratio=train_ratio,
        validation_ratio=validation_ratio,
    )
    train_end = counts["train"]
    validation_end = train_end + counts["validation"]
    splits = {
        "train": ordered[:train_end],
        "validation": ordered[train_end:validation_end],
        "test": ordered[validation_end:],
    }
    warnings: list[str] = []
    if len(ordered) < 10:
        warnings.append("small_dataset_split_review_manually")
    if skipped:
        warnings.append("segments_skipped")

    result = {
        "schema_version": "kva.dataset_split.v1",
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "source_manifest": str(source),
        "config": {
            "train_ratio": train_ratio,
            "validation_ratio": validation_ratio,
            "test_ratio": round(1.0 - train_ratio - validation_ratio, 6),
            "require_transcript": require_transcript,
        },
        "summary": {
            "source_segment_count": len(segments),
            "eligible_segment_count": len(ordered),
            "skipped_segment_count": len(skipped),
            "train_count": len(splits["train"]),
            "validation_count": len(splits["validation"]),
            "test_count": len(splits["test"]),
        },
        "splits": splits,
        "skipped": skipped,
        "warnings": warnings,
        "next_steps": [
            "Listen to validation and test samples before training.",
            "Keep speaker identity and private recordings outside the public repository.",
            "Use the same split manifest for repeatable model comparisons.",
        ],
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["split_path"] = str(destination)
    return result


def _should_add_prompt(
    *,
    prompts: list[dict[str, Any]],
    total_seconds: float,
    target_seconds: float,
    prompt_count: int | None,
) -> bool:
    if prompt_count is not None:
        return len(prompts) < prompt_count
    return total_seconds < target_seconds


def _estimate_prompt_duration(text: str, *, speed_factor: float) -> float:
    base_seconds = 2.0 + len(text) * 0.18
    return round(max(3.0, base_seconds * speed_factor), 3)


def _recording_script_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# KVAE Recording Script",
        "",
        f"- Speaker ID: {plan.get('speaker_id') or 'unset'}",
        f"- Prompt count: {plan['prompt_count']}",
        f"- Estimated duration: {round(plan['estimated_total_duration_sec'] / 60, 2)} minutes",
        "",
        "## Recording Checklist",
        "",
        "- Use a quiet room and one microphone position.",
        "- Leave one or two seconds of silence before the first line.",
        "- Read the line, then leave a short pause before the next prompt.",
        "- Re-record lines with clipping, coughs, or misreads.",
        "",
        "## Prompts",
        "",
    ]
    for prompt in plan["prompts"]:
        lines.extend(
            [
                f"### {prompt['id']} · {prompt['category']} · {prompt['style']}",
                "",
                f"- Direction: {prompt['acting_direction']}",
                f"- Tags: {', '.join(prompt['tags'])}",
                "",
                prompt["text"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _segment_sort_key(segment: dict[str, Any]) -> str:
    audio = segment.get("audio") or {}
    return str(audio.get("sha256") or segment.get("path") or segment.get("file_name") or segment.get("index"))


def _split_counts(count: int, *, train_ratio: float, validation_ratio: float) -> dict[str, int]:
    if count <= 0:
        return {"train": 0, "validation": 0, "test": 0}
    if count == 1:
        return {"train": 1, "validation": 0, "test": 0}
    if count == 2:
        return {"train": 1, "validation": 1, "test": 0}

    train_count = math.floor(count * train_ratio)
    validation_count = math.floor(count * validation_ratio)
    test_count = count - train_count - validation_count
    if validation_count == 0:
        validation_count = 1
        train_count -= 1
    if test_count == 0:
        test_count = 1
        train_count -= 1
    if train_count <= 0:
        train_count = 1
    while train_count + validation_count + test_count > count:
        if train_count > 1:
            train_count -= 1
        elif validation_count > 1:
            validation_count -= 1
        elif test_count > 1:
            test_count -= 1
        else:
            break
    return {
        "train": train_count,
        "validation": validation_count,
        "test": count - train_count - validation_count,
    }
