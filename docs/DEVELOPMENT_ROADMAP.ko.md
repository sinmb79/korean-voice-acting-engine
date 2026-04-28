# 개발 로드맵

[English document](DEVELOPMENT_ROADMAP.md)

이 문서는 KVAE가 어디까지 구현되었고 무엇이 아직 남아 있는지 숨기지 않고 보고하기 위한 로드맵입니다.

## 현재 완료 상태

완료:

- 숫자, 영어, 기호, 날짜, 시간, 전화번호, 조사, 발음 trace를 포함한 한국어 정규화
- SSML과 생성 manifest 출력
- private local voice와 public AI voice profile 해석
- 출처, 라이선스, 표기문, AI 음성 고지를 포함한 공개 한국어 AI 음성 카탈로그
- `kva public-voices --install-plan` 기반 라이선스 안전 공개 음성 설치 계획
- `kva convert` 기반 녹음 음성 변환
- `kva voice-lab` 기반 여러 캐릭터 후보 생성
- `kva vocal-tract` 기반 source-filter 성도 음성 설계
- `kva benchmarks` 기반 전문 음성 제품 벤치마크
- `kva benchmarks` 기반 대형 제작사식 성우/음향 제작기법 카탈로그
- `kva source-library` 기반 라이선스 안전 소스 라이브러리 스키마
- `kva creature-design` 기반 크리처 사운드 디자인 레시피
- 원본 화자의 말소리 정체성을 제거하는 비인간 bioacoustic 공룡 렌더링
- `default`, `dialogue`, `creature`, `narration`, `shorts` Voice Lab role group
- `kva review-audio` 기반 오디오 리뷰
- `kva recording-check` 기반 원본 녹음 점검
- `kva split-recording` 기반 긴 녹음 세그먼트 분할
- `kva recording-plan` 기반 한국어 녹음 세션 대본 생성
- `kva transcript-review` 기반 TSV 전사문 교정 워크플로
- `kva dataset-split` 기반 deterministic train/validation/test split manifest
- `kva doctor` 기반 런타임과 안전 설정 점검
- release quality gate와 GitHub Actions CI

짧게 말하면, KVAE는 현재 로컬 CLI 엔진, 안전 메타데이터, 리뷰 리포트, 벤치마크 카탈로그, CI를 갖춘 상태입니다.

## 남은 개발 과정

### Phase 1. Voice Lab 제품 워크플로

상태: 진행 중, v1 사용 가능.

목표:

- 입력 녹음 하나로 여러 캐릭터 음성 후보 생성
- WAV, manifest, review JSON, playlist, summary 자동 저장
- 나중에 deterministic 변환을 neural speech-to-speech로 교체해도 계약 유지

다음 보강:

- 역할별 명료도 기준
- 후보 비교 리포트
- 사람 청취 리뷰와 listening score 필드

### Phase 2. 공개 음성 설치와 렌더 어댑터

상태: 메타데이터 카탈로그와 설치 계획은 구현됨. 실제 렌더 어댑터는 남아 있음.

목표:

- 사용자가 명시적으로 승인한 공개 한국어 AI 음성을 설치
- 외부 모델 다운로드 전 라이선스 확인 요구
- 모든 manifest에 출처, 라이선스, 표기, AI 음성 고지 포함

필요:

- MMS, Piper, Coqui 등 provider adapter
- 사용자가 선택한 로컬 폴더 아래 offline cache 구조

### Phase 3. Neural Speech-To-Speech Backend

상태: CLI 계약은 준비됨. neural backend는 미완성.

목표:

- 사용자의 연기 타이밍, 쉼, 감정 보존
- 목소리 정체성만 선택한 캐릭터로 변환
- 단순 pitch/EQ 변환보다 자연스러운 결과
- vocal-tract design 계약을 source/filter 제어와 neural rendering에 재사용
- 성우가 증명하는 인간 음성의 가변성을 source, filter, articulation, performance 제어 구조로 모델링
- 사람이 말하는 캐릭터 변환과 완전한 비인간 bioacoustic rendering 분리

필요:

- RVC/FreeVC/so-vits-svc/KVAE-STS backend interface
- F0, spectral envelope, aperiodicity를 다루는 WORLD/pyworld analysis-synthesis adapter
- 로컬 모델 registry
- train/evaluation split
- 객관 리뷰와 사람 청취 리뷰 병행

### Phase 4. 한국어 연기 데이터셋 확장

상태: recording-check, recording-plan, split-recording, transcript-review, dataset-split v1은 구현됨. 검증된 대규모 데이터셋은 아직 필요.

목표:

- 화자별 30-120분의 깨끗한 한국어 녹음
- 역할별 연기 데이터 포함
- 숫자, 날짜, 영어 약어, 문장 끝, 조사, 어려운 발음 커버

필요:

- backend별 dataset export 형식

### Phase 5. 크리에이터 사운드 디자인 엔진

상태: 벤치마크 카탈로그, source-library 스캔/검증, 레시피 CLI, 공룡 렌더 진입점은 시작됨. 전체 소스 라이브러리 관리자와 다중 크리처 레이어 렌더러는 남아 있음.

목표:

- 대형 제작사가 성우와 음향효과를 만드는 방식을 벤치마킹
- 그 방식을 무료 한국어 친화 창작자 워크플로로 전환
- 모든 소스 레이어의 출처와 라이선스 명확화
- 인간 캐릭터 변환과 완전한 비인간 크리처 사운드 디자인 분리
- 비인간 역할에서는 개인 목소리의 정체성을 노출하지 않고 타이밍과 에너지만 사용

필요:

- `kva source-library add`
- waveform indexing, tag, source provenance check
- 늑대, 괴물, 외계 생명체, 폴리 중심 역할까지 확장된 `kva creature-design` render
- 영상 클립의 폴리/action spotting
- A/B/C 후보 생성과 사람 청취 점수
- 비교, 원본 bypass, 출처/라이선스 표시, export가 가능한 로컬 UI

### Phase 6. 로컬 앱 UI

상태: CLI만 존재.

목표:

- 비개발자도 사용 가능
- WAV를 끌어 넣기
- 역할 선택
- 듣기, 비교, export
- 출처, 라이선스, AI 음성 고지 명확히 표시

필요:

- 로컬 데스크톱 또는 웹 UI
- waveform preview
- role preset editor
- review dashboard

### Phase 7. 릴리스 패키징

상태: wheel build smoke는 통과. 정식 릴리스 자동화는 남아 있음.

목표:

- 깔끔한 설치
- `kva doctor` 실행
- CI 통과
- 영어 기본 문서와 선택 한국어 문서 제공

필요:

- release checklist 자동화
- 서명된 release artifact
- versioned changelog
- private 음성이 없는 beginner example

## 완료의 정의

KVAE는 사용자가 다음을 할 수 있을 때 완성에 가까워집니다.

1. 설치한다.
2. `kva doctor`를 실행한다.
3. private 또는 public 한국어 음성 profile을 선택한다.
4. 한국어 텍스트 또는 녹음 연기를 입력한다.
5. 여러 목소리 후보를 생성한다.
6. review report를 확인한다.
7. 출처, 라이선스, AI 음성 고지를 확인한다.
8. private 음성 데이터를 public repo 밖에 둔다.
9. 자신의 취향에 맞게 역할과 검증 기준을 수정한다.
