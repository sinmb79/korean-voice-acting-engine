from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


PLATFORM_DELIVERY_PROFILES: list[dict[str, Any]] = [
    {
        "id": "youtube_shorts_hook",
        "platform": "youtube_shorts",
        "situation": "hook_and_explainer",
        "role": "news_anchor",
        "quality_use_case": "shorts",
        "polish_preset": "shorts",
        "text": "처음 세 초가 지나면 시청자는 이미 판단합니다. 그래서 핵심은 짧게 말하되, 한국어가 또렷하게 꽂히는 목소리입니다.",
        "target_delivery": {
            "pace": "brisk",
            "energy": "forward",
            "pauses": "short",
            "emotion": "controlled_urgency",
            "ending": "clear_call_to_continue",
        },
        "checks": ["fast_hook", "high_clarity", "short_pause", "no_shouting", "one_take_flow"],
    },
    {
        "id": "instagram_reels_soft_info",
        "platform": "instagram_reels",
        "situation": "soft_lifestyle_information",
        "role": "bright_teacher",
        "quality_use_case": "shorts",
        "polish_preset": "shorts",
        "text": "오늘은 복잡한 설명 대신, 바로 따라 할 수 있는 한 가지 방법만 알려드리겠습니다. 듣기 편해야 끝까지 볼 수 있습니다.",
        "target_delivery": {
            "pace": "moderately_bright",
            "energy": "friendly",
            "pauses": "light",
            "emotion": "warm_helpful",
            "ending": "friendly_falling",
        },
        "checks": ["friendly_energy", "clear_korean_particles", "mobile_speaker_clarity", "not_mechanical"],
    },
    {
        "id": "tiktok_reaction_punch",
        "platform": "tiktok",
        "situation": "reaction_commentary",
        "role": "news_anchor",
        "quality_use_case": "shorts",
        "polish_preset": "shorts",
        "text": "이 장면이 왜 계속 공유되는지 보겠습니다. 웃긴 장면처럼 보이지만, 사실은 누구나 한 번쯤 겪어 본 순간이기 때문입니다.",
        "target_delivery": {
            "pace": "brisk",
            "energy": "punchy",
            "pauses": "tight",
            "emotion": "curious_reaction",
            "ending": "question_ready",
        },
        "checks": ["reaction_rhythm", "contrast_emphasis", "shorts_loudness", "comment_prompt_ready"],
    },
    {
        "id": "short_drama_dialogue",
        "platform": "short_drama",
        "situation": "emotional_dialogue",
        "role": "calm_narrator",
        "quality_use_case": "drama",
        "polish_preset": "drama",
        "text": "괜찮다고 말하려 했지만, 그는 잠시 멈췄습니다. 너무 빨리 대답하면 진심이 아닌 것처럼 들릴 것 같았습니다.",
        "target_delivery": {
            "pace": "slow",
            "energy": "restrained",
            "pauses": "held",
            "emotion": "quiet_hesitation",
            "ending": "soft_falling",
        },
        "checks": ["breath_preservation", "emotional_pause", "soft_delivery", "no_overcompression"],
    },
    {
        "id": "short_drama_female_lead_confession",
        "platform": "short_drama",
        "situation": "controlled_confession",
        "role": "drama_wife_lead",
        "quality_use_case": "drama",
        "polish_preset": "drama",
        "text": "괜찮다고 말하면 정말 괜찮아질 줄 알았어요. 그런데 오늘은 그 말이 더 이상 저를 지켜주지 못합니다.",
        "target_delivery": {
            "pace": "slow",
            "energy": "contained",
            "pauses": "held",
            "emotion": "hurt_but_controlled",
            "ending": "soft_falling",
        },
        "checks": ["adult_dialogue", "controlled_hurt", "breath_gap", "no_cartoon_pitch"],
    },
    {
        "id": "short_drama_inner_monologue",
        "platform": "short_drama",
        "situation": "inner_monologue",
        "role": "drama_wife_inner",
        "quality_use_case": "drama",
        "polish_preset": "drama",
        "text": "문이 닫히고 나서야 숨을 쉬었습니다. 괜찮은 척하던 얼굴이 가장 먼저 무너졌습니다.",
        "target_delivery": {
            "pace": "very_slow",
            "energy": "intimate",
            "pauses": "wide",
            "emotion": "tired_private_truth",
            "ending": "low_breathed_falling",
        },
        "checks": ["close_mic_feel", "inner_voice", "soft_dynamic_range", "not_overbright"],
    },
    {
        "id": "short_drama_male_lead_tension",
        "platform": "short_drama",
        "situation": "restrained_argument",
        "role": "drama_husband_tense",
        "quality_use_case": "drama",
        "polish_preset": "drama",
        "text": "나는 당신을 밀어낸 게 아닙니다. 다만 내가 무너지는 걸 당신에게 보이고 싶지 않았습니다.",
        "target_delivery": {
            "pace": "slow_firm",
            "energy": "low_tension",
            "pauses": "measured",
            "emotion": "restrained_accusation",
            "ending": "firm_low_falling",
        },
        "checks": ["low_register", "restrained_tension", "consonant_clarity", "no_shouting"],
    },
    {
        "id": "short_drama_warm_second_lead",
        "platform": "short_drama",
        "situation": "warm_reassurance",
        "role": "drama_warm_artist",
        "quality_use_case": "drama",
        "polish_preset": "drama",
        "text": "지금 대답하지 않아도 됩니다. 당신이 편해지는 속도에 맞춰서, 나는 여기 있겠습니다.",
        "target_delivery": {
            "pace": "gentle",
            "energy": "warm",
            "pauses": "natural",
            "emotion": "softly_interested",
            "ending": "warm_falling",
        },
        "checks": ["warmth", "romance_dialogue", "listener_comfort", "natural_pause"],
    },
    {
        "id": "short_drama_anxious_confession",
        "platform": "short_drama",
        "situation": "anxious_confession",
        "role": "drama_other_woman",
        "quality_use_case": "drama",
        "polish_preset": "drama",
        "text": "처음부터 이렇게 될 줄 알았다면 시작하지 않았을 겁니다. 그래도 지금은 솔직히 말해야 합니다.",
        "target_delivery": {
            "pace": "unsteady",
            "energy": "fragile",
            "pauses": "uncertain",
            "emotion": "anxious_confession",
            "ending": "uncertain_falling",
        },
        "checks": ["anxious_breath", "fragile_delivery", "still_clear_korean", "no_melodrama"],
    },
    {
        "id": "youtube_documentary_narration",
        "platform": "youtube_longform",
        "situation": "documentary_narration",
        "role": "documentary",
        "quality_use_case": "documentary",
        "polish_preset": "documentary",
        "text": "좋은 다큐멘터리 내레이션은 정보를 밀어 넣지 않습니다. 대신 다음 장면을 기다리게 만드는 여백을 남깁니다.",
        "target_delivery": {
            "pace": "slow_warm",
            "energy": "calm",
            "pauses": "wide",
            "emotion": "quiet_awe",
            "ending": "deep_falling",
        },
        "checks": ["warmth", "longform_comfort", "stable_loudness", "listener_room"],
    },
    {
        "id": "podcast_explainer",
        "platform": "podcast",
        "situation": "conversational_explainer",
        "role": "calm_narrator",
        "quality_use_case": "documentary",
        "polish_preset": "documentary",
        "text": "이 이야기는 조금 천천히 들어야 합니다. 핵심은 기술 자체가 아니라, 사람이 듣고 판단할 수 있는 품질 기준입니다.",
        "target_delivery": {
            "pace": "conversational",
            "energy": "steady",
            "pauses": "natural",
            "emotion": "thoughtful",
            "ending": "low_falling",
        },
        "checks": ["natural_breath", "low_fatigue", "not_overbright", "long_listening_comfort"],
    },
    {
        "id": "education_clear_step",
        "platform": "education",
        "situation": "step_by_step_instruction",
        "role": "bright_teacher",
        "quality_use_case": "announcer",
        "polish_preset": "announcer",
        "text": "첫 번째는 문장을 짧게 나누는 것입니다. 두 번째는 숫자와 영어 표현을 미리 한국어 발음으로 정리하는 것입니다.",
        "target_delivery": {
            "pace": "clear_moderate",
            "energy": "encouraging",
            "pauses": "structured",
            "emotion": "warm_teacher",
            "ending": "friendly_falling",
        },
        "checks": ["step_clarity", "number_reading", "english_term_reading", "learner_comfort"],
    },
    {
        "id": "public_announcement_notice",
        "platform": "public_announcement",
        "situation": "formal_notice",
        "role": "news_anchor",
        "quality_use_case": "announcer",
        "polish_preset": "announcer",
        "text": "안내 말씀드립니다. 오늘 오후 여섯 시부터 점검이 진행되며, 서비스는 약 삼십 분 동안 일시적으로 중단됩니다.",
        "target_delivery": {
            "pace": "formal_moderate",
            "energy": "controlled",
            "pauses": "clear",
            "emotion": "neutral_formal",
            "ending": "firm_falling",
        },
        "checks": ["formal_tone", "time_reading", "announcement_clarity", "trustworthy_delivery"],
    },
]


def build_platform_delivery_suite_report() -> dict[str, Any]:
    return {
        "schema_version": "kva.platform_delivery_suite.v1",
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "purpose": (
            "A platform and situation delivery suite for checking whether the same Korean voice can be shaped "
            "for shorts, drama, long-form narration, education, podcast, and public announcements without "
            "claiming a different speaker identity."
        ),
        "required_review_loop": [
            "render each profile with its role",
            "run kva review-audio with the profile text",
            "run kva product-quality with quality_use_case",
            "compare delivery against target_delivery by human listening",
            "keep AI voice and private voice consent metadata in every manifest",
        ],
        "human_listening_questions": [
            "Does the delivery fit the named platform and situation?",
            "Is the Korean still natural after the role or polish preset is applied?",
            "Are pauses and energy appropriate for the expected viewing context?",
            "Does it preserve the source speaker rather than pretending to be a new actor?",
        ],
        "profiles": PLATFORM_DELIVERY_PROFILES,
    }


def write_platform_delivery_suite(output_dir: str | Path) -> dict[str, Any]:
    report = build_platform_delivery_suite_report()
    root = Path(output_dir)
    prompts_dir = root / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    for profile in report["profiles"]:
        (prompts_dir / f"{profile['id']}.txt").write_text(profile["text"] + "\n", encoding="utf-8")

    json_path = root / "platform_delivery_suite.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    markdown_path = root / "platform_delivery_suite.md"
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")

    return {
        "ok": True,
        "output_dir": str(root),
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "profile_count": len(report["profiles"]),
        "prompt_dir": str(prompts_dir),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Platform Delivery Suite",
        "",
        report["purpose"],
        "",
        "## Required Review Loop",
        "",
    ]
    for item in report["required_review_loop"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Human Listening Questions", ""])
    for item in report["human_listening_questions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Profiles", ""])
    for profile in report["profiles"]:
        checks = ", ".join(profile["checks"])
        target = ", ".join(f"{key}={value}" for key, value in profile["target_delivery"].items())
        lines.extend(
            [
                f"### {profile['id']}",
                "",
                f"- Platform: `{profile['platform']}`",
                f"- Situation: `{profile['situation']}`",
                f"- Role: `{profile['role']}`",
                f"- Quality use case: `{profile['quality_use_case']}`",
                f"- Polish preset: `{profile['polish_preset']}`",
                f"- Target delivery: {target}",
                f"- Checks: {checks}",
                "",
                "```text",
                profile["text"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)
