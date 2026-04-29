# Character Review Engine

[English document](CHARACTER_REVIEW_ENGINE.md)

`kva review-character`는 생성된 WAV가 요청한 KVAE 배역의 음향 형태에 가까운지 검증합니다. 사람의 최종 청취 판단을 대체하지는 않지만, 왜 결과물이 아직 그 배역처럼 들리지 않는지 반복 가능한 수치와 경고로 보여줍니다.

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine review-character `
  --audio outputs\dinosaur.wav `
  --role dinosaur_giant_roar `
  --out outputs\dinosaur.character-review.json
```

## 왜 필요한가

고급 음성 프로그램은 렌더러만 갖고 있지 않습니다. 목표 화자 유사도, 명료도, 아티팩트, 사람 검수 루프를 함께 둡니다. Dehumaniser 계열의 크리처 사운드 디자인도 저역 몸통 공명, 목 압력, 거칠기, 사람 말소리 흔적 제거를 따로 봅니다.

KVAE도 같은 구조가 필요합니다. Character Review Engine은 WAV에서 거친 음향 특징을 측정하고, 배역별 기준과 비교해서 경고를 만듭니다.

## 측정 지표

- `body_index`: 저역 몸통/가슴/크리처 공명
- `brightness_index`: 고역 존재감, 공기감, 짧은 성도 느낌
- `grit_index`: 거칠기, 압력, 목소리 마찰, 엔벨로프 흔들림
- `human_speech_trace_index`: 깨끗한 사람 말소리 포먼트 잔여감
- `stability_index`: 발화 에너지의 안정성

배역군별 기준:

- `dinosaur`: 높은 몸통감, 낮은 사람 말소리 흔적, 과하지 않은 밝기, 충분한 목 압력
- `monster`: 높은 몸통감과 거칠기, 낮은 원본 화자 잔여감
- `wolf`: 늑대형 몸통감과 growl 질감
- `child`: 밝은 성도감과 낮은 성인 저역 잔여감
- `female_lead`: 밝고 가벼운 몸통, 안정적인 대사
- `male_lead`: 절제된 몸통과 통제된 presence
- `narration`: 명료도, 온기, 안정성의 균형

## 출력

JSON에는 다음이 들어갑니다.

- `score`: 0부터 100까지의 배역 적합도 프록시
- `status`: `pass`, `warn`, `fail`
- `warnings`: 문제 라벨
- `features`: 측정된 음향 값
- `target_metrics`: 배역군별 기준
- `findings`: 기준을 벗어난 항목
- `development_actions`: 다음에 조정해야 할 렌더러 방향

## Voice Lab 연결

`kva voice-lab`은 review가 켜져 있을 때 각 후보마다 `*.character-review.json`을 함께 씁니다. 요약 JSON과 README에는 character score가 들어가므로, 모든 manifest를 열지 않아도 후보를 비교할 수 있습니다.

## 한계

이 기능은 예술적으로 설득력 있는지를 증명하지는 않습니다. 대신 명백한 불일치와 회귀를 잡아냅니다. 다음 단계는 사람의 A/B 청취 판단과 한국어 연기 데이터셋을 모아 역할 유사도 평가기를 학습시키는 것입니다.
