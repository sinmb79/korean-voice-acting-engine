# 개발 로드맵

[English document](DEVELOPMENT_ROADMAP.md)

이 문서는 KVAE가 어디까지 됐고, 아직 무엇이 남았는지 솔직하게 보고하기 위해 둡니다.

## 현재 완료 상태

완료:

- 숫자, 영어, 기호, 날짜, 시간, 전화번호, 조사, 발음 trace를 포함한 한국어 정규화
- SSML 및 manifest 생성
- private local voice와 public AI voice profile 해석
- 출처, 라이선스, 표기문, AI 음성 고지를 포함한 공개 한국어 AI 음성 카탈로그
- `kva convert` 기반 녹음 음성 변환
- `kva voice-lab` 기반 다중 캐릭터 후보 생성
- `default`, `dialogue`, `creature`, `narration`, `shorts` Voice Lab role group
- `kva review-audio` 기반 오디오 리뷰
- `kva recording-check` 기반 원본 녹음 점검
- `kva doctor` 기반 런타임/안전 설정 점검
- 릴리스 품질 게이트와 GitHub Actions CI

짧게 말하면, KVAE는 현재 로컬 CLI 엔진, 안전 메타데이터, 리뷰 리포트, CI까지 갖춘 상태입니다.

## 남은 개발 과정

### Phase 1. Voice Lab 제품형 워크플로

상태: 진행 중, v1 사용 가능.

목표:

- 입력 녹음 하나로 여러 캐릭터 목소리 후보 생성
- WAV, manifest, review JSON, playlist, summary 자동 저장
- 나중에 deterministic 변환을 neural speech-to-speech로 교체해도 계약 유지

다음 보강:

- 역할별 명료도 기준
- 후보 비교 리포트
- 사람 청취 리뷰용 listening score 필드

### Phase 2. 공개 음성 설치 및 렌더 어댑터

상태: 메타데이터 카탈로그 구현 완료, 실제 설치/렌더 어댑터는 남음.

목표:

- 사용자가 승인한 공개 한국어 AI 음성을 명시적으로 설치
- 외부 모델 다운로드 전 라이선스 확인 요구
- 모든 manifest에 출처, 라이선스, 표기문, AI 음성 고지 포함

필요:

- `public-voices install-plan`
- MMS, Piper, Coqui 등 provider adapter
- 사용자가 선택한 로컬 폴더 아래 offline cache 구조

### Phase 3. Neural Speech-to-Speech 백엔드

상태: CLI 계약은 준비, neural backend는 미완성.

목표:

- 사용자의 연기 타이밍, 쉼, 감정 보존
- 목소리 정체성만 선택한 캐릭터로 변환
- 단순 pitch/EQ 변환보다 자연스러운 결과

필요:

- RVC/FreeVC/so-vits-svc/KVAE-STS backend interface
- 로컬 모델 registry
- train/evaluation split
- 객관 리뷰와 사람 청취 리뷰 병행

### Phase 4. 한국어 연기 데이터셋 확장

상태: recording-check와 benchmark plan 존재, 대형 데이터셋은 남음.

목표:

- 화자별 30-120분의 깨끗한 한국어 녹음
- 역할별 연기 데이터 포함
- 숫자, 날짜, 영어 약어, 문장 끝, 조사, 어려운 발음 커버

필요:

- 녹음 세션 생성기
- silence/segment splitter
- 전사문 교정 워크플로
- train/validation/test 분리

### Phase 5. 로컬 앱 UI

상태: CLI만 존재.

목표:

- 비개발자도 사용 가능
- WAV를 끌어넣고
- 역할을 선택하고
- 들어보고 비교하고 export
- 출처/라이선스/AI 음성 고지 명확히 표시

필요:

- 로컬 데스크톱 또는 웹 UI
- waveform preview
- role preset editor
- review dashboard

### Phase 6. 릴리스 패키징

상태: wheel build smoke 통과, 정식 릴리스 자동화는 남음.

목표:

- 깨끗하게 설치
- `kva doctor` 실행
- CI 통과
- 영어 기본 문서와 선택 한국어 문서 제공

필요:

- release checklist 자동화
- 서명된 release artifact
- versioned changelog
- private 음성이 없는 beginner example

## 완료의 정의

KVAE는 사용자가 다음을 할 수 있어야 “완료”에 가까워집니다.

1. 설치한다.
2. `kva doctor`를 실행한다.
3. private 또는 public 한국어 음성 profile을 선택한다.
4. 한국어 텍스트 또는 녹음 연기를 입력한다.
5. 여러 목소리 후보를 생성한다.
6. review report를 확인한다.
7. 출처/라이선스/AI 음성 고지를 확인한다.
8. private 음성 데이터를 public repo 밖에 둔다.
9. 자기 취향에 맞게 역할과 품질 기준을 수정한다.
