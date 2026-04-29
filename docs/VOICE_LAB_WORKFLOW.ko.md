# Voice Lab 워크플로

[English document](VOICE_LAB_WORKFLOW.md)

`kva voice-lab`은 한 번 녹음한 연기 음성을 여러 캐릭터 음성 후보로 한꺼번에 만드는 제품형 워크플로입니다.

포함하는 작업:

1. 음성 변환
2. 배역별 manifest 작성
3. 선택적 오디오 리뷰
4. 배역별 character-fit 리뷰
5. playlist 생성
6. summary report 생성

기본 변환 엔진은 KVAE 자체 WAV 렌더러인 `kva-native-character-v1`입니다. 기존 ffmpeg 필터 경로가 필요할 때만 `--engine ffmpeg`를 사용합니다.

## 빠른 시작

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine voice-lab `
  --input my_performance.wav `
  --out-dir outputs\voice-lab-demo `
  --group default `
  --engine native `
  --expected-file script.txt `
  --asr-model base
```

출력 폴더에는 다음 파일이 생깁니다.

- `*.wav`
- `*.result.json`
- `*.manifest.json`
- `*.review.json`
- `*.character-review.json`
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
  --engine native `
  --dry-run
```

## 추천 배역 그룹

- `default`: 균형 잡힌 시작 세트
- `dialogue`: 내레이터, 교사, 이야기꾼, 악역, 어린이, 오리지널 드라마 주인공
- `drama`: 21세기 대군부인 계열 남녀 주인공과 보조 배역
- `creature`: 늑대, 괴물, 공룡 clear/heavy/fx/roar 계열
- `narration`: calm, documentary, news, storyteller
- `shorts`: 창작자용 압축 세트

기본 그룹 배역:

- `calm_narrator`
- `wolf_growl_clear`
- `monster_deep_clear`
- `dinosaur_giant_clear`
- `child_bright`

대사는 `*_clear` 계열을 먼저 비교하는 것이 좋습니다. heavy, fx, roar 계열은 명료도보다 캐릭터성과 연출감을 확인하는 후보로 보는 것이 안전합니다.

## Character Review

review가 켜져 있으면 `voice-lab`은 각 후보마다 `kva review-character`도 함께 실행합니다. 요약에는 `character_score`, `character_status`, character warning이 들어가므로, WAV가 기술적으로는 정상이어도 공룡/어린이/괴물처럼 들리지 않는 후보를 바로 확인할 수 있습니다.

## 남은 개발

`voice-lab`은 안정적인 계약을 먼저 만든 워크플로입니다. 앞으로 다음 방향으로 확장합니다.

- 더 강력한 KVAE 자체 neural speech-to-speech 변환
- 공개 음성 모델 렌더 어댑터
- 로컬 GUI
- 학습형 배역별 한국어 명료도와 역할 유사도 기준
- 더 큰 한국어 연기 데이터셋
