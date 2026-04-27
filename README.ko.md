# Korean Voice Acting Engine

[English README](README.md)

메타 설명: 한국어를 먼저 이해하고, 한 사람의 목소리를 여러 배역으로 확장하는 로컬 우선 성우 TTS 엔진.

레이블/태그: 한국어 TTS, 성우 엔진, 음성 학습, 로컬 AI, 오픈소스, 22B Labs, The 4th Path

## 왜 이 프로젝트가 존재하나

좋은 TTS는 글자를 소리로 바꾸는 도구에서 끝나지 않습니다. 특히 한국어는 숫자, 영어 약어, 조사, 억양, 문장 끝의 높낮이가 조금만 어긋나도 바로 낯선 외래어처럼 들립니다.

이 프로젝트는 기존 영어/중국어 중심 TTS 엔진에 한국어를 억지로 붙이는 대신, 한국어를 먼저 읽고 해석한 뒤 목소리와 배역을 연결하는 엔진을 만들기 위해 시작했습니다.

목표는 분명합니다. 한 사람이 제공한 음성을 바탕으로, 그 사람의 정체성은 남기되 성우처럼 여러 배역의 말투로 확장하는 것입니다.

## 현재 들어있는 것

- 한국어 숫자, 영어, 약어, 기호 읽기 정규화
- 날짜, 시간, 전화번호, 조사 결합 보조 규칙
- `speech_text`, `phoneme_text`, `normalization_trace` 생성
- SSML 변환과 생성/검증 manifest 출력
- 성우 배역 프리셋: 내레이터, 다큐멘터리, 뉴스, 선생님, 노인 이야기꾼, 낮은 악역, 빠른 아이 목소리, AI 어시스턴트, 늑대, 괴물, 공룡, 어린이
- 로컬 기본 음성 프로필 자동 연결: `configs/default_voice.local.json`
- 가족 음성 레지스트리 분석기
- KVA 자체 모델 포맷: `kva.native_voice_model.v1`
- 보안 환경용 로컬 학습 준비 CLI
- 녹음 음성 입력 기반 캐릭터 변환 CLI: `kva convert`
- 한 번의 녹음으로 여러 후보를 만드는 제품형 워크플로: `kva voice-lab`
- 오디오 품질, ASR, CER/WER 검증 CLI: `kva review-audio`
- 공개 한국어 AI 음성 카탈로그: 출처, 라이선스, 표기문, AI 음성 고지 포함
- 테스트 코드와 개발구현서

## 빠르게 실행하기

개발자가 아닌 사람도 목적을 이해할 수 있게 말하면, 첫 명령은 “한국어 문장을 TTS가 읽기 좋은 대본으로 바꾸는 일”입니다.

```powershell
cd korean-voice-acting-engine
$env:PYTHONPATH = "src"
python -m kva_engine normalize --file data\sample_input.txt --out outputs\sample.speech.json
```

다음 명령은 같은 문장에 성우 배역을 얹습니다.

```powershell
python -m kva_engine cast --file data\sample_input.txt --role old_storyteller --out outputs\sample.cast.json
```

로컬 기본 목소리가 제대로 연결되었는지는 아래처럼 확인합니다.

```powershell
python -m kva_engine voice-profile
```

공개 한국어 AI 음성 후보는 아래처럼 확인합니다.

```powershell
python -m kva_engine public-voices
python -m kva_engine voice-profile public:mms-tts-kor
```

로컬 실행 환경과 안전 설정은 아래처럼 점검합니다.

```powershell
python -m kva_engine doctor --voice-profile public:mms-tts-kor
```

녹음 파일 하나로 여러 성우/캐릭터 후보를 한 번에 만들 수 있습니다.

```powershell
python -m kva_engine voice-lab `
  --input my_voice.wav `
  --out-dir outputs\voice-lab-demo `
  --group default `
  --expected-file script.txt `
  --asr-model base
```

SSML과 생성 manifest도 바로 만들 수 있습니다.

```powershell
python -m kva_engine ssml --file data\sample_input.txt --out outputs\sample.ssml.json
python -m kva_engine manifest --script outputs\sample.speech.json --role old_storyteller --out outputs\sample.manifest.json
```

## Codex를 통한 음성 학습

이 프로젝트의 기본 방향은 보스 PC에서 Codex가 KVAE 명령을 실행해 로컬 학습과 검증을 반복하는 것입니다.

```powershell
python -m kva_engine train-native `
  --registry C:\Users\you\workspace\shared-voices `
  --profile-id my-voice-profile `
  --out outputs\family_voice_training\kva_native_voice_model.json
```

현재 보안 환경처럼 `torch`, `torchaudio`, `numpy`가 없는 곳에서는 파형을 직접 생성하는 신경망 학습까지는 가지 않습니다. 대신 KVA가 사용할 음성 정체성 seed, acoustic profile, role control layer를 만듭니다.

집 컴퓨터나 GPU 환경에서는 이 모델 파일을 출발점으로 삼아 Korean acoustic model, duration predictor, pitch/energy predictor, neural vocoder를 이어 붙이면 됩니다.

녹음 원본은 먼저 점검합니다.

```powershell
python -m kva_engine recording-check `
  --audio C:\Users\you\workspace\shared-voices\my-voice\references\voice_ko_reference.wav `
  --out outputs\recording-check.json
```

## 공개 배포와 가족 음성 보호

이 저장소는 코드와 문서를 공개하기 위한 저장소입니다. 가족 음성 원본, private dataset, checkpoint, LoRA weight, generated output은 `.gitignore`로 제외되어 있습니다.

목소리는 단순한 샘플이 아니라 사람의 흔적입니다. 공개할 수 있는 것은 엔진이고, 보호해야 하는 것은 사람입니다.

`configs/*.local.json`도 공개 추적에서 제외됩니다. 개인 기본 목소리는 로컬 설정에서 private 음성 폴더를 가리키며, 실제 오디오 파일은 저장소에 복사하지 않습니다.

## 검증

개발 환경에서 아래 명령으로 테스트합니다.

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m compileall -q src
```

## 문서

- `docs/CODEX_TRAINING_WORKFLOW.md`: Codex 기반 로컬 학습 워크플로
- `docs/DEVELOPMENT_ROADMAP.md`: 남은 개발 과정과 완료 기준
- `docs/DEVELOPMENT_IMPLEMENTATION_SPEC.md`: 전체 개발구현서
- `docs/RESEARCH_REVIEW.md`: 공개 프로그램, 논문, 국내외 사례 검토
- `docs/KVA_NATIVE_TRAINING.md`: KVA 네이티브 학습 방향
- `docs/FAMILY_VOICE_TRAINING.md`: 가족 음성 레지스트리 기반 학습 기록
- `docs/KVAE_RENDER_ENGINE.md`: 로컬 VoxCPM 렌더 경로
- `docs/KVAE_CONVERT_ENGINE.md`: 녹음 음성 입력 기반 캐릭터 변환 경로
- `docs/VOICE_LAB_WORKFLOW.md`: 한 번의 녹음에서 여러 목소리 후보 생성
- `docs/KVAE_REVIEW_ENGINE.md`: 오디오 품질, ASR, WER/CER 검증 경로
- `docs/PUBLIC_VOICE_CATALOG.md`: 공개 한국어 AI 음성 카탈로그
- `docs/RELEASE_QUALITY_GATES.md`: 릴리스 품질 게이트
- `docs/SAFETY_POLICY.md`: 음성/동의/공개 정책
- `docs/SECURE_DEVELOPMENT.md`: 보안 환경 개발 원칙

## 제작자의 철학

한국어를 먼저 존중해야 한국어 목소리가 살아납니다.

이 프로젝트는 빠른 흉내보다 느린 이해를 택합니다. 사람의 목소리를 빌리는 기술은, 사람을 지우지 않을 때 비로소 쓸 만해집니다.

작성자: **22B Labs · 제4의 길 (The 4th Path)**
