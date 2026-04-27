# 릴리스 품질 게이트

[English document](RELEASE_QUALITY_GATES.md)

KVAE는 코드가 실행된다고 끝난 것이 아닙니다. 릴리스는 런타임, 개인정보 보호, 문서, 오디오 리뷰 게이트를 통과해야 합니다.

## 필수 명령

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m compileall -q src
python -m kva_engine doctor --voice-profile public:mms-tts-kor
```

## 개인정보 보호 게이트

공개 파일에 다음이 있으면 릴리스하지 않습니다.

- 개인 로컬 사용자명 또는 private 음성 절대경로
- private 음성 녹음
- private LoRA 또는 모델 체크포인트
- 생성된 WAV/MP3/FLAC/M4A 파일
- 로컬 토큰 또는 API 키 문자열

권장 Windows 점검:

```powershell
Get-ChildItem -Recurse -File -Include *.py,*.md,*.json,*.jsonl,*.txt -Path . |
  Where-Object { $_.FullName -notmatch '\\.git\\|\\outputs\\|\\__pycache__\\|default_voice\.local\.json$' } |
  Select-String -Pattern 'C:\Users\your-private-name','github_token_prefix' -SimpleMatch
```

## 런타임 게이트

`kva doctor`는 다음을 확인해야 합니다.

- Python 3.11+
- 공개 음성 카탈로그 사용 가능
- 오디오 변환/리뷰용 `ffmpeg`, `ffprobe` 사용 가능
- private voice profile이 git에서 제외됨
- ASR 리뷰가 필요할 때 선택적 Whisper 사용 가능

## 오디오 게이트

생성 음성은 아래처럼 리뷰합니다.

```powershell
python -m kva_engine review-audio `
  --audio outputs\sample.wav `
  --expected-file script.txt `
  --asr-model base `
  --role calm_narrator `
  --out outputs\sample.review.json
```

최소 확인 항목:

- WAV 존재
- 샘플레이트와 채널 수 정상
- clipping 없음
- RMS가 너무 낮지 않음
- 무음 비율이 과도하지 않음
- 선택한 역할 기준 CER/WER 허용 범위

## 문서 게이트

공개 문서는 영어를 기본으로 합니다. 한국어 문서는 필요한 곳에 `.ko.md` 선택 문서로 제공합니다.

모든 공개 AI 음성 항목은 다음을 포함해야 합니다.

- 출처 URL
- 라이선스
- 상업적 사용 가능 여부
- 표기문
- AI 음성 고지

## 아직 부족한 점

KVAE는 더 깊은 neural training 통합, 사용자용 앱, 더 큰 한국어 연기 데이터셋이 필요합니다. 그 전까지 모든 릴리스는 현재 한계를 솔직히 밝히고, 사용자가 역할·음성·품질 기준을 수정/보완할 수 있는 길을 열어둬야 합니다.
