# 외부 검토: MOSS-TTS-Nano, VoxCPM, VibeVoice

[English document](EXTERNAL_REVIEW_TTS_BACKENDS.md)

이 문서는 새로 검토한 세 음성 AI 저장소를 KVAE에서 어떻게 다룰지 정리합니다.

## 결정

KVAE는 VoxCPM2를 현재 기본 렌더 백엔드로 유지합니다. MOSS-TTS-Nano는 가벼운 CPU/ONNX 대체 후보로 평가하고, VibeVoice-Realtime은 한국어 연구 후보로만 둡니다. VibeVoice-ASR은 장문 녹음의 대본 검수 후보로 따로 볼 가치가 있습니다.

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine tts-backends
python -m kva_engine tts-backends --production-only
python -m kva_engine tts-backends --id moss_tts_nano --compact
```

## 1. MOSS-TTS-Nano

저장소: https://github.com/OpenMOSS/MOSS-TTS-Nano

로컬 검토 스냅샷:

- Git commit: `64380f81651d89cc18741a247e3feb3ec33ba344`
- License: Apache-2.0

확인한 특징:

- 0.1B 파라미터의 다국어 음성 생성 모델입니다.
- 한국어가 20개 지원 언어 중 하나로 표시되어 있습니다.
- CPU 친화적이고 streaming 지향입니다.
- ONNX CPU inference 경로가 있으며, inference 단계에서 PyTorch 의존을 제거할 수 있습니다.
- prompt audio 기반 voice cloning이 기본 워크플로입니다.
- fine-tuning 코드가 제공됩니다.

KVAE에 유용한 점:

- GPU가 없는 사용자에게 줄 수 있는 저사양, 오프라인, CPU 한국어 음성 실험 후보입니다.
- VoxCPM2를 돌리기 어려운 환경의 fallback 후보가 될 수 있습니다.
- ONNX 경로는 향후 Windows 설치형 배포를 단순화할 가능성이 있습니다.

경계:

- 아직 `kva render`에 연결하지 않았습니다.
- 한국어 품질은 KVAE review report와 실제 청취 검수를 거친 뒤 승격해야 합니다.
- Windows에서는 텍스트 정규화 패키지 설치가 까다로울 수 있습니다.

## 2. VoxCPM / VoxCPM2

저장소: https://github.com/OpenBMB/VoxCPM

로컬 검토 스냅샷:

- Git commit: `19b6bf7590025418821a86dcb817504e0ad7e5df`
- License: Apache-2.0

확인한 특징:

- VoxCPM2가 현재 주요 release입니다.
- 2B 파라미터, 30개 언어 지원이며 한국어가 공식 지원 목록에 포함되어 있습니다.
- voice design, controllable voice cloning, prompt/audio continuation cloning, 48kHz 출력, streaming, LoRA, full fine-tuning을 지원합니다.
- 저장소는 코드와 weight가 Apache-2.0이며 상업 사용 준비가 되어 있다고 설명합니다.
- 일반 로컬 실행은 CUDA급 환경을 전제로 하며, 문서상 Python >=3.10,<3.13, PyTorch >=2.5, CUDA >=12가 필요합니다.

KVAE에 유용한 점:

- 이미 KVAE의 `kva render --engine voxcpm` 경로와 맞습니다.
- 이 저장소에서 현재 가장 현실적인 한국어 private reference voice 실험 백엔드입니다.
- MOSS와 VibeVoice를 평가하는 동안 기본값으로 유지합니다.

경계:

- voice cloning은 악용될 수 있으므로 모든 결과물에 동의, 출처, AI 고지를 남겨야 합니다.
- voice design과 controllable cloning은 생성마다 결과가 달라질 수 있으므로 `kva review-audio`와 사람의 A/B 청취 검수를 유지해야 합니다.
- 아이, 크리처, 완전히 다른 성우를 설득력 있게 만든다고 약속하는 용도로 쓰면 안 됩니다.

## 3. VibeVoice

저장소: https://github.com/microsoft/VibeVoice

로컬 검토 스냅샷:

- Git commit: `e73d1e17c3754f046352014856a922f8208fb5d3`
- License: MIT

확인한 특징:

- VibeVoice는 ASR과 TTS 연구 모델을 포함한 음성 AI family입니다.
- 저장소는 이전 VibeVoice-TTS 코드가 오용 우려 이후 제거되었다고 밝힙니다.
- VibeVoice-Realtime-0.5B는 streaming TTS 모델로 공개되어 있습니다.
- Realtime TTS의 중심 언어는 영어이며, 한국어는 실험적 multilingual exploration voice로만 제공됩니다.
- 문서는 추가 테스트 없이는 commercial 또는 real-world application 사용을 권장하지 않습니다.
- VibeVoice-ASR은 60분 single-pass transcription, speaker/timestamp/content 구조, hotword, 50개 이상 언어를 지원합니다.

KVAE에 유용한 점:

- VibeVoice-Realtime은 streaming TTS 구조 연구 참고자료로 의미가 있습니다.
- VibeVoice-ASR은 긴 한국어 녹음에서 chunked ASR이 화자/context를 놓칠 때 검토할 후보입니다.

경계:

- VibeVoice-Realtime을 기본 한국어 TTS 백엔드로 만들면 안 됩니다.
- 한국어 상업 제작 경로로 쓰기 전에는 로컬 품질 테스트와 안전성 검토가 필요합니다.
- ASR 결과는 초안으로 보고, 사람의 대본 교정 과정을 거쳐야 합니다.

## KVAE 반영

- `kva tts-backends` 명령을 추가해 검토한 백엔드 후보를 볼 수 있게 했습니다.
- `kva capabilities`에 `korean_tts_backend_selection` 경로를 추가했습니다.
- `kva capabilities`에 `long_form_asr_and_diarization` 경로를 추가했습니다.
- VoxCPM2를 production 기본값으로 유지했습니다.
- MOSS-TTS-Nano와 VibeVoice는 shipped backend가 아니라 후보로 표시했습니다.
