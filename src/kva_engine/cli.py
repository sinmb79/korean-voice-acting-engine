from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kva_engine.acting.planner import plan_voice_acting
from kva_engine.acting.presets import PRESETS
from kva_engine.diagnostics import run_doctor
from kva_engine.korean.g2p_adapter import G2P_MODES
from kva_engine.korean.normalizer import load_pronunciation_dict, normalize_file, normalize_text
from kva_engine.public_voices import get_public_voice, list_public_voices, load_public_voice_catalog, public_voice_profile
from kva_engine.review.audio_review import recording_check, review_audio
from kva_engine.review.manifest import build_generation_manifest
from kva_engine.ssml import speech_script_to_ssml
from kva_engine.synthesis.conversion import build_voice_conversion_plan, convert_voice_file
from kva_engine.synthesis.voxcpm import VoxCpmRenderError, build_voxcpm_synthesis_plan, render_voxcpm_speech
from kva_engine.training.family_registry import build_family_registry_training_manifest
from kva_engine.training.native_voice_model import train_native_voice_model
from kva_engine.voice_profile import load_voice_profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kva", description="Korean Voice Acting Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser("normalize", help="Create Korean speech_script JSON")
    normalize_parser.add_argument("text", nargs="?", help="Display text to normalize")
    normalize_parser.add_argument("--file", help="UTF-8 text file to normalize")
    normalize_parser.add_argument("--dict", dest="dict_path", help="Pronunciation dictionary JSON")
    normalize_parser.add_argument("--g2p", default="rules", choices=sorted(G2P_MODES), help="Pronunciation planner mode")
    normalize_parser.add_argument("--out", help="Output JSON path")
    normalize_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    doctor_parser = subparsers.add_parser("doctor", help="Check the local KVAE runtime and safety configuration")
    doctor_parser.add_argument("--voice-profile", help="Optional voice profile JSON, audio file, voice folder, or public:<id>")
    doctor_parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when warnings are present")
    doctor_parser.add_argument("--out", help="Output JSON path")
    doctor_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    cast_parser = subparsers.add_parser("cast", help="Apply a voice acting role to normalized text")
    cast_parser.add_argument("text", nargs="?", help="Display text to normalize and cast")
    cast_parser.add_argument("--file", help="UTF-8 text file to normalize and cast")
    cast_parser.add_argument("--dict", dest="dict_path", help="Pronunciation dictionary JSON")
    cast_parser.add_argument("--g2p", default="rules", choices=sorted(G2P_MODES), help="Pronunciation planner mode")
    cast_parser.add_argument("--role", default="calm_narrator", choices=sorted(PRESETS))
    cast_parser.add_argument(
        "--voice-profile",
        help="Voice profile JSON, audio file, or voice folder. Defaults to configs/default_voice.local.json when present.",
    )
    cast_parser.add_argument("--out", help="Output JSON path")
    cast_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    voice_profile_parser = subparsers.add_parser("voice-profile", help="Show the resolved default voice profile")
    voice_profile_parser.add_argument("path", nargs="?", help="Optional profile JSON, audio file, or voice folder")
    voice_profile_parser.add_argument("--out", help="Output JSON path")
    voice_profile_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    public_voices_parser = subparsers.add_parser("public-voices", help="List built-in public Korean AI voice options")
    public_voices_parser.add_argument("--id", dest="voice_id", help="Show one public voice by id")
    public_voices_parser.add_argument(
        "--profile",
        action="store_true",
        help="Return a KVAE voice profile for --id, usable as public:<id>",
    )
    public_voices_parser.add_argument(
        "--include-experimental",
        action="store_true",
        help="Include entries that require manual license/provenance review",
    )
    public_voices_parser.add_argument(
        "--commercial-only",
        action="store_true",
        help="Only show entries explicitly marked as commercially usable",
    )
    public_voices_parser.add_argument("--out", help="Output JSON path")
    public_voices_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    ssml_parser = subparsers.add_parser("ssml", help="Create SSML from Korean-normalized text")
    ssml_parser.add_argument("text", nargs="?", help="Display text to normalize")
    ssml_parser.add_argument("--file", help="UTF-8 text file to normalize")
    ssml_parser.add_argument("--dict", dest="dict_path", help="Pronunciation dictionary JSON")
    ssml_parser.add_argument("--g2p", default="rules", choices=sorted(G2P_MODES), help="Pronunciation planner mode")
    ssml_parser.add_argument("--out", help="Output JSON path")
    ssml_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    review_parser = subparsers.add_parser("manifest", help="Create generation/review manifest")
    review_parser.add_argument("--script", dest="script_path", help="Speech script JSON path")
    review_parser.add_argument("--audio", dest="audio_path", help="Generated WAV path to analyze")
    review_parser.add_argument("--voice-profile", help="Voice profile JSON, audio file, or voice folder")
    review_parser.add_argument("--role", help="Voice acting role")
    review_parser.add_argument("--out", help="Output JSON path")
    review_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    audio_review_parser = subparsers.add_parser("review-audio", help="Review generated/converted audio quality")
    audio_review_parser.add_argument("--audio", required=True, help="WAV path to review")
    audio_review_parser.add_argument("--expected-text", help="Expected transcript text")
    audio_review_parser.add_argument("--expected-file", dest="expected_text_path", help="UTF-8 expected transcript file")
    audio_review_parser.add_argument("--asr-model", help="Optional Whisper model name, e.g. tiny, base, small")
    audio_review_parser.add_argument("--asr-text", help="Already transcribed text; skips Whisper")
    audio_review_parser.add_argument("--voice-profile", help="Voice profile JSON, audio file, or voice folder")
    audio_review_parser.add_argument("--role", help="Voice acting role")
    audio_review_parser.add_argument("--out", help="Output JSON path")
    audio_review_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    recording_check_parser = subparsers.add_parser("recording-check", help="Check raw recording quality for KVAE training")
    recording_check_parser.add_argument("--audio", required=True, help="Recording WAV path to check")
    recording_check_parser.add_argument("--out", help="Output JSON path")
    recording_check_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    render_parser = subparsers.add_parser("render", help="Render Korean speech to WAV through the KVAE engine")
    render_parser.add_argument("text", nargs="?", help="Display text to normalize and render")
    render_parser.add_argument("--file", help="UTF-8 text file to normalize and render")
    render_parser.add_argument("--dict", dest="dict_path", help="Pronunciation dictionary JSON")
    render_parser.add_argument("--g2p", default="rules", choices=sorted(G2P_MODES), help="Pronunciation planner mode")
    render_parser.add_argument("--role", default="calm_narrator", choices=sorted(PRESETS))
    render_parser.add_argument("--engine", default="voxcpm", choices=("voxcpm",))
    render_parser.add_argument("--voice-profile", help="Voice profile JSON, audio file, or voice folder")
    render_parser.add_argument("--out", required=True, help="Output WAV path")
    render_parser.add_argument("--json-out", help="Output render result JSON path")
    render_parser.add_argument("--manifest-out", help="Output generation/review manifest JSON path")
    render_parser.add_argument("--python", dest="python_executable", help="Python executable with VoxCPM installed")
    render_parser.add_argument("--model-path", help="Local VoxCPM model path or Hugging Face model id")
    render_parser.add_argument("--reference-audio", help="Reference WAV/M4A path")
    render_parser.add_argument("--prompt-audio", help="Prompt WAV path; defaults to reference audio")
    render_parser.add_argument("--prompt-text-file", help="Prompt transcript text file")
    render_parser.add_argument("--lora-path", help="Trained VoxCPM LoRA checkpoint directory")
    render_parser.add_argument("--cfg-value", type=float, help="VoxCPM CFG value")
    render_parser.add_argument("--inference-timesteps", type=int, default=20)
    render_parser.add_argument(
        "--no-role-audio-transform",
        action="store_true",
        help="Do not apply role pitch/speed controls after neural generation",
    )
    render_parser.add_argument("--no-normalize", action="store_true", help="Skip ffmpeg loudness normalization")
    render_parser.add_argument("--dry-run", action="store_true", help="Print the resolved render plan without generating audio")
    render_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert a recorded voice performance into a KVAE role/character voice",
    )
    convert_parser.add_argument("--input", required=True, help="Input WAV/M4A/MP3/FLAC performance audio")
    convert_parser.add_argument("--role", required=True, choices=sorted(PRESETS))
    convert_parser.add_argument("--out", required=True, help="Output WAV path")
    convert_parser.add_argument("--voice-profile", help="Optional voice profile for consent/ownership metadata")
    convert_parser.add_argument("--json-out", help="Output conversion result JSON path")
    convert_parser.add_argument("--manifest-out", help="Output conversion manifest JSON path")
    convert_parser.add_argument("--no-normalize", action="store_true", help="Skip ffmpeg loudness normalization")
    convert_parser.add_argument("--dry-run", action="store_true", help="Print the resolved conversion plan without creating audio")
    convert_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    train_parser = subparsers.add_parser(
        "train-profile",
        help="Prepare a local family voice training manifest from a voice registry",
    )
    train_parser.add_argument(
        "--registry",
        required=True,
        help="Path to 22b-family-voice-registry or a compatible local registry",
    )
    train_parser.add_argument("--role", help="Optional role filter, e.g. father")
    train_parser.add_argument("--profile-id", help="Optional registry profile id filter")
    train_parser.add_argument("--out", required=True, help="Output manifest JSON path")
    train_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    native_train_parser = subparsers.add_parser(
        "train-native",
        help="Train a KVA-native statistical voice model from a local voice registry",
    )
    native_train_parser.add_argument(
        "--registry",
        required=True,
        help="Path to 22b-family-voice-registry or a compatible local registry",
    )
    native_train_parser.add_argument("--role", help="Optional role filter, e.g. father")
    native_train_parser.add_argument("--profile-id", help="Optional registry profile id filter")
    native_train_parser.add_argument("--out", required=True, help="Output KVA native model JSON path")
    native_train_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    args = parser.parse_args(argv)
    if args.command == "doctor":
        report = run_doctor(voice_profile_path=args.voice_profile)
        code = 0
        if report["status"] == "fail" or (args.strict and report["status"] != "pass"):
            code = 1
        _emit(report, out=args.out, compact=args.compact)
        return code
    if args.command == "normalize":
        script = _build_script(args)
        return _emit(script.to_dict(), out=args.out, compact=args.compact)
    if args.command == "cast":
        script = _build_script(args)
        voice_profile = load_voice_profile(args.voice_profile)
        plan = plan_voice_acting(script, role=args.role, voice_profile=voice_profile)
        return _emit(plan, out=args.out, compact=args.compact)
    if args.command == "voice-profile":
        profile = load_voice_profile(args.path)
        return _emit({"voice_profile": profile}, out=args.out, compact=args.compact)
    if args.command == "public-voices":
        if args.voice_id and args.profile:
            return _emit({"voice_profile": public_voice_profile(args.voice_id)}, out=args.out, compact=args.compact)
        if args.voice_id:
            return _emit({"voice": get_public_voice(args.voice_id)}, out=args.out, compact=args.compact)
        catalog = load_public_voice_catalog()
        voices = list_public_voices(
            include_experimental=args.include_experimental,
            commercial_only=args.commercial_only,
        )
        return _emit(
            {
                "catalog_version": catalog.get("catalog_version"),
                "title": catalog.get("title"),
                "disclosure": catalog.get("disclosure"),
                "voices": voices,
            },
            out=args.out,
            compact=args.compact,
        )
    if args.command == "ssml":
        script = _build_script(args)
        return _emit(
            {
                "speech_text": script.speech_text,
                "ssml": speech_script_to_ssml(script),
                "warnings": script.warnings,
            },
            out=args.out,
            compact=args.compact,
        )
    if args.command == "manifest":
        manifest = build_generation_manifest(
            script_path=args.script_path,
            audio_path=args.audio_path,
            voice_profile_path=args.voice_profile,
            role=args.role,
        )
        return _emit(manifest, out=args.out, compact=args.compact)
    if args.command == "review-audio":
        review = review_audio(
            audio_path=args.audio,
            expected_text=args.expected_text,
            expected_text_path=args.expected_text_path,
            asr_model=args.asr_model,
            asr_text=args.asr_text,
            role=args.role,
            voice_profile_path=args.voice_profile,
        )
        return _emit(review, out=args.out, compact=args.compact)
    if args.command == "recording-check":
        review = recording_check(audio_path=args.audio)
        return _emit(review, out=args.out, compact=args.compact)
    if args.command == "render":
        script = _build_script(args)
        plan = build_voxcpm_synthesis_plan(
            text=script.speech_text,
            output_path=args.out,
            voice_profile_path=args.voice_profile,
            role=args.role,
            python_executable=args.python_executable,
            model_path=args.model_path,
            reference_audio=args.reference_audio,
            prompt_audio=args.prompt_audio,
            prompt_text_file=args.prompt_text_file,
            lora_path=args.lora_path,
            cfg_value=args.cfg_value,
            inference_timesteps=args.inference_timesteps,
            role_audio_transform=not args.no_role_audio_transform,
            normalize=not args.no_normalize,
            manifest_path=args.manifest_out,
        )
        if args.dry_run:
            return _emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "display_text": script.display_text,
                    "speech_text": script.speech_text,
                    "phoneme_text": script.phoneme_text,
                    "render_plan": plan.to_dict(),
                    "warnings": script.warnings + plan.warnings,
                },
                out=args.json_out,
                compact=args.compact,
            )
        try:
            result = render_voxcpm_speech(plan)
        except VoxCpmRenderError as exc:
            return _emit(
                {
                    "ok": False,
                    "error": str(exc),
                    "stdout_tail": _tail(exc.stdout),
                    "stderr_tail": _tail(exc.stderr),
                    "render_plan": plan.to_dict(),
                },
                out=args.json_out,
                compact=args.compact,
            ) or 1
        result["display_text"] = script.display_text
        result["speech_text"] = script.speech_text
        result["phoneme_text"] = script.phoneme_text
        result["warnings"] = script.warnings + result.get("plan", {}).get("warnings", [])
        return _emit(result, out=args.json_out, compact=args.compact)
    if args.command == "convert":
        plan = build_voice_conversion_plan(
            input_path=args.input,
            output_path=args.out,
            role=args.role,
            voice_profile_path=args.voice_profile,
            normalize=not args.no_normalize,
            manifest_path=args.manifest_out,
        )
        if args.dry_run:
            return _emit({"ok": True, "dry_run": True, "conversion_plan": plan.to_dict()}, out=args.json_out, compact=args.compact)
        result = convert_voice_file(plan)
        return _emit(result, out=args.json_out, compact=args.compact)
    if args.command == "train-profile":
        manifest = build_family_registry_training_manifest(
            args.registry,
            role=args.role,
            profile_id=args.profile_id,
        )
        return _emit(manifest, out=args.out, compact=args.compact)
    if args.command == "train-native":
        model = train_native_voice_model(
            args.registry,
            role=args.role,
            profile_id=args.profile_id,
        )
        return _emit(model, out=args.out, compact=args.compact)
    return 2


def _build_script(args: argparse.Namespace):
    pronunciation_dict = load_pronunciation_dict(args.dict_path)
    if args.file:
        return normalize_file(args.file, pronunciation_dict=pronunciation_dict, g2p_mode=args.g2p)
    if args.text:
        return normalize_text(args.text, pronunciation_dict=pronunciation_dict, g2p_mode=args.g2p)
    raise SystemExit("Either text or --file is required.")


def _emit(data: dict, *, out: str | None, compact: bool) -> int:
    indent = None if compact else 2
    output = json.dumps(data, ensure_ascii=False, indent=indent)
    if out:
        output_path = Path(out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")
    return 0


def _tail(text: str, *, line_count: int = 40) -> str:
    return "\n".join(text.splitlines()[-line_count:])
