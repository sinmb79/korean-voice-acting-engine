from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from kva_engine.review.audio_review import review_audio, write_review
from kva_engine.synthesis.conversion import build_voice_conversion_plan, convert_voice_file


DEFAULT_VOICE_LAB_ROLES = (
    "calm_narrator",
    "wolf_growl_clear",
    "monster_deep_clear",
    "dinosaur_giant_clear",
    "child_bright",
)

VOICE_LAB_ROLE_GROUPS = {
    "default": DEFAULT_VOICE_LAB_ROLES,
    "dialogue": (
        "calm_narrator",
        "twentyfirst_prince_lead",
        "twentyfirst_grand_lady_lead",
        "bright_teacher",
        "old_storyteller",
        "villain_low",
        "child_bright",
    ),
    "drama": (
        "twentyfirst_prince_lead",
        "twentyfirst_grand_lady_lead",
        "calm_narrator",
        "villain_low",
        "old_storyteller",
    ),
    "creature": (
        "wolf_growl_clear",
        "wolf_growl_heavy",
        "monster_deep_clear",
        "monster_deep_fx",
        "dinosaur_giant_clear",
        "dinosaur_giant_roar",
    ),
    "narration": (
        "calm_narrator",
        "documentary",
        "news_anchor",
        "old_storyteller",
    ),
    "shorts": (
        "calm_narrator",
        "documentary",
        "wolf_growl_clear",
        "monster_deep_clear",
        "child_bright",
    ),
}


def parse_role_list(value: str | None) -> list[str]:
    if not value:
        return list(DEFAULT_VOICE_LAB_ROLES)
    return [role.strip() for role in value.split(",") if role.strip()]


def roles_for_group(group: str | None) -> list[str]:
    group_name = group or "default"
    if group_name not in VOICE_LAB_ROLE_GROUPS:
        raise KeyError(f"Unknown voice-lab role group: {group_name}")
    return list(VOICE_LAB_ROLE_GROUPS[group_name])


def resolve_voice_lab_roles(*, roles: str | None = None, group: str | None = None) -> list[str]:
    if roles:
        return parse_role_list(roles)
    return roles_for_group(group)


def run_voice_lab_conversion(
    *,
    input_path: str | Path,
    output_dir: str | Path,
    roles: list[str] | tuple[str, ...] | None = None,
    voice_profile_path: str | Path | None = None,
    expected_text: str | None = None,
    expected_text_path: str | Path | None = None,
    asr_model: str | None = None,
    normalize: bool = True,
    review: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    selected_roles = list(roles or DEFAULT_VOICE_LAB_ROLES)
    source = Path(input_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    samples = []
    for role in selected_roles:
        wav_path = destination / f"{role}.wav"
        result_path = destination / f"{role}.result.json"
        manifest_path = destination / f"{role}.manifest.json"
        review_path = destination / f"{role}.review.json"

        plan = build_voice_conversion_plan(
            input_path=source,
            output_path=wav_path,
            role=role,
            voice_profile_path=voice_profile_path,
            normalize=normalize,
            manifest_path=manifest_path,
        )
        if dry_run:
            result: dict[str, Any] = {
                "ok": True,
                "dry_run": True,
                "conversion_plan": plan.to_dict(),
            }
        else:
            result = convert_voice_file(plan)
        _write_json(result_path, result)

        review_payload = None
        if review and not dry_run:
            review_payload = review_audio(
                audio_path=wav_path,
                expected_text=expected_text,
                expected_text_path=expected_text_path,
                asr_model=asr_model,
                role=role,
                voice_profile_path=voice_profile_path,
            )
            write_review(review_payload, review_path)

        samples.append(
            _sample_summary(
                role=role,
                wav_path=wav_path,
                result_path=result_path,
                manifest_path=manifest_path,
                review_path=review_path if review and not dry_run else None,
                result=result,
                review=review_payload,
            )
        )

    playlist_path = destination / "playlist.m3u"
    readme_path = destination / "README.md"
    summary_path = destination / "voice_lab_summary.json"
    _write_playlist(playlist_path, [sample["wav_path"] for sample in samples])

    summary = {
        "job_id": _job_id(),
        "task": "voice_lab_conversion",
        "dry_run": dry_run,
        "input_path": str(source),
        "output_dir": str(destination),
        "roles": selected_roles,
        "review_enabled": review,
        "asr_model": asr_model,
        "expected_text_path": str(expected_text_path) if expected_text_path else None,
        "playlist_path": str(playlist_path),
        "readme_path": str(readme_path),
        "summary_path": str(summary_path),
        "samples": samples,
        "ok": all(sample["ok"] for sample in samples),
        "remaining_development": [
            "Add neural speech-to-speech backend behind the same voice-lab contract.",
            "Add a local GUI for non-developer users.",
            "Add public voice installation/render adapters after license-safe install prompts.",
            "Expand Korean acting datasets and role-specific evaluation thresholds.",
        ],
    }
    _write_json(summary_path, summary)
    _write_readme(readme_path, summary)
    return summary


def _sample_summary(
    *,
    role: str,
    wav_path: Path,
    result_path: Path,
    manifest_path: Path,
    review_path: Path | None,
    result: dict[str, Any],
    review: dict[str, Any] | None,
) -> dict[str, Any]:
    metrics = review.get("metrics") if review else None
    return {
        "role": role,
        "ok": bool(result.get("ok")) and (review.get("ok", True) if review else True),
        "wav_path": str(wav_path),
        "result_path": str(result_path),
        "manifest_path": str(manifest_path),
        "review_path": str(review_path) if review_path else None,
        "audio": result.get("audio"),
        "quality": review.get("quality") if review else None,
        "cer_percent": metrics.get("cer", {}).get("percent") if metrics else None,
        "wer_percent": metrics.get("wer", {}).get("percent") if metrics else None,
        "warnings": sorted(set(result.get("warnings", []) + (review.get("warnings", []) if review else []))),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_playlist(path: Path, wav_paths: list[str]) -> None:
    path.write_text("#EXTM3U\n" + "\n".join(wav_paths) + "\n", encoding="utf-8")


def _write_readme(path: Path, summary: dict[str, Any]) -> None:
    rows = []
    for sample in summary["samples"]:
        rows.append(
            "| {role} | {ok} | `{wav}` | {cer} | {wer} | {warnings} |".format(
                role=sample["role"],
                ok="ok" if sample["ok"] else "review",
                wav=Path(sample["wav_path"]).name,
                cer=_percent(sample["cer_percent"]),
                wer=_percent(sample["wer_percent"]),
                warnings=", ".join(sample["warnings"]) or "-",
            )
        )

    content = "\n".join(
        [
            "# KVAE Voice Lab Output",
            "",
            "This folder was generated by `kva voice-lab`.",
            "",
            "## Input",
            "",
            "```text",
            summary["input_path"],
            "```",
            "",
            "## Samples",
            "",
            "| role | status | file | CER | WER | warnings |",
            "| --- | --- | --- | ---: | ---: | --- |",
            *rows,
            "",
            "## Files",
            "",
            f"- Playlist: `{Path(summary['playlist_path']).name}`",
            f"- Summary: `{Path(summary['summary_path']).name}`" if "summary_path" in summary else "- Summary: `voice_lab_summary.json`",
            "",
            "## Disclosure",
            "",
            "Generated voices should be treated as AI-generated or AI-assisted speech. Keep private speaker data outside the public repository.",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def _percent(value: float | int | None) -> str:
    return "-" if value is None else f"{float(value):.3f}%"


def _job_id() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
