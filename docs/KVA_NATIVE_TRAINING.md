# KVA 네이티브 학습 방향

메타 설명: 외부 TTS 엔진이 아니라 KVA 자체 모델 포맷으로 가족 음성을 학습시키기 위한 현재 구현과 다음 단계.

태그: KVA Native, 한국어 TTS, 성우 엔진, 음성 학습, 로컬 학습, 22B Labs

## 핵심 결정

이 프로젝트는 VoxCPM, Chatterbox, VibeVoice 같은 기존 엔진을 제품의 중심에 두지 않습니다. 그 엔진들은 참고 대상일 수는 있지만, 우리가 만들 모델의 주인은 `kva-native`입니다.

현재 구현된 `train-native` 명령은 가족 음성 레지스트리를 읽어 KVA 자체 모델 파일을 만듭니다. 이 모델은 아직 파형을 직접 생성하는 신경망이 아니라, KVA 엔진이 사용할 첫 번째 음성 정체성 층입니다.

## 현재 모델 형식

출력 스키마:

```text
kva.native_voice_model.v1
```

포함하는 정보:

- 가족 구성원별 actor identity
- 언어별 acoustic profile
- RMS, peak, zero crossing rate, silence ratio, DC offset 기반 voiceprint
- KVA timbre controls
- 성우 역할별 acting role controls
- 역할 평균 voiceprint
- 보안/동의 정책
- 다음 신경망 학습 단계

포함하지 않는 정보:

- 원본 오디오 복사본
- 외부 서버 업로드 정보
- 공개 가능한 가족 음성 파일
- 실제 neural vocoder weights

## 실행 명령

```powershell
cd D:\Workspace\Korean-Voice-Acting-Engine
$env:PYTHONPATH = "src"
python -m kva_engine train-native `
  --registry D:\Workspace\22b-family-voice-registry `
  --out outputs\family_voice_training\kva_native_voice_model.json
```

특정 역할만 학습할 수도 있습니다.

```powershell
python -m kva_engine train-native `
  --registry D:\Workspace\22b-family-voice-registry `
  --role father `
  --out outputs\family_voice_training\father.kva-native.json
```

## 왜 이걸 먼저 만들었나

성우 엔진은 단순히 음색을 복제하는 기계가 아닙니다. “누가 말하는가”와 “어떤 배역으로 말하는가”를 분리해야 합니다.

그래서 KVA 모델은 먼저 가족 음성의 정체성 층을 만들고, 그 위에 `calm_narrator`, `documentary`, `news_anchor`, `bright_teacher`, `old_storyteller`, `villain_low`, `childlike_fast`, `ai_assistant` 같은 역할 제어를 얹습니다.

이 구조가 있어야 같은 사람의 목소리에서 성우처럼 다른 배역을 만들 수 있습니다.

## 집 컴퓨터에서 이어서 할 일

1. 오프라인 Python 환경에 `torch`, `torchaudio`, `numpy`, `soundfile`, `librosa`를 설치합니다.
2. `outputs\family_voice_training\kva_native_voice_model.json`을 KVA native identity seed로 사용합니다.
3. 가족 음성 원본은 공개 repo 밖에 유지합니다.
4. 한국어 텍스트 정규화 결과인 `speech_script`와 KVA native voice model을 함께 넣는 acoustic trainer를 구현합니다.
5. 먼저 `son` 프로필처럼 LoRA가 없는 가족 구성원부터 KVA native neural adapter를 학습합니다.

## 한계

현재 `train-native`는 우리 엔진의 첫 학습 단계입니다. 그러나 아직 완전한 TTS가 아닙니다. 파형 생성을 위해서는 다음 모듈이 필요합니다.

- Korean acoustic model
- duration predictor
- pitch/energy predictor
- neural vocoder
- ASR 기반 발음 검수 루프

지금 만든 것은 씨앗입니다. 중요한 건 이 씨앗이 남의 엔진에 붙어 있는 게 아니라, 우리 엔진의 이름으로 자라고 있다는 점입니다.

작성자: **22B Labs · 제4의 길 (The 4th Path)**
