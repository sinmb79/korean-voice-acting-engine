# KVAE Review Engine

[English document](KVAE_REVIEW_ENGINE.md)

KVAE는 음성을 만든 뒤 바로 검증 기록을 남깁니다. 목표는 “파일이 생성됐다”에서 멈추지 않고, 보스가 실제로 들어보기 전에 기본 품질과 대본 일치도를 먼저 확인하는 것입니다.

## review-audio

생성/변환된 WAV를 검사합니다.

```powershell
python -m kva_engine review-audio `
  --audio outputs\wolf.wav `
  --expected-file outputs\script.txt `
  --asr-model base `
  --role wolf_growl `
  --out outputs\wolf.review.json
```

Whisper가 설치되어 있지 않거나 이미 전사문이 있는 경우에는 `--asr-text`를 사용할 수 있습니다.

```powershell
python -m kva_engine review-audio `
  --audio outputs\wolf.wav `
  --expected-text "오늘은 테스트입니다." `
  --asr-text "오늘은 테스트입니다." `
  --out outputs\wolf.review.json
```

리포트에는 다음 항목이 들어갑니다.

- WAV 존재 여부, 길이, 샘플레이트, 채널, RMS, peak, silence ratio
- Whisper 전사 결과 또는 제공된 `asr_text`
- CER/WER
- clipping, 과도한 무음, 너무 작은 음량, 너무 짧은 오디오 경고
- voice profile privacy와 redistribution 제한 정보

## recording-check

학습용 원본 녹음 파일을 점검합니다.

```powershell
python -m kva_engine recording-check `
  --audio C:\Users\you\workspace\shared-voices\my-voice\references\voice_ko_reference.wav `
  --out outputs\recording-check.json
```

현재 기준은 보수적입니다.

- 30초 미만이면 학습용으로 짧다고 경고합니다.
- 프로덕션 학습 원본은 44.1kHz 또는 48kHz mono WAV를 권장합니다.
- 긴 무음, clipping 의심, 너무 낮은 peak/RMS를 경고합니다.

## 해석 기준

`ok: true`는 자동 점검에서 치명적 문제가 없다는 뜻입니다. 전문 성우 품질을 보장한다는 뜻은 아닙니다.

캐릭터 변환에서는 효과가 강한 프리셋일수록 ASR 점수가 떨어질 수 있으므로, clear 계열과 heavy/fx/roar 계열을 함께 만들어 사람이 최종 선택해야 합니다.
