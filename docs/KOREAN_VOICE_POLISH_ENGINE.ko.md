# Korean Voice Polish Engine

[English document](KOREAN_VOICE_POLISH_ENGINE.md)

KVAE의 현실적인 제품 방향은 “전혀 다른 성우, 아이, 괴물, 공룡 목소리를 마법처럼 만드는 것”이 아니라 한국어 음성을 또렷하고 안정적으로 손질하는 것입니다.

`kva polish`는 원본 화자의 정체성을 유지하면서 실제 사용처에 맞게 녹음을 다듬습니다.

- `cleanup`: 자연스러운 기본 정리
- `announcer`: 한국어 아나운서처럼 또렷한 발화
- `shorts`: 숏츠용으로 더 단단하고 앞으로 나오는 내레이션
- `drama`: 연기 호흡을 살리는 부드러운 대사 정리
- `documentary`: 따뜻한 장문 내레이션

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine polish `
  --input my_voice.wav `
  --preset announcer `
  --out outputs\my_voice.announcer.wav `
  --manifest-out outputs\my_voice.announcer.json
```

## 하는 일

KVAE 내부 DSP로 다음 처리를 합니다.

- DC offset 제거
- high-pass/low-pass 정리
- 온기, 명료도, presence, air EQ
- 치찰음 완화
- 약한 노이즈 플로어 제어
- 말소리 압축
- 피크 정규화
- 화자 정체성이 유지된다는 안전 manifest 기록

## 하지 않는 일

이 엔진은 한 명의 성인 녹음에서 새로운 화자, 아이 목소리, 크리처 목소리, 전문 성우를 만들 수 있다고 주장하지 않습니다.

그런 변환은 훨씬 큰 한국어 데이터셋, 동의된 목표 음성, neural speech-to-speech 모델, 사람 A/B 검수 루프가 있어야 가능합니다. 현재 공개 KVAE의 기본 제품 약속으로 두지 않습니다.

## 제품 약속

KVAE는 한국어 창작자가 자신의 목소리를 더 쓸 만하게 만드는 도구가 되어야 합니다.

- 더 또렷한 발화
- 더 깨끗한 내레이션
- 더 안정적인 음량
- 숏츠, 드라마, 다큐, 공지, 교육용 세팅
- 개인 음성 자산의 로컬 우선 보호

작은 약속이지만, 정직하고 실제로 쓸 수 있는 방향입니다.
