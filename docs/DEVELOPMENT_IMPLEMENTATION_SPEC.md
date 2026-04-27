# Korean Voice Acting Engine 개발 구현서

메타 설명: 한국어 엔진과 성우 엔진을 분리해, 일반인의 목소리를 다양한 배역 음성으로 확장하는 무료 오픈소스 TTS 프로젝트.

작성자: 22B Labs · 제4의 길 (The 4th Path)

태그: 한국어 TTS, 성우 엔진, 음성 합성, 보이스 캐스팅, 한국어 전처리, 발음 사전, 오픈소스, 로컬 우선

---

## 1. 왜 이 프로젝트가 존재해야 하는가

기존 공개 TTS 엔진은 대체로 영어 또는 중국어 중심으로 설계되어 있다. 한국어는 단순히 지원 언어 목록에 들어갈 수는 있지만, 실제 제작 과정에서는 숫자, 영어 약어, 외래어, 조사, 받침, 연음, 호흡, 문장 끝 억양에서 계속 부자연스러움이 발생한다.

일반인은 성우처럼 여러 배역을 자유롭게 연기하기 어렵다. 한 사람에게는 대개 한 가지 자연스러운 목소리만 있고, 영상 제작에는 노인, 아이, 해설자, 안내자, 악역, 뉴스톤, 다큐톤처럼 여러 음성이 필요하다.

이 프로젝트는 두 문제를 하나의 구조로 해결한다.

첫째, 한국어를 먼저 제대로 읽는 엔진을 만든다.

둘째, 성우가 목소리를 바꿀 때 쓰는 발성, 호흡, 억양, 감정, 캐릭터 해석 원리를 파라미터화해 사용자의 목소리에 적용한다.

목표는 사람의 목소리를 훔치는 것이 아니다. 사용자가 동의해 제공한 자기 목소리를 바탕으로, 자기 창작 세계에 필요한 여러 배역을 만들 수 있게 하는 것이다.

## 2. 프로젝트 정의

프로젝트명: Korean Voice Acting Engine

짧은 이름: KVA Engine

한국어 제품명 후보: 성우 엔진

한 문장 정의:

> 한국어 엔진으로 대본을 사람처럼 읽게 만들고, 성우 엔진으로 일반인의 목소리를 여러 배역으로 연기시키는 무료 오픈소스 한국어-first 음성 제작 엔진.

핵심 원칙:

- 기존 완성형 TTS 엔진에 단순 래핑하지 않는다.
- 한국어 전처리, 발음, 호흡, 억양 계획은 직접 구현한다.
- 음성 생성 모델도 장기적으로 자체 학습을 목표로 한다.
- 초기 연구 단계에서 논문, 공개 아키텍처, 공개 데이터셋은 참고할 수 있지만, 배포 모델은 라이선스와 동의가 깨끗한 데이터만 사용한다.
- 유명인, 실제 성우, 제3자 목소리를 무단 복제하는 기능은 넣지 않는다.

## 3. 전체 아키텍처

```text
display_text
  |
  v
Korean Engine
  - text normalization
  - English/number Korean reading conversion
  - josa and spacing handling
  - Korean pronunciation planning
  - breath and phrase planning
  |
  v
speech_script
  |
  v
Voice Acting Engine
  - role preset
  - acting parameters
  - emotion pressure
  - pace and breath
  - resonance and articulation
  |
  v
acoustic_plan
  |
  v
Neural Speech Engine
  - acoustic model
  - voice identity adapter
  - style/role adapter
  - vocoder
  |
  v
wav/mp3 output
  |
  v
Review Engine
  - ASR validation
  - pronunciation error detection
  - noise and clipping check
  - correction memory update
```

## 4. 모듈 구성

### 4.1 Korean Engine

역할: 원문을 TTS가 그대로 읽게 하지 않고, 한국어 성우가 읽을 수 있는 악보로 바꾼다.

주요 기능:

- 표시용 텍스트와 읽기용 텍스트 분리
- 영어 약어 한글 낭독 변환
- 숫자, 날짜, 시간, 금액, 전화번호, 버전, 단위 변환
- 브랜드명, 프로젝트명, 기술 용어 사용자 발음 사전 적용
- 조사 결합 처리
- 한국어 발음 규칙 적용
- 문장 길이에 따른 호흡 단위 분할
- 강조와 문장 끝 억양 후보 생성

예시:

```text
display_text:
OpenAI API는 3.5초 안에 응답했다.

speech_text:
오픈에이아이 에이피아이는 삼 점 오 초 안에 응답했다.
```

숫자 변환 기본 규칙:

```text
3.5초       -> 삼 점 오 초
2026년      -> 이천이십육 년
010-1234    -> 공일공 일이삼사
v2.1        -> 버전 이 점 일
22B Labs    -> 이십이비 랩스
3월 5일     -> 삼월 오일
3-5단계     -> 삼에서 오 단계
```

영어/약어 변환 기본 규칙:

```text
AI      -> 에이아이
API     -> 에이피아이
TTS     -> 티티에스
OpenAI  -> 오픈에이아이
LoRA    -> 로라
Codex   -> 코덱스
JSON    -> 제이슨
```

### 4.2 Korean Pronunciation Planner

역할: 한글 표기를 실제 발음 계획으로 바꾼다.

초기에는 규칙 기반으로 구현하고, 이후 오류 로그를 쌓아 하이브리드 방식으로 확장한다.

다룰 규칙:

- 연음
- 경음화
- 비음화
- 유음화
- 받침 단순화
- 겹받침 처리
- 조사 결합에 따른 발음 변화
- 외래어와 영어 약어 뒤 조사 처리

예시 테스트 케이스:

```text
국립       -> 궁닙
읽는       -> 익는
값이       -> 갑씨 또는 갑시 계열 검토
신라       -> 실라
AI가       -> 에이아이가
API를      -> 에이피아이를
```

주의:

- 하나의 정답만 강제하지 않는다.
- 낭독체, 대화체, 뉴스체에 따라 허용 발음과 호흡이 다를 수 있다.
- 사용자 사전이 항상 기본 규칙보다 우선한다.

### 4.3 Voice Acting Engine

역할: 성우의 연기 노하우를 파라미터로 바꾸고, 한국어 엔진이 만든 speech_script에 배역을 입힌다.

성우 연기 요소:

- 평균 피치
- 피치 변화폭
- 말 속도
- 단어 사이 간격
- 문장 사이 호흡
- 숨소리 양
- 자음 선명도
- 모음 길이
- 공명 위치 느낌
- 문장 끝 상승/하강
- 감정 압력
- 감정 절제 정도
- 나이감
- 체격감
- 사회적 거리감

캐릭터 프리셋 예시:

```json
{
  "name": "old_storyteller",
  "label": "따뜻한 노년 이야기꾼",
  "pitch": -4,
  "pitch_variance": 0.65,
  "speed": 0.78,
  "breath": 0.45,
  "articulation": "soft",
  "resonance": "chest",
  "pause_style": "long_reflective",
  "sentence_end": "low_falling",
  "emotion": "warm_regret"
}
```

초기 프리셋:

- calm_narrator: 차분한 내레이터
- documentary: 다큐멘터리 해설자
- news_anchor: 명료한 뉴스 앵커
- bright_teacher: 밝은 강의자
- old_storyteller: 따뜻한 노년 이야기꾼
- villain_low: 낮고 절제된 악역
- childlike_fast: 가볍고 빠른 어린 캐릭터
- ai_assistant: 또렷하고 친절한 안내 음성

### 4.4 Neural Speech Engine

역할: acoustic_plan을 실제 음성으로 합성한다.

장기 목표:

- 외부 완성형 TTS 엔진 없이 자체 한국어 음성 합성 모델을 학습한다.
- PyTorch, torchaudio, librosa, soundfile 같은 일반 ML/오디오 라이브러리는 사용할 수 있다.
- VITS, FastSpeech2, diffusion/flow 기반 TTS 논문 구조는 참고 가능하지만, 제품 백엔드는 자체 학습 모델로 둔다.

단계별 모델 전략:

```text
Stage 1: 단일 화자 한국어 TTS
  - 사용자의 목소리 30분~3시간
  - 한국어 낭독 안정성 검증

Stage 2: 화자 정체성 어댑터
  - 사용자의 목소리 특징을 별도 embedding/adaptor로 분리
  - 대본 내용과 음색을 분리하는 구조 실험

Stage 3: 성우 스타일 어댑터
  - 캐릭터 프리셋을 acoustic feature에 반영
  - pitch, duration, energy, pause, breath control 학습

Stage 4: 다화자/다스타일 한국어 모델
  - 동의 기반 데이터셋으로 여러 성별, 연령감, 연기 스타일 확장
```

### 4.5 Review & Correction Engine

역할: 생성 결과를 사람이 매번 귀로만 고치지 않게 만든다. 한 번 틀린 발음은 시스템에 남아야 한다.

검수 항목:

- 생성 음성을 STT로 다시 인식
- 원문 display_text와 speech_text 기준으로 CER/WER 비교
- 사용자가 지정한 발음 사전 적용 여부 확인
- 잡음, 클리핑, 무음 과다, 음량 편차 탐지
- 문장별 실패 로그 저장

오류 누적 예시:

```json
{
  "source": "OpenAI",
  "wrong_outputs": ["오픈아이", "오페나이"],
  "preferred_reading": "오픈에이아이",
  "scope": "global",
  "created_from": "review",
  "confidence": 0.94
}
```

## 5. 핵심 데이터 포맷

### 5.1 Speech Script

한국어 엔진의 출력이자 성우 엔진의 입력이다.

```json
{
  "id": "line-0001",
  "display_text": "OpenAI API는 3.5초 안에 응답했다.",
  "speech_text": "오픈에이아이 에이피아이는 삼 점 오 초 안에 응답했다.",
  "language": "ko",
  "tokens": [
    {
      "text": "오픈에이아이",
      "source": "OpenAI",
      "type": "term",
      "emphasis": 0.2
    },
    {
      "text": "에이피아이는",
      "source": "API는",
      "type": "term_with_josa",
      "emphasis": 0.3
    },
    {
      "text": "삼 점 오 초",
      "source": "3.5초",
      "type": "number_unit",
      "emphasis": 0.4
    },
    {
      "text": "응답했다",
      "type": "predicate",
      "ending": "falling"
    }
  ],
  "phrases": [
    {
      "text": "오픈에이아이 에이피아이는",
      "pause_after_sec": 0.12
    },
    {
      "text": "삼 점 오 초 안에 응답했다.",
      "pause_after_sec": 0.35
    }
  ]
}
```

### 5.2 Voice Acting Plan

성우 엔진의 출력이다.

```json
{
  "role": "calm_narrator",
  "emotion": "neutral_confident",
  "pitch_shift": -1.0,
  "pitch_variance": 0.85,
  "speed": 0.92,
  "breathiness": 0.12,
  "articulation_strength": 0.78,
  "pause_scale": 1.1,
  "ending_style": "low_falling",
  "energy": 0.62
}
```

### 5.3 Generation Manifest

생성 결과를 추적하기 위한 파일이다.

```json
{
  "job_id": "20260427-0001",
  "input_script": "scripts/example.scene.json",
  "voice_profile": "profiles/user/default.json",
  "role": "calm_narrator",
  "output_wav": "outputs/20260427-0001.wav",
  "sample_rate": 48000,
  "review": {
    "asr_text": "오픈에이아이 에이피아이는 삼 점 오 초 안에 응답했다",
    "cer": 0.0,
    "warnings": []
  }
}
```

## 6. 데이터 수집 설계

### 6.1 사용자 본인 목소리 기본팩

최소 목표:

- 깨끗한 녹음 30분
- 같은 마이크, 같은 공간, 같은 거리 유지
- 48kHz WAV 권장
- 잡음 제거 전 원본 보관

권장 목표:

- 기본 낭독 60분
- 숫자/영어/기술용어 20분
- 감정 절제 문장 20분
- 대화체 20분
- 긴 내레이션 60분

### 6.2 한국어 어려운 문장 세트

초기 테스트 세트는 최소 300문장으로 시작한다.

범주:

- 영어 약어
- 기술 용어
- 숫자와 단위
- 날짜와 시간
- 전화번호
- 금액
- 버전명
- 외래어 뒤 조사
- 받침 발음
- 긴 문장 호흡
- 짧은 대화체
- 유튜브 내레이션체
- 다큐멘터리 해설체

예시:

```text
22B Labs는 OpenAI API를 사용해 TTS v2.1을 테스트했다.
2026년 4월 27일 오후 3시 5분에 결과가 나왔다.
010-1234-5678로 전화하지 말고, 이메일로 보내 주세요.
국립 연구소의 값이 예상보다 컸다.
읽는 사람에 따라 같은 문장도 완전히 다르게 들린다.
```

### 6.3 성우 노하우 데이터

실제 성우 목소리 무단 학습은 금지한다.

허용되는 데이터:

- 공개 강의나 교재에서 설명된 발성 원리의 텍스트 요약
- 사용자가 직접 녹음한 스타일 샘플
- 명시적으로 허락받은 자원자의 연기 샘플
- 라이선스가 확인된 공개 음성 데이터
- 사람이 직접 평가한 스타일 라벨

학습하려는 것은 특정 성우의 목소리가 아니라, 다음과 같은 일반 원리다.

- 낮은 피치와 긴 쉼이 주는 권위감
- 빠른 속도와 높은 피치가 주는 어린 느낌
- 자음 선명도가 주는 뉴스톤
- 문장 끝 하강이 주는 안정감
- 긴 호흡과 약한 에너지가 주는 회상감

## 7. 저장소 구조 초안

```text
Korean-Voice-Acting-Engine/
  README.md
  LICENSE
  docs/
    DEVELOPMENT_IMPLEMENTATION_SPEC.md
    DATASET_GUIDE.md
    SAFETY_POLICY.md
    KOREAN_READING_RULES.md
    VOICE_ACTING_PRESETS.md
  configs/
    default.yaml
    korean_rules.yaml
    voice_presets.yaml
  data/
    README.md
    pronunciation_dict.example.json
    hard_korean_sentences.example.jsonl
  src/
    kva_engine/
      korean/
        normalizer.py
        number_reader.py
        english_reader.py
        josa.py
        pronunciation.py
        prosody.py
      acting/
        presets.py
        planner.py
        parameters.py
      speech/
        acoustic_model.py
        vocoder.py
        trainer.py
        infer.py
      review/
        asr_check.py
        audio_quality.py
        correction_memory.py
      cli.py
      api.py
  scripts/
    record_voice_pack.py
    prepare_dataset.py
    train_single_speaker.py
    synthesize_scene.py
    review_outputs.py
  tests/
    test_number_reader.py
    test_english_reader.py
    test_pronunciation.py
    test_speech_script_schema.py
  outputs/
    .gitkeep
```

## 8. 개발 단계

### v0.1 한국어 엔진

목표:

- 원문을 speech_text로 안정적으로 변환한다.
- 숫자, 영어, 약어, 날짜, 전화번호, 단위 규칙을 구현한다.
- 사용자 발음 사전을 적용한다.

완료 조건:

- 어려운 한국어 문장 300개에 대해 speech_text 생성
- 규칙별 단위 테스트 작성
- display_text와 speech_text 분리 저장

### v0.2 성우 엔진

목표:

- 캐릭터 프리셋을 정의한다.
- speech_script에 연기 파라미터를 붙인다.
- 같은 문장에 여러 배역 계획을 만들 수 있게 한다.

완료 조건:

- 최소 8개 캐릭터 프리셋
- JSON 기반 voice_acting_plan 출력
- 대본 한 편에서 배역별 계획 분리

### v0.3 단일 화자 음성 생성

목표:

- 사용자의 목소리 데이터로 첫 자체 한국어 음성 모델을 학습한다.
- 짧은 문장과 긴 문장의 발음 안정성을 확인한다.

완료 조건:

- 30분 이상 녹음 데이터 학습
- 100개 테스트 문장 생성
- 잡음/클리핑/무음 검수 리포트 생성

### v0.4 성우 스타일 적용

목표:

- pitch, duration, pause, energy, breathiness를 캐릭터 프리셋에 따라 조절한다.
- 같은 음성 정체성에서 여러 배역 느낌을 만든다.

완료 조건:

- 최소 5개 배역 음성 생성
- 사용자가 A/B 비교할 수 있는 샘플 리포트
- 프리셋별 실패 사례 기록

### v0.5 자동 검수와 교정 기억

목표:

- 생성 음성을 STT로 재검수한다.
- 잘못 읽은 표현을 correction memory에 누적한다.

완료 조건:

- 생성 결과별 manifest 저장
- 발음 오류 후보 자동 제안
- 사용자 승인 후 발음 사전에 반영

### v1.0 공개 베타

목표:

- 로컬 CLI로 대본 입력, 배역 선택, 음성 생성까지 실행한다.
- 초보자도 따라 할 수 있는 한국어 README를 제공한다.

완료 조건:

- Windows 로컬 실행 가이드
- 샘플 대본과 샘플 프리셋
- 안전 정책
- 라이선스와 데이터 사용 경계 문서화

## 9. CLI 사용 목표

최종적으로 이런 사용감을 목표로 한다.

```powershell
python -m kva_engine normalize scripts\scene01.txt --out outputs\scene01.speech.json

python -m kva_engine cast outputs\scene01.speech.json `
  --voice-profile profiles\my_voice `
  --roles configs\voice_presets.yaml `
  --out outputs\scene01.cast.json

python -m kva_engine synthesize outputs\scene01.cast.json `
  --out outputs\scene01.wav

python -m kva_engine review outputs\scene01.wav `
  --script outputs\scene01.speech.json `
  --update-corrections
```

## 10. 안전 정책 초안

반드시 금지:

- 타인의 목소리를 동의 없이 학습하거나 배포
- 유명인, 성우, 가족, 지인 목소리 무단 복제
- 실제 인물을 사칭하는 음성 생성
- 정치, 금융, 법률, 의료 사칭 자동응답 제작
- 모델 파일에 출처 불명 음성 데이터를 섞어 배포

허용:

- 본인의 목소리로 만든 개인 창작용 음성
- 명시적 동의를 받은 자원자 데이터
- 가상의 캐릭터 프리셋
- 성우 발성 원리의 일반화된 파라미터화
- 로컬 우선 처리와 투명한 로그 저장

원칙:

> 성우의 목소리를 복제하지 않는다. 성우가 목소리를 바꾸는 방법을 배운다.

## 11. 품질 평가 기준

한국어 엔진 평가:

- 영어/숫자 변환 정확도
- 사용자 사전 적용률
- 조사 결합 오류율
- 발음 규칙 테스트 통과율

음성 평가:

- 발음 오독률
- STT 재인식 CER/WER
- 잡음 수준
- 클리핑 여부
- 문장별 음량 편차
- 긴 문장 안정성
- 사람이 듣는 자연스러움 MOS

성우 엔진 평가:

- 같은 목소리 정체성 유지 여부
- 배역 간 구분 가능성
- 과장/부자연스러움 발생률
- 문장 끝 억양 안정성
- 캐릭터 프리셋 재현성

## 12. 첫 구현 우선순위

가장 먼저 만들 파일:

```text
src/kva_engine/korean/number_reader.py
src/kva_engine/korean/english_reader.py
src/kva_engine/korean/normalizer.py
src/kva_engine/korean/prosody.py
src/kva_engine/acting/presets.py
data/pronunciation_dict.example.json
data/hard_korean_sentences.example.jsonl
tests/test_number_reader.py
tests/test_english_reader.py
```

첫 주 목표:

- 프로젝트 스캐폴드 생성
- 숫자/영어/약어 변환기 구현
- 발음 사전 포맷 확정
- 어려운 한국어 문장 100개 작성
- speech_script JSON 출력

둘째 주 목표:

- 문장 분할과 호흡 계획 구현
- 캐릭터 프리셋 8개 작성
- cast plan JSON 출력
- CLI 초안 작성

셋째 주 목표:

- 녹음 스크립트와 데이터 준비 도구 작성
- 단일 화자 학습 파이프라인 초안
- 오디오 품질 검사 도구 작성

## 13. 오픈소스 배포 방향

코드 라이선스 후보:

- Apache-2.0: 기업 활용과 특허 조항까지 고려할 때 안정적
- MIT: 가장 단순하고 접근성이 높음

권장:

- 코드: Apache-2.0
- 문서: CC BY 4.0
- 샘플 데이터: 직접 제작한 경우 CC BY 4.0 또는 CC0 검토
- 사용자 음성 데이터: 절대 저장소에 포함하지 않음
- 학습된 개인 모델: 사용자가 로컬에서 보관

README는 한국어를 1순위로 작성하고, 영어는 2순위로 제공한다.

## 14. 핵심 차별점

기존 TTS:

```text
텍스트를 음성으로 바꾼다.
```

KVA Engine:

```text
한국어를 먼저 성우가 읽을 수 있는 대본으로 바꾸고,
사용자의 목소리를 여러 배역으로 연기하게 만든다.
```

기존 보이스 클로닝:

```text
한 사람의 목소리를 따라 한다.
```

KVA Engine:

```text
한 사람의 목소리에서 여러 배역의 가능성을 꺼낸다.
```

## 15. 지금 결정된 방향

- 프로젝트는 `한국어 엔진`과 `성우 엔진`을 분리한다.
- 한국어 엔진이 먼저 존재하고, 성우 엔진은 그 뒤에 연결된다.
- 완성형 외부 TTS 엔진 의존을 제품 핵심으로 두지 않는다.
- 사용자의 목소리만으로 시작하되, 여러 성우성은 연기 파라미터와 스타일 어댑터로 구현한다.
- 수정은 반복 생성으로 버리지 않고 correction memory에 누적한다.
- 무료 공개 배포를 전제로 안전 정책과 데이터 라이선스를 초기부터 문서화한다.

## 16. 외부 조사 반영 기록

조사일: 2026-04-27

조사 범위:

- 공개 TTS 엔진과 레포: VibeVoice, CosyVoice, F5-TTS, Chatterbox, MeloTTS, Supertonic, VITS, StyleTTS2, Korean FastSpeech2
- 한국어 전처리와 데이터셋: g2pK, KSS, CoreaSpeech, AI-Hub 계열 데이터, KsponSpeech 관련 자료
- 국내 기업 사례: KT Voice AI, Humelo DIVE/Prosody, Kakao SSML, SELVAS, ReadSpeaker Korea, Soree
- 사용자 피드백: GitHub Issues, 커뮤니티 피드백, 번호/철자 누락, 다국어 억양 전이, 커스텀 보이스 요구

핵심 결론:

1. 한국어 문제는 모델 크기만으로 해결되지 않는다.
2. 숫자, 영어, 약어, 특수기호, 조사, 받침, 연음, 호흡을 처리하는 `Korean Text Frontend`가 제품 품질을 좌우한다.
3. 커스텀 보이스와 성우 스타일은 같은 문제가 아니다. 커스텀 보이스는 "누구의 음색인가"이고, 성우 스타일은 "어떻게 연기하는가"이다.
4. 장문/다화자 음성 생성은 단순 문장 concat으로는 자연스러운 turn-taking과 speaker consistency를 유지하기 어렵다.
5. 무료 공개 배포 프로젝트일수록 consent, watermark, disclosure, abuse prevention을 초기 구조에 넣어야 한다.

## 17. 공개 엔진과 논문에서 반영할 점

### 17.1 VibeVoice 검토

출처:

- GitHub: https://github.com/microsoft/VibeVoice
- Technical report: https://arxiv.org/abs/2508.19205
- ICLR 2026 paper: https://openreview.net/pdf?id=FihSkzyxdv
- Realtime docs: https://github.com/microsoft/VibeVoice/blob/main/docs/vibevoice-realtime-0.5b.md

VibeVoice의 장점:

- 장문 대화형 음성에 초점을 맞춘다.
- 최대 90분, 최대 4화자 long-form conversational speech를 목표로 한다.
- acoustic tokenizer와 semantic tokenizer를 분리해 장문에서 화자 일관성과 의미 흐름을 유지하려 한다.
- ultra-low frame rate 7.5 Hz speech representation을 사용해 긴 시퀀스 처리 비용을 낮춘다.
- podcast 데이터에서 pseudo transcription과 speaker turn label을 만드는 data preparation pipeline을 중시한다.
- 평가에서 WER, speaker similarity, realism, richness, preference를 함께 본다.

VibeVoice의 한계와 주의:

- VibeVoice-TTS 코드는 misuse 우려로 저장소에서 제거된 이력이 있다.
- Realtime 0.5B 문서는 영어 중심이며, 한국어 등 다른 언어는 탐색용이고 예측 불가능할 수 있다고 경고한다.
- Realtime 모델은 단일 화자 중심이며, voice customization은 제한되어 있다.
- GitHub Issue에는 "일부 단어가 생략되거나 다르게 읽힌다", "own voices를 어떻게 추가하느냐", "새 언어 학습 스크립트가 있느냐" 같은 피드백이 있다.
- 따라서 우리 프로젝트는 VibeVoice를 제품 의존성으로 삼지 않고, long-form multi-speaker architecture reference로만 사용한다.

우리 문서에 반영할 결정:

- `LongForm Dialogue Track`을 별도 개발 트랙으로 둔다.
- 장문을 단순히 문장별로 합친 뒤 이어붙이는 방식을 기본으로 삼지 않는다.
- 대본에는 speaker turn, emotion carryover, previous acoustic context, scene context를 명시한다.
- acoustic representation과 semantic/prosody representation을 분리하는 구조를 장기 연구 항목으로 둔다.
- VibeVoice식 평가에서 배울 점을 반영해 `Realism`, `Richness`, `Preference`, `Speaker Consistency`, `Korean Reading Accuracy`를 모두 품질 지표에 넣는다.

추가 데이터 포맷:

```json
{
  "scene_id": "scene-001",
  "turns": [
    {
      "speaker": "narrator",
      "display_text": "처음에는 모든 것이 조용했다.",
      "speech_text": "처음에는 모든 것이 조용했다.",
      "emotion": "low_tension",
      "previous_context": null,
      "turn_pause_sec": 0.45
    },
    {
      "speaker": "childlike_fast",
      "display_text": "근데 저 소리는 뭐예요?",
      "speech_text": "근데 저 소리는 뭐예요?",
      "emotion": "curious_anxious",
      "previous_context": "narrator_low_tension",
      "turn_pause_sec": 0.18
    }
  ]
}
```

### 17.2 g2pK와 한국어 전처리

출처:

- https://github.com/Kyubyong/g2pK

g2pK는 영어 단어의 한글 변환, 문맥 기반 숫자 읽기, 자모 출력, 구어적 모음 통합 옵션을 제공한다. 또한 규칙만으로 모든 예외를 덮을 수 없으므로 idiom/special dictionary가 필요하다는 점을 명시한다.

우리 문서에 반영할 결정:

- `Korean Engine`은 반드시 세 가지 출력을 만든다.
  - `speech_text`: 사람이 검수할 수 있는 읽기용 한글 문장
  - `phoneme_text`: 발음 규칙이 적용된 음소/자모 표현
  - `normalization_trace`: 어떤 규칙이 왜 적용되었는지 추적하는 로그
- 사용자 발음 사전은 기본 규칙보다 우선한다.
- 규칙 기반 변환과 correction memory를 결합한다.
- 한국어 어려운 문장 세트는 숫자/영어/외래어/조사/받침 유형별로 태그를 붙여야 한다.

추가 출력 예:

```json
{
  "display_text": "지금 시각은 12시 12분입니다.",
  "speech_text": "지금 시각은 열두 시 십이 분입니다.",
  "phoneme_text": "지금 시가근 열두 시 시비 부님니다.",
  "normalization_trace": [
    {
      "source": "12시",
      "rule": "hour_native_korean",
      "output": "열두 시"
    },
    {
      "source": "12분",
      "rule": "minute_sino_korean",
      "output": "십이 분"
    }
  ]
}
```

### 17.3 CoreaSpeech와 한국어 데이터 설계

출처:

- https://openreview.net/forum?id=8nHq0IIwpd
- https://coreaspeech.github.io/demo/

CoreaSpeech는 한국어 TTS가 영어/중국어 대비 부족한 이유로 rigorous preprocessing, systematically constructed datasets, standardized Korean TTS benchmarks, Korean-optimized models 부족을 지적한다. 또한 숫자와 영어 용어 정규화, 자모 기반 coreset selection, numeric subset benchmark를 강조한다.

우리 문서에 반영할 결정:

- 데이터셋은 "많이 모으기"보다 "한국어 난점이 균형 있게 포함되도록 고르기"가 우선이다.
- `hard_korean_sentences`에는 jamo coverage, final consonant coverage, number pattern coverage, English-mixed pattern coverage를 기록한다.
- 학습 데이터뿐 아니라 benchmark set을 별도로 둔다.
- 숫자와 영어가 들어간 numeric/mixed subset은 반드시 독립 평가한다.

추가 데이터 태그:

```json
{
  "id": "hard-ko-0001",
  "text": "22B Labs는 OpenAI API를 사용해 TTS v2.1을 테스트했다.",
  "tags": [
    "english_brand",
    "english_acronym",
    "version_number",
    "josa_after_english",
    "technical_narration"
  ],
  "expected_speech_text": "이십이비 랩스는 오픈에이아이 에이피아이를 사용해 티티에스 버전 이 점 일을 테스트했다."
}
```

### 17.4 Korean FastSpeech2, VITS, StyleTTS2

출처:

- Korean FastSpeech2: https://github.com/HGU-DLLAB/Korean-FastSpeech2-Pytorch
- VITS: https://github.com/jaywalnut310/vits
- StyleTTS2: https://github.com/yl4579/StyleTTS2

반영할 점:

- Korean FastSpeech2는 한국어에서도 duration alignment가 중요하다는 점을 보여준다. MFA 기반 duration 추출 또는 대체 alignment 방법이 필요하다.
- VITS는 stochastic duration predictor를 통해 같은 텍스트가 여러 리듬으로 말해질 수 있음을 모델링한다. 성우 엔진의 다양한 연기 리듬과 잘 맞는다.
- StyleTTS2는 style을 latent variable로 보고 diffusion으로 적합한 style을 생성한다. 성우 엔진은 단순 pitch/speed 조절을 넘어 style embedding을 장기 목표로 삼아야 한다.

우리 문서에 반영할 결정:

- v0.3 단일 화자 모델은 FastSpeech2/VITS 계열을 baseline으로 비교한다.
- v0.4 성우 스타일 적용에서는 pitch, duration, energy를 수동 조절하는 baseline과 style embedding 기반 모델을 분리한다.
- v1.0 이후에는 `style_encoder`, `role_embedding`, `prosody_predictor`를 별도 모듈로 둔다.

### 17.5 CosyVoice, Chatterbox, F5-TTS, MeloTTS, Supertonic

출처:

- CosyVoice: https://github.com/FunAudioLLM/CosyVoice
- Chatterbox: https://github.com/resemble-ai/chatterbox
- F5-TTS: https://github.com/SWivid/F5-TTS
- MeloTTS: https://github.com/myshell-ai/MeloTTS
- Supertonic: https://github.com/supertone-inc/supertonic

반영할 점:

- CosyVoice는 한국어 포함 다국어 zero-shot, text normalization, pronunciation inpainting, streaming, instruction control을 강조한다. 다만 한국어 전용 안정성은 별도 검증이 필요하다.
- Chatterbox는 paralinguistic tag, reference clip language mismatch에 따른 accent transfer, CFG/exaggeration tuning, PerTh watermarking을 참고할 만하다.
- F5-TTS 사용자 이슈에서는 spelling/number 누락, 너무 빠른 철자 읽기, 출력 일관성 문제가 보고되었다. 이는 우리 `Korean Engine`이 영어/숫자/철자를 한글 낭독 텍스트로 확정한 뒤 모델에 넘겨야 함을 뒷받침한다.
- F5-TTS cross-lingual issue에서는 reference language와 target language가 다를 때 accent transfer가 발생한다. 우리 시스템은 한국어 출력에는 한국어 reference prompt를 우선하도록 강제한다.
- MeloTTS는 Korean 지원과 CPU real-time inference를 제공한다. 가벼운 baseline과 온디바이스 목표를 잡을 때 참고한다.
- Supertonic은 ONNX 기반 on-device TTS와 Korean support, voice builder를 공개적으로 내세운다. 우리도 `local-first`, `edge-friendly`, `ONNX export`를 장기 배포 목표에 넣는다.

우리 문서에 반영할 결정:

- `reference_voice_policy`를 추가한다.
- 한국어 출력에는 한국어 reference clip을 기본으로 요구한다.
- 외국어 reference clip으로 한국어를 만들 경우 `accent_risk: high` 경고를 띄운다.
- number/spelling/short input/long input은 별도 회귀 테스트로 관리한다.
- 공개 배포 음성에는 watermark 또는 disclosure metadata 삽입을 기본값으로 둔다.

## 18. 국내 기업과 서비스에서 반영할 점

### 18.1 KT Voice AI

출처:

- https://ai.kt.com/resources/detail03

KT는 TTS에서 Transformer 기반 End-to-End 구조, 자연스러운 억양과 감정 표현, 숫자·기호·약어 자동 변환 Text Normalization을 강조한다. 또한 ASR과 화자인식까지 자체 기술로 확보하고, 딥보이스 탐지까지 언급한다.

우리 문서에 반영할 결정:

- TTS만 보지 말고 ASR review와 speaker verification/detection을 함께 설계한다.
- `Text Normalization`은 보조 기능이 아니라 핵심 엔진으로 둔다.
- 보이스피싱/사칭 방지 관점에서 generated audio disclosure와 detection hook을 설계한다.

### 18.2 Humelo DIVE/Prosody

출처:

- https://humelo.com/
- https://humelo.com/insights/korean-tts-api-comparison-2026
- https://console.humelo.com/docs

Humelo는 한국어 음운 규칙, 조사·어미에 따른 억양 변화, 존댓말/반말 톤 차이, 단어장, 감정 표현, 스트리밍, 보이스 클로닝을 강조한다. 고객 피드백에서는 문맥에 맞춘 톤, 템포, 쉼표가 자연스럽고 낭독체 느낌이 줄었다는 점이 중요하다.

우리 문서에 반영할 결정:

- 성우 엔진은 감정 이름만 받지 않고 `tone`, `tempo`, `pause`, `formality`를 분리한다.
- 존댓말/반말 변환을 함부로 자동 수행하지 않고, `formality`는 대본 의도와 분리해서 관리한다.
- 단어장은 `global`, `project`, `voice_profile`, `scene` 범위로 나눈다.

### 18.3 Kakao SSML

출처:

- https://developers.kakao.com/assets/guide/kakao_ssml_guide.pdf

Kakao SSML은 `voice`, `prosody`, `break`, `say-as`, `sub`를 제공한다. 특히 `spell-out`, `digits`, `telephone`, `date`, `time`, `kakao:number`, `kakao:vocative`, `sub alias`는 우리가 설계 중인 한국어 낭독 스크립트와 직접 연결된다.

우리 문서에 반영할 결정:

- 내부 `speech_script`는 SSML 호환성을 염두에 둔다.
- `say_as`와 `substitution`을 별도 필드로 둔다.
- 쉼은 단어 내부가 아니라 문장/절 경계에서만 넣는 것을 기본값으로 한다.
- `break`는 150ms~1500ms 범위의 가드레일을 둔다.

추가 필드:

```json
{
  "text": "010-1234-5678",
  "say_as": "telephone",
  "speech_text": "공일공 일이삼사 오육칠팔"
}
```

### 18.4 SELVAS, ReadSpeaker Korea, Soree

출처:

- SELVAS: https://www.selvasai.com/tts
- ReadSpeaker Korea: https://www.readspeaker.co.kr/assets/files/%EB%A6%AC%EB%93%9C%EC%8A%A4%ED%94%BC%EC%BB%A4%EC%BD%94%EB%A6%AC%EC%95%84_TTS_%EC%8B%A0%EC%86%8C%EA%B0%9C%EC%9E%90%EB%A3%8C_2024v2.0.pdf
- Soree: https://getsoree.com/

반영할 점:

- 전통 엔터프라이즈 TTS는 효율, 채널 수, 안정성, 사전 기능을 중시한다.
- Soree처럼 작은 서비스도 `JSON -> 제이슨`, `API -> 에이피아이`, 숫자 변환, 개인 발음 사전을 명확한 제품 기능으로 내세운다.
- 이는 한국어 TTS에서 전처리가 사용자 가치로 직접 체감된다는 증거다.

우리 문서에 반영할 결정:

- v0.1부터 CLI 출력뿐 아니라 "변환 전/후 비교 리포트"를 제공한다.
- 발음 사전 UI/API는 나중 일이 아니라 핵심 기능으로 본다.
- 고품질 모델이 늦어져도 한국어 전처리 엔진은 독립 오픈소스 패키지로 배포 가능해야 한다.

## 19. 예상 문제점과 대책

### 19.1 한국어 숫자/영어 변환이 끝없이 예외를 만든다

문제:

- 숫자는 시간, 날짜, 금액, 전화번호, 버전, 비율, 점수, 단위에 따라 읽는 법이 다르다.
- 영어 약어는 알파벳 읽기, 외래어 읽기, 브랜드 고유 읽기가 섞인다.

대책:

- 규칙 기반 변환기를 먼저 만들고, 모든 변환에 `normalization_trace`를 남긴다.
- 사용자 발음 사전을 기본 규칙보다 우선한다.
- `unknown_token_policy`를 둬 모르는 토큰은 그대로 합성하지 않고 검수 후보로 보낸다.
- numeric/mixed benchmark를 별도 운영한다.

완료 기준:

- hard Korean benchmark 1,000문장 중 speech_text 정확도 98% 이상
- 숫자/영어 혼합 문장 300개 중 high-risk token 미검출률 1% 이하

### 19.2 cross-lingual accent transfer

문제:

- 영어 reference voice로 한국어를 만들면 영어 억양이 한국어에 묻는다.
- 다국어 모델은 언어 태그가 있어도 실제 출력이 target language를 완전히 따르지 않을 수 있다.

대책:

- 한국어 출력에는 한국어 reference clip을 기본 요구한다.
- reference clip 언어, transcript 언어, target 언어를 manifest에 기록한다.
- mismatch가 있으면 `accent_risk`를 표시하고 사용자가 승인해야 진행한다.
- 초기 모델 학습 데이터는 한국어만으로 안정화한 뒤 다국어를 확장한다.

완료 기준:

- 한국어 reference 사용 시 외국어 억양 주관 평가 2/5 이하
- mismatch warning 누락 0건

### 19.3 내 목소리 하나로 여러 성우를 만들 때 정체성과 다양성이 충돌한다

문제:

- 내 목소리 정체성을 너무 유지하면 모든 캐릭터가 비슷하다.
- 캐릭터성을 강하게 주면 내 목소리 느낌이 사라진다.

대책:

- `identity_strength`와 `role_strength`를 별도 파라미터로 둔다.
- 캐릭터 프리셋마다 허용 가능한 voice drift 범위를 정의한다.
- speaker similarity만 보지 않고 role separability를 함께 평가한다.

추가 평가:

```text
Identity Similarity: 내 목소리로 들리는가
Role Separability: 배역 간 차이가 충분한가
Natural Acting: 과장 없이 연기처럼 들리는가
```

### 19.4 장문 생성에서 말투와 화자 일관성이 무너진다

문제:

- 긴 대본은 중간부터 속도, 음색, 감정, 쉼표가 흔들린다.
- 문장별 합성 후 concat하면 대화의 흐름과 turn-taking이 어색하다.

대책:

- scene 단위 context를 유지한다.
- speaker별 acoustic memory 또는 style state를 둔다.
- VibeVoice에서 배운 것처럼 speaker turn label과 previous context를 데이터 포맷에 넣는다.
- 긴 대본은 문장별 생성과 scene-level re-render를 모두 지원한다.

완료 기준:

- 10분 대본에서 같은 speaker의 identity drift를 사람이 명확히 느끼는 비율 10% 이하
- turn boundary awkwardness 평가 평균 3.5/5 이상

### 19.5 짧은 입력과 특수기호가 모델을 불안정하게 만든다

문제:

- VibeVoice Realtime 문서도 very short input, code, math, uncommon symbols에서 불안정성을 경고한다.
- F5-TTS 이슈에서도 spelling/number 누락과 빠른 철자 읽기가 보고되었다.

대책:

- 3어절 이하 입력은 앞뒤 context를 붙이거나 안정화 prompt를 추가한다.
- code/math/symbol은 TTS 입력 전 반드시 한국어 설명문으로 변환한다.
- spelling은 글자 사이 pause와 rate를 강제한다.

예:

```json
{
  "source": "M.A.R.I.A.",
  "speech_text": "엠, 에이, 알, 아이, 에이",
  "letter_pause_ms": 180,
  "rate": 0.85
}
```

### 19.6 학습 데이터 라이선스와 배포 위험

문제:

- 공개 데이터셋은 연구용, 비상업, 재배포 금지 등 제약이 섞여 있다.
- 사용자 음성은 생체 정보에 가까우며, 모델 파일 자체가 민감 자산이 될 수 있다.

대책:

- `dataset_manifest.json`에 출처, 라이선스, 동의 범위, 배포 가능 여부를 기록한다.
- 사용자 원본 음성과 개인 모델은 저장소에 절대 포함하지 않는다.
- 공개 베타에는 직접 제작한 샘플 또는 명시적으로 허가된 데이터만 포함한다.
- 데이터셋별 `allowed_use`를 코드에서 검사한다.

### 19.7 오픈소스 악용과 사칭

문제:

- 무료 공개 배포는 접근성을 높이지만, 동시에 음성 사칭과 사기 위험을 높인다.
- 생성 음성이 자연스러워질수록 악용 가능성도 커진다.

대책:

- 기본 출력에 metadata disclosure를 넣는다.
- 가능하면 inaudible watermark 또는 audible disclosure 옵션을 제공한다.
- 제3자 voice profile 생성에는 consent file을 요구한다.
- 유명인/실존 인물 이름 프리셋을 금지한다.
- `SAFETY_POLICY.md`에 금지 사용 사례를 명확히 적는다.

추가 manifest:

```json
{
  "voice_owner": "self",
  "consent": {
    "type": "self_recorded",
    "recorded_at": "2026-04-27",
    "redistribution_allowed": false
  },
  "disclosure": {
    "ai_generated": true,
    "watermark": "planned",
    "metadata_tag": true
  }
}
```

### 19.8 CPU/로컬 환경에서 학습과 추론이 너무 무겁다

문제:

- 고품질 TTS 학습은 GPU 의존도가 높다.
- 로컬 사용자에게 너무 무거우면 무료 공개 프로젝트가 실제로 쓰이지 않는다.

대책:

- v0.1~v0.2는 모델 학습 없이 동작하는 한국어/성우 planning 패키지로 만든다.
- v0.3 학습은 GPU 권장, CPU는 데이터 검증과 짧은 inference만 지원한다.
- ONNX export와 quantization은 v1.0 이후 목표로 둔다.
- Supertonic처럼 on-device 지향 구조를 장기 배포 목표에 넣는다.

## 20. 보정된 개발 우선순위

기존 우선순위는 "한국어 엔진 -> 성우 엔진 -> 음성 생성"이었다. 외부 조사를 반영한 뒤 우선순위는 더 세밀해진다.

### Phase 0: Research & Benchmark Ground

목표:

- 한국어 난점 벤치마크 1,000문장 구축
- 숫자/영어/기호/조사/받침/긴 문장/짧은 대화체 태그 설계
- 공개 데이터셋 라이선스 매트릭스 작성
- 안전 정책 초안 작성

산출물:

```text
docs/RESEARCH_REVIEW.md
docs/DATASET_LICENSE_MATRIX.md
docs/SAFETY_POLICY.md
data/hard_korean_sentences.example.jsonl
data/pronunciation_dict.example.json
```

### Phase 1: Korean Engine MVP

목표:

- display_text -> speech_text -> phoneme_text 변환
- normalization_trace 생성
- 사용자 사전 우선 적용
- SSML 호환 필드 설계

필수 테스트:

- number_reader
- english_reader
- symbol_reader
- date_time_reader
- telephone_reader
- josa_after_english
- g2p_adapter

### Phase 2: Voice Acting Planner MVP

목표:

- 캐릭터 프리셋 8개
- `identity_strength`, `role_strength`, `emotion_pressure`, `formality`, `pause_style` 분리
- scene/turn 기반 대본 포맷 지원

필수 테스트:

- 같은 문장에 여러 role plan 생성
- 긴 대본 turn boundary 유지
- 짧은 입력 안정화

### Phase 3: Baseline Neural Engine

목표:

- 단일 화자 한국어 모델 baseline
- FastSpeech2/VITS 계열 비교
- 최소 30분, 권장 3시간 사용자 음성 데이터 파이프라인
- alignment, duration, pitch, energy 추출

성공 기준:

- 짧은 문장 100개 생성
- mixed Korean benchmark에서 ASR CER 측정
- 잡음/클리핑/무음 검사 통과

### Phase 4: Style & Casting Adapter

목표:

- role embedding 실험
- style encoder 실험
- pitch/duration/energy 수동 control baseline
- 캐릭터별 voice drift와 role separability 측정

성공 기준:

- 최소 5개 배역 샘플 생성
- 같은 voice owner 기반임을 유지하면서 배역 차이가 들릴 것
- 과장된 가짜 연기 느낌을 줄이는 프리셋 조정 루프

### Phase 5: Review, Memory, Safety

목표:

- 생성 음성 ASR 검수
- pronunciation correction memory 업데이트
- metadata disclosure와 watermark hook
- consent manifest 검사

성공 기준:

- 한 번 고친 용어가 다음 합성에서 자동 반영
- voice profile 생성 시 consent manifest 없으면 실패
- 공개 샘플에 AI-generated metadata 포함

## 21. 구현서 보정 후 핵심 결정

- VibeVoice는 장문/다화자/turn-taking 연구 레퍼런스로 삼되, 한국어 제품 의존성으로 두지 않는다.
- 한국어 엔진은 `speech_text`만 만들지 않고 `phoneme_text`와 `normalization_trace`를 함께 만든다.
- 성우 엔진은 pitch/speed 조절기가 아니라 role, emotion, formality, pause, articulation, identity strength를 분리한 planner로 만든다.
- 데이터 전략은 양보다 한국어 난점 coverage를 우선한다.
- benchmark set은 학습 데이터와 분리한다.
- safety는 README 마지막에 붙이는 주의문이 아니라 코드와 manifest에 들어가는 기능이다.
- 무료 공개 배포의 첫 가치는 거대 모델이 아니라, 누구나 고칠 수 있는 한국어 낭독 엔진이다.

마지막 문장:

> 한국어를 먼저 숨 쉬게 하고, 그 숨 위에 배역을 입힌다.
