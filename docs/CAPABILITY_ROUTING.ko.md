# 기능 라우팅

[English document](CAPABILITY_ROUTING.md)

KVAE의 제품 경계를 더 엄격하게 정리했습니다.

- **KVAE 안에서 처리**: 한국어 대본 정리, 녹음 검수, 프라이버시 안전 학습 준비, 원래 화자를 보존하는 한국어 음성 폴리싱
- **외부 프로그램으로 대체**: 다른 사람 목소리, 설득력 있는 아이 목소리, 크리처/공룡 사운드 디자인, 심한 노이즈/반향 복원, 영상 더빙/편집
- **연구 기능으로만 유지**: 실험에는 의미가 있지만 제품 품질로 약속하면 안 되는 KVAE 내부 기능

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine capabilities --production-only
python -m kva_engine capabilities --task child_or_age_voice --compact
python -m kva_engine tts-backends --production-only
```

## KVAE 제품 범위

일반 사용자 기능으로 제공할 것은 다음입니다.

- `kva normalize`, `kva ssml`, `kva cast`: 한국어 음성용 대본 준비
- `kva recording-check`, `kva review-audio`, 학습 데이터 준비 명령
- `kva polish`: cleanup, announcer, shorts, drama, documentary 프리셋 기반 음성 손질
- `kva tts-backends`: 검토된 TTS/ASR 백엔드 상태와 선택 기준
- `kva source-library`: 음원 출처 라이브러리 schema와 라이선스 gate

이 기능들은 원래 화자의 정체성을 보존합니다. 새로운 성우, 아이, 괴물, 늑대, 공룡 목소리를 만든다고 약속하지 않습니다.

## 외부 대체 범위

다음 작업은 전문 도구가 필요합니다.

- 다른 사람 목소리: 동의된 대상 목소리가 있는 [Resemble AI Speech-to-Speech](https://www.resemble.ai/products/speech-to-speech) 또는 [ElevenLabs Voice Changer](https://elevenlabs.io/voice-changer)
- 아이/연령 변환 목소리: [NAVER Cloud CLOVA Dubbing](https://guide.ncloud-docs.com/docs/en/clovadubbing-overview), [Vrew](https://vrew.ai/ko/) 같은 라이선스 확인 가능한 음성 라이브러리/더빙 도구
- 크리처/괴물/공룡: [Krotos Dehumaniser 2](https://www.krotosaudio.com/dehumaniser2/)와 DAW, 그리고 라이선스 안전한 동물/폴리/합성 소스
- 심한 노이즈/반향 복원: [iZotope RX Dialogue Isolate](https://www.izotope.com/en/products/rx/features/dialogue-isolate), [Adobe Podcast Enhance Speech](https://podcast.adobe.com/en/enhance-speech-v2), [Descript Studio Sound](https://help.descript.com/hc/en-us/articles/10327603613837-Studio-Sound)
- 로컬 통합 실험: [Voice-Pro](https://github.com/abus-aikorea/voice-pro)는 ASR, 자막, 번역, TTS, 보이스 클로닝 테스트용 GPLv3 WebUI로 별도 실행합니다. KVAE는 WAV/SRT/TXT/JSON 산출물만 주고받고 코드는 복사하지 않습니다.
- 영상 내레이션 API workflow: [Narrator AI CLI Skill](https://github.com/NarratorAI-Studio/narrator-ai-cli-skill)은 `NARRATOR_APP_KEY`와 명시적 resource/task 확인이 필요한 별도 MIT agent workflow로만 사용합니다.
- 최종 시각/립싱크 조립: [Open Generative AI](https://github.com/Anil-matcha/Open-Generative-AI)는 라이선스와 안전 검토 뒤 별도 이미지/영상/립싱크 studio로만 사용합니다.
- 영상 조립/자막/최종 편집: Vrew, DaVinci Resolve/Fairlight, 또는 별도 영상 편집기

## TTS와 ASR 백엔드 범위

KVAE는 현재 [VoxCPM2](https://github.com/OpenBMB/VoxCPM)를 `kva render --engine voxcpm`의 기본 렌더 백엔드로 둡니다. Apache-2.0이며 한국어가 공식 지원 언어에 포함됩니다.

[MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano)는 Apache-2.0 기반의 가벼운 CPU/ONNX 연구 후보입니다. 한국어가 지원 언어에 포함되어 있지만, KVAE에서 한국어 명료도 검수를 통과하기 전까지는 후보로 둡니다.

[VibeVoice](https://github.com/microsoft/VibeVoice)는 MIT입니다. VibeVoice-Realtime은 한국어가 실험적 지원이므로 연구 후보로만 둡니다. VibeVoice-ASR은 장문 ASR/화자분리 검수 후보이지, 현재 KVAE core dependency가 아닙니다.

## 음향효과 라이브러리 범위

검토한 Quark 공유자료 `百万剪辑狮的音效库`는 큰 SFX collection으로 보이지만, 확인한 공유 metadata 안에서는 재배포권이나 상업 사용권이 보이지 않았습니다. KVAE는 라이선스가 확인되기 전까지 분류 참고자료로만 사용합니다. 음원 파일을 KVAE에 직접 넣거나 재배포하지 않습니다.

## 페르소나 데이터셋 범위

[NVIDIA Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)는 한국 인물 페르소나 다양성을 대본 프롬프트와 검수 케이스에 반영할 때 유용합니다. 음성 데이터셋이 아니므로 녹음, speaker embedding, 아이 목소리를 제공하지 않습니다. KVAE에서는 CC-BY-4.0 출처 표기와 함께 텍스트 기반 프롬프트 다양성 용도로만 사용합니다.

## 권장 제작 흐름

1. KVAE에서 한국어 대본을 정리합니다.
2. 깨끗한 WAV를 녹음하거나 가져옵니다.
3. `kva recording-check`를 실행합니다.
4. 사용처에 맞게 `kva polish`를 실행합니다.
5. KVAE의 안정 범위를 벗어나는 요청은 기능 라우터가 제안하는 외부 프로그램으로 보냅니다.
6. 완성 오디오는 다시 `kva review-audio`로 검수하고, 출처/라이선스/AI 음성 고지 정보를 남깁니다.

이렇게 하면 KVAE는 잘할 수 있는 일만 정확히 하고, 전문 도구나 사람 성우가 필요한 부분은 억지로 흉내 내지 않습니다.
