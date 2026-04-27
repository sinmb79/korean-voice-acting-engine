# Voice Lab 워크플로

[English document](VOICE_LAB_WORKFLOW.md)

`kva voice-lab`은 사용자가 한 번 녹음한 음성을 여러 캐릭터 목소리 후보로 한 번에 만드는 제품형 워크플로입니다.

이 명령은 다음을 묶습니다.

1. 음성 변환
2. 역할별 manifest 저장
3. 선택적 오디오 리뷰
4. playlist 생성
5. summary report 생성

## 빠른 시작

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine voice-lab `
  --input my_performance.wav `
  --out-dir outputs\voice-lab-demo `
  --group default `
  --expected-file script.txt `
  --asr-model base
```

출력 폴더에는 다음이 생깁니다.

- `*.wav`
- `*.result.json`
- `*.manifest.json`
- `*.review.json`
- `playlist.m3u`
- `voice_lab_summary.json`
- `README.md`

## Dry Run

오디오를 만들기 전에 계획만 확인할 수 있습니다.

```powershell
python -m kva_engine voice-lab `
  --input my_performance.wav `
  --out-dir outputs\voice-lab-plan `
  --roles wolf_growl_clear,monster_deep_clear `
  --dry-run
```

## 추천 역할

이름 있는 group:

- `default`: 균형 잡힌 시작 세트
- `dialogue`: 내레이터, 선생님, 이야기꾼, 악역, 어린이
- `creature`: 늑대, 괴물, 공룡 clear/heavy/fx/roar 변형
- `narration`: calm, documentary, news, storyteller
- `shorts`: 창작자용 압축 세트

기본 group 역할:

- `calm_narrator`
- `wolf_growl_clear`
- `monster_deep_clear`
- `dinosaur_giant_clear`
- `child_bright`

대사 전달용은 clear 계열을 우선 사용합니다. heavy, fx, roar 계열은 연출용 질감으로 보는 것이 좋습니다.

## 남은 개발

`voice-lab`은 안정적인 계약을 먼저 만든 것입니다. 이후 내부 엔진은 다음으로 확장할 수 있습니다.

- neural speech-to-speech 변환
- 공개 음성 모델 렌더 어댑터
- 로컬 GUI
- 역할별 한국어 명료도 기준
- 더 큰 연기 데이터셋
