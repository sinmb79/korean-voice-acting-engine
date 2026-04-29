from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


KOREAN_EVALUATION_PROMPTS: list[dict[str, Any]] = [
    {
        "id": "ko_numbers_dates_units",
        "category": "normalization",
        "use_case": "announcer",
        "text": "2026년 4월 29일 오후 6시 30분, 서울의 기온은 18.5도였고, 강수 확률은 30퍼센트였습니다.",
        "checks": ["dates", "times", "decimal_numbers", "units", "clear_reading"],
    },
    {
        "id": "ko_english_brand_mix",
        "category": "code_switching",
        "use_case": "shorts",
        "text": "오늘 업데이트는 KVAE, VoxCPM2, ONNX CPU 모드를 비교해서 한국어 목소리가 얼마나 자연스러운지 확인하는 과정입니다.",
        "checks": ["english_acronyms", "model_names", "korean_particles", "natural_pacing"],
    },
    {
        "id": "ko_phone_money_address",
        "category": "normalization",
        "use_case": "announcement",
        "text": "문의 전화는 02-1234-5678이고, 참가비는 3만 5천 원입니다. 장소는 서울특별시 중구 세종대로 110입니다.",
        "checks": ["phone_number", "money", "address", "announcement_clarity"],
    },
    {
        "id": "ko_short_form_one_take",
        "category": "shorts",
        "use_case": "shorts",
        "text": "처음엔 단순한 음성 변환처럼 보였습니다. 하지만 실제로 필요한 건 목소리를 바꾸는 기술보다, 한국어가 자연스럽게 들리는지 끝까지 검수하는 시스템이었습니다.",
        "checks": ["one_take_flow", "pause_naturalness", "not_mechanical", "ending_lands"],
    },
    {
        "id": "ko_drama_low_breath",
        "category": "acting",
        "use_case": "drama",
        "text": "괜찮다고 말하고 싶었지만, 목소리가 먼저 흔들렸습니다. 그래서 그는 잠시 숨을 고르고, 아주 천천히 다시 말했습니다.",
        "checks": ["breath_preservation", "emotion", "soft_delivery", "no_overcompression"],
    },
    {
        "id": "ko_documentary_long_sentence",
        "category": "long_form",
        "use_case": "documentary",
        "text": "좋은 내레이션은 정보를 많이 담는 것보다, 듣는 사람이 다음 문장을 기다릴 수 있도록 호흡을 남겨두는 데에서 시작됩니다.",
        "checks": ["long_sentence", "warmth", "listener_comfort", "stable_loudness"],
    },
    {
        "id": "ko_pronunciation_minimal_pairs",
        "category": "pronunciation",
        "use_case": "education",
        "text": "값과 갑, 밤과 밥, 낫과 낮과 낯을 구분해서 읽어야 한국어 발음 검수가 가능합니다.",
        "checks": ["final_consonants", "minimal_pairs", "education_clarity"],
    },
    {
        "id": "ko_question_emphasis",
        "category": "prosody",
        "use_case": "shorts",
        "text": "정말 이 정도면 충분할까요? 아니요. 이제는 듣는 사람이 바로 비교하고 판단할 수 있는 검수 파일까지 만들어야 합니다.",
        "checks": ["question_intonation", "contrast", "emphasis", "natural_rhythm"],
    },
    {
        "id": "ko_public_disclosure",
        "category": "safety",
        "use_case": "announcement",
        "text": "이 음성은 사용자의 동의를 받은 자료를 바탕으로 생성되었으며, 공개 배포 전에는 출처와 AI 음성 사용 사실을 함께 고지해야 합니다.",
        "checks": ["ai_disclosure", "consent_language", "formal_tone"],
    },
    {
        "id": "ko_backend_stability",
        "category": "stability",
        "use_case": "announcer",
        "text": "같은 문장을 세 번 생성했을 때 발음과 속도와 음량이 크게 흔들리지 않아야 제품 기능이라고 말할 수 있습니다.",
        "checks": ["repeatability", "speed_stability", "loudness_stability", "pronunciation_stability"],
    },
]


def build_evaluation_suite_report() -> dict[str, Any]:
    return {
        "schema_version": "kva.korean_evaluation_suite.v1",
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "purpose": (
            "A fixed Korean smoke-test suite for comparing TTS backends, polish presets, and release candidates. "
            "A backend should not be promoted until these prompts are rendered, reviewed, and listened to."
        ),
        "required_review_loop": [
            "render each prompt with the candidate backend",
            "run kva review-audio with expected text or ASR transcript",
            "fill human listening scores for Korean pronunciation, naturalness, emotion fit, and artifact level",
            "run kva product-quality before release",
        ],
        "human_score_scale": {
            "1": "unusable",
            "2": "poor",
            "3": "acceptable draft",
            "4": "production usable",
            "5": "excellent",
        },
        "prompts": KOREAN_EVALUATION_PROMPTS,
    }


def write_evaluation_suite(output_dir: str | Path) -> dict[str, Any]:
    report = build_evaluation_suite_report()
    root = Path(output_dir)
    prompts_dir = root / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    for prompt in report["prompts"]:
        (prompts_dir / f"{prompt['id']}.txt").write_text(prompt["text"] + "\n", encoding="utf-8")

    json_path = root / "korean_eval_suite.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    markdown_path = root / "korean_eval_suite.md"
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")

    return {
        "ok": True,
        "output_dir": str(root),
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "prompt_count": len(report["prompts"]),
        "prompt_dir": str(prompts_dir),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Korean Evaluation Suite",
        "",
        report["purpose"],
        "",
        "## Required Review Loop",
        "",
    ]
    for item in report["required_review_loop"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Prompts", ""])
    for prompt in report["prompts"]:
        checks = ", ".join(prompt["checks"])
        lines.extend(
            [
                f"### {prompt['id']}",
                "",
                f"- Category: `{prompt['category']}`",
                f"- Use case: `{prompt['use_case']}`",
                f"- Checks: {checks}",
                "",
                "```text",
                prompt["text"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)
