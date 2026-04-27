# KVAE Convert Engine

[English document](KVAE_CONVERT_ENGINE.md)

`kva convert`는 텍스트가 아니라 사용자가 직접 녹음한 음성 파일을 입력으로 받아, KVAE 역할/캐릭터 목소리로 변환합니다.

```powershell
python -m kva_engine convert `
  --input my_acting.wav `
  --role monster_deep `
  --out outputs\monster.wav
```

## 현재 엔진

현재 구현은 `kva-convert-ffmpeg-v1`입니다.

- 원본 연기의 길이와 호흡을 유지합니다.
- 역할별 pitch, tempo, EQ, roughness, echo를 적용합니다.
- loudness normalization을 적용합니다.
- output WAV와 manifest를 저장합니다.

이 단계는 즉시 사용할 수 있는 로컬 deterministic 변환 레이어입니다. 나중에 RVC, FreeVC, so-vits-svc, KVAE 자체 Korean STS 모델을 붙여도 CLI 계약은 유지합니다.

## 예시

```powershell
python -m kva_engine convert --input voice.wav --role wolf_growl --out wolf.wav
python -m kva_engine convert --input voice.wav --role wolf_growl_clear --out wolf-clear.wav
python -m kva_engine convert --input voice.wav --role wolf_growl_heavy --out wolf-heavy.wav
python -m kva_engine convert --input voice.wav --role monster_deep --out monster.wav
python -m kva_engine convert --input voice.wav --role monster_deep_clear --out monster-clear.wav
python -m kva_engine convert --input voice.wav --role monster_deep_fx --out monster-fx.wav
python -m kva_engine convert --input voice.wav --role dinosaur_giant --out dinosaur.wav
python -m kva_engine convert --input voice.wav --role dinosaur_giant_clear --out dinosaur-clear.wav
python -m kva_engine convert --input voice.wav --role dinosaur_giant_roar --out dinosaur-roar.wav
python -m kva_engine convert --input voice.wav --role child_bright --out child.wav
```

## 변환 뒤 자동 검증

변환 결과는 `review-audio`로 바로 점검할 수 있습니다.

```powershell
python -m kva_engine review-audio `
  --audio wolf.wav `
  --expected-file script.txt `
  --asr-model base `
  --role wolf_growl `
  --out wolf.review.json
```

강한 효과가 들어간 `monster_deep_fx`, `dinosaur_giant_roar`는 캐릭터성은 강하지만 발음 명료도가 낮아질 수 있습니다. 최종 제품에서는 `*_clear` 계열을 기본 후보로 만들고, heavy/fx/roar 계열은 연출용 후보로 함께 비교합니다.
