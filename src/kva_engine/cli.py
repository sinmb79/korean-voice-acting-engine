from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kva_engine.acting.planner import plan_voice_acting
from kva_engine.acting.presets import PRESETS
from kva_engine.korean.normalizer import load_pronunciation_dict, normalize_file, normalize_text
from kva_engine.training.family_registry import build_family_registry_training_manifest
from kva_engine.training.native_voice_model import train_native_voice_model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kva", description="Korean Voice Acting Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser("normalize", help="Create Korean speech_script JSON")
    normalize_parser.add_argument("text", nargs="?", help="Display text to normalize")
    normalize_parser.add_argument("--file", help="UTF-8 text file to normalize")
    normalize_parser.add_argument("--dict", dest="dict_path", help="Pronunciation dictionary JSON")
    normalize_parser.add_argument("--out", help="Output JSON path")
    normalize_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    cast_parser = subparsers.add_parser("cast", help="Apply a voice acting role to normalized text")
    cast_parser.add_argument("text", nargs="?", help="Display text to normalize and cast")
    cast_parser.add_argument("--file", help="UTF-8 text file to normalize and cast")
    cast_parser.add_argument("--dict", dest="dict_path", help="Pronunciation dictionary JSON")
    cast_parser.add_argument("--role", default="calm_narrator", choices=sorted(PRESETS))
    cast_parser.add_argument("--out", help="Output JSON path")
    cast_parser.add_argument("--compact", action="store_true", help="Print compact JSON")

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
    if args.command == "normalize":
        script = _build_script(args)
        return _emit(script.to_dict(), out=args.out, compact=args.compact)
    if args.command == "cast":
        script = _build_script(args)
        plan = plan_voice_acting(script, role=args.role)
        return _emit(plan, out=args.out, compact=args.compact)
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
        return normalize_file(args.file, pronunciation_dict=pronunciation_dict)
    if args.text:
        return normalize_text(args.text, pronunciation_dict=pronunciation_dict)
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
