# 전문 성우 제품 벤치마크 계획

[English document](PRO_VOICE_BENCHMARK_PLAN.md)

작성일: 2026-04-27  
최신 확인: 2026-04-28

## 결론

KVAE가 지향해야 할 방향은 단순 TTS가 아니라 다음 3개 축을 가진 성우 엔진입니다.

1. Text-to-Speech: 대본을 입력하면 자연스러운 한국어 음성 생성
2. Speech-to-Speech: 사용자가 직접 연기한 음성의 호흡과 감정을 유지하며 다른 목소리로 변환
3. Character Voice Design: 늑대, 괴물, 공룡, 어린이, 악역, 내레이터, 선생님 같은 캐릭터 보이스를 설계하고 저장

짧은 private 음성 프로필은 로컬 경로를 증명할 수 있지만 전문 품질 학습에는 짧습니다. 프로덕션 품질에는 더 많은 깨끗한 녹음이 필요합니다.

## 2026-04-28 공식 자료 확인

- ElevenLabs Professional Voice Clone 공식 문서는 최소 30분, 최적 2-3시간에 가까운 고품질 음성을 권장합니다. 또한 사용할 언어와 같은 언어의 샘플을 넣고, 스타일을 섞지 말라고 안내합니다.
- Supertone Shift는 실시간 보이스 체인저를 전면에 둡니다. KVAE의 `convert` 방향은 이 UX와 맞닿아 있습니다.
- Humelo DIVE/Prosody는 한국어 기업용 보이스클로닝과 TTS API 축을 가집니다. KVAE는 한국어 발음 사전, SSML, API/CLI, 품질 검증 리포트를 기본 기능으로 가져가야 합니다.
- NAVER CLOVA Dubbing은 영상/더빙 워크플로를 제품 축으로 둡니다. KVAE의 다음 앱 계층은 WAV만 만드는 도구가 아니라 쇼츠/영상 편집과 이어져야 합니다.

참고 링크:

- https://elevenlabs.io/docs/product-guides/voices/voice-cloning/professional-voice-cloning
- https://www.supertone.ai/ko/shift
- https://humelo.com/dive
- https://console.humelo.com/
- https://help.naver.com/service/23823?lang=en

## 필요한 학습 데이터

### 기본 본인 목소리

- 최소: 10분
- 실용적 전문 최소: 30분
- 권장 목표: 60-120분
- 형식: 깨끗한 mono WAV, 44.1kHz 또는 48kHz
- 조건: 같은 사람, 같은 마이크, 같은 공간, 안정된 거리, 낮은 잡음

### 한국어 발음 커버리지

- 숫자, 날짜, 시간, 전화번호, 금액, 퍼센트
- 영어 약어: AI, API, TTS, JSON, GPT, LoRA, KVAE
- 된소리, 거센소리, 받침, 연음, 비음화가 많은 문장
- 존댓말, 반말, 뉴스체, 설명체, 이야기체
- 짧은 문장과 긴 문장

### 역할별 연기 데이터

각 역할마다 최소 20문장, 권장 50문장 이상:

- calm_narrator
- documentary
- news_anchor
- bright_teacher
- old_storyteller
- villain_low
- wolf_growl
- monster_deep
- dinosaur_giant
- child_bright

### Speech-to-Speech 기준 데이터

같은 문장을 여러 연기로 직접 읽은 데이터가 필요합니다.

- 보통 성우톤
- 속삭임
- 화남
- 웃음 섞인 말
- 무서운 말
- 괴물처럼 거칠게 말하기
- 어린아이처럼 빠르고 높게 말하기

이 데이터는 목소리만 바꾸고 원본 연기의 pacing, pause, inflection을 보존하는 데 필요합니다.

## 구현 우선순위

### Phase A: 학습 데이터 확장

- 30분 녹음 스크립트
- 녹음 검수 CLI
- 자동 silence split
- Whisper 전사 및 사람 검수 파일 생성
- train/val/test 분리

### Phase B: Speech-to-Speech 변환 명령

```powershell
python -m kva_engine convert --input my_acting.wav --role wolf_growl --out wolf.wav
```

보스가 한 번 연기한 WAV를 여러 target voice로 변환하는 것이 중심 기능입니다.

### Phase C: 캐릭터 보이스 프리셋 정교화

- `wolf_growl_clear`와 `wolf_growl_heavy`
- `monster_deep_clear`와 `monster_deep_fx`
- `dinosaur_giant_clear`와 `dinosaur_giant_roar`
- 어린이 목소리는 pitch만 올리지 말고 발음, 속도, 문장 길이까지 제어

### Phase D: 전문 성우 샘플 평가

매 샘플마다 다음을 기록합니다.

- 원문
- ASR 전사문
- WER/CER
- 음량
- clipping 여부
- 말 명료도
- 캐릭터성
- 본인 목소리 보존감

## 제품 정의

KVAE의 최종 제품 정의:

> 사용자가 직접 읽은 한국어 연기를 입력하면, 그 연기의 호흡과 감정은 살리고 목소리 정체성만 다양한 성우/캐릭터로 바꾸는 로컬 우선 성우 엔진.
