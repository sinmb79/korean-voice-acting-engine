from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from kva_engine.public_voices import load_public_voice_catalog
from kva_engine.voice_profile import default_local_voice_config, load_voice_profile


def run_doctor(*, voice_profile_path: str | Path | None = None) -> dict[str, Any]:
    checks = [
        _python_check(),
        _catalog_check(),
        _ffmpeg_check("ffmpeg"),
        _ffmpeg_check("ffprobe"),
        _optional_import_check("whisper", purpose="ASR review"),
        _voice_profile_check(voice_profile_path),
        _gitignore_check(),
    ]
    return {
        "tool": "kva doctor",
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "python": sys.version.split()[0],
        },
        "status": _overall_status(checks),
        "checks": checks,
        "summary": _summary(checks),
    }


def _python_check() -> dict[str, Any]:
    ok = sys.version_info >= (3, 11)
    return {
        "name": "python_version",
        "status": "pass" if ok else "fail",
        "message": f"Python {sys.version.split()[0]}",
        "required": ">=3.11",
    }


def _catalog_check() -> dict[str, Any]:
    try:
        catalog = load_public_voice_catalog()
    except Exception as exc:
        return {
            "name": "public_voice_catalog",
            "status": "fail",
            "message": f"Public voice catalog failed to load: {exc}",
        }
    return {
        "name": "public_voice_catalog",
        "status": "pass",
        "message": f"{len(catalog.get('voices', []))} public voice entries available",
        "catalog_version": catalog.get("catalog_version"),
    }


def _ffmpeg_check(binary_name: str) -> dict[str, Any]:
    binary = shutil.which(binary_name)
    if not binary:
        return {
            "name": binary_name,
            "status": "warn",
            "message": f"{binary_name} not found in PATH",
            "fix": f"Install {binary_name} and make sure it is available in PATH.",
        }
    version = _first_line([binary, "-version"])
    return {
        "name": binary_name,
        "status": "pass",
        "message": version or f"{binary_name} is available",
        "path": binary,
    }


def _optional_import_check(module_name: str, *, purpose: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return {
            "name": f"python_module:{module_name}",
            "status": "warn",
            "message": f"{module_name} is not installed; {purpose} features will be limited.",
        }
    return {
        "name": f"python_module:{module_name}",
        "status": "pass",
        "message": f"{module_name} is importable",
    }


def _voice_profile_check(path: str | Path | None) -> dict[str, Any]:
    try:
        profile = load_voice_profile(path)
    except Exception as exc:
        return {
            "name": "voice_profile",
            "status": "fail",
            "message": f"Voice profile failed to load: {exc}",
        }
    if profile is None:
        return {
            "name": "voice_profile",
            "status": "warn",
            "message": "No default voice profile configured.",
            "fix": f"Create {default_local_voice_config()} or pass --voice-profile.",
        }
    if profile.get("public_voice"):
        return {
            "name": "voice_profile",
            "status": "pass",
            "message": f"Public AI voice profile selected: {profile.get('id')}",
            "privacy": profile.get("privacy"),
            "license": profile.get("license"),
        }
    if not profile.get("exists"):
        return {
            "name": "voice_profile",
            "status": "warn",
            "message": f"Voice profile is configured but its reference asset is missing: {profile.get('id')}",
            "profile": _safe_profile_summary(profile),
        }
    return {
        "name": "voice_profile",
        "status": "pass",
        "message": f"Local private voice profile available: {profile.get('id')}",
        "profile": _safe_profile_summary(profile),
    }


def _gitignore_check() -> dict[str, Any]:
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        return {
            "name": "private_asset_gitignore",
            "status": "warn",
            "message": ".gitignore is not available from the current working directory.",
        }
    text = gitignore.read_text(encoding="utf-8")
    required = [
        "configs/*.local.json",
        "*.wav",
        "*.m4a",
        "*.safetensors",
        "outputs/*",
    ]
    missing = [pattern for pattern in required if pattern not in text]
    return {
        "name": "private_asset_gitignore",
        "status": "pass" if not missing else "fail",
        "message": "Private voice/model patterns are ignored." if not missing else "Missing private ignore patterns.",
        "missing": missing,
    }


def _overall_status(checks: list[dict[str, Any]]) -> str:
    statuses = {check["status"] for check in checks}
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"


def _summary(checks: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "pass": sum(1 for check in checks if check["status"] == "pass"),
        "warn": sum(1 for check in checks if check["status"] == "warn"),
        "fail": sum(1 for check in checks if check["status"] == "fail"),
    }


def _first_line(command: list[str]) -> str | None:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    output = completed.stdout or completed.stderr
    return output.splitlines()[0] if output else None


def _safe_profile_summary(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": profile.get("id"),
        "privacy": profile.get("privacy"),
        "exists": profile.get("exists"),
        "public_voice": profile.get("public_voice", False),
    }
