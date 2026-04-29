# 외부 검토: Voice-Pro와 Nemotron-Personas-Korea

[English document](EXTERNAL_REVIEW_VOICE_PRO_NEMOTRON.md)

## Voice-Pro

저장소: https://github.com/abus-aikorea/voice-pro

로컬 검토용 클론은 KVAE repo 안이 아니라 사용자 workspace의 외부 검토 폴더에 받았습니다.

라이선스 판단:

- GitHub 기준 GNU GPLv3입니다.
- 실제로 클론한 `LICENSE` 파일도 GNU GPL v3입니다.
- KVAE는 Apache-2.0이므로 Voice-Pro 코드를 KVAE 안으로 복사하면 안 됩니다.

KVAE에 반영할 만한 점:

- ASR, 자막, 번역, 음원 분리, TTS, 보이스 클로닝을 탭/단계로 분리한 구조
- WAV, SRT, TXT, JSON, manifest 같은 산출물 기반 도구 간 연동
- 모델이 무거운 기능은 선택형 외부 도구로 두는 방식
- 창작자용 WebUI는 필요하지만, KVAE 핵심 CLI는 작고 검증 가능하게 유지하는 방향

안전한 적용 방식:

- `kva capabilities`의 외부 대체 프로그램으로 Voice-Pro를 추가합니다.
- Whisper, Demucs, Edge-TTS, F5-TTS, CosyVoice, RVC, 자막, 번역 실험은 Voice-Pro에서 별도 실행합니다.
- 결과 WAV/SRT/TXT/JSON만 KVAE로 가져와 `kva review-audio`, 출처 기록, 사용처별 polish를 적용합니다.
- Voice-Pro 소스 코드는 KVAE에 vendoring하지 않습니다.

## NVIDIA Nemotron-Personas-Korea

데이터셋: https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea

라이선스: CC-BY-4.0.

확인한 데이터 특성:

- 한국어 텍스트 데이터셋입니다.
- 합성 페르소나입니다.
- 1,000,000개 행으로 구성되어 있습니다.
- 페르소나 필드, 속성 필드, 인구통계/지리 컨텍스트, UUID 등 26개 필드가 있습니다.
- 대한민국 법령상 성인 연령인 만 19세 이상 페르소나만 포함합니다.
- 음성, speaker embedding, 실제 녹음은 없습니다.

KVAE에 반영할 만한 점:

- 한국어 녹음 프롬프트를 더 다양하게 만들 수 있습니다.
- 드라마, 숏츠, 교육, 다큐, 공지 대본을 페르소나 기반으로 만들 수 있습니다.
- 나이, 지역, 직업, 가족 맥락, 취미, 말하는 상황을 검수 케이스에 반영할 수 있습니다.
- 서울/젊은 층/사무직 중심의 획일적 예시를 줄일 수 있습니다.

안전한 적용 방식:

- `kva capabilities`에 `persona_script_coverage` 라우트를 추가합니다.
- 이 데이터셋은 텍스트 프롬프트 소스로만 사용하고, 음성 학습 데이터로 취급하지 않습니다.
- 이 데이터셋에서 파생한 프롬프트나 평가 케이스를 만들 때 NVIDIA Nemotron-Personas-Korea 출처를 표기합니다.
- 아이 목소리, 실제 인물 정체성, 특정 화자의 녹음이 있다고 주장하지 않습니다.
