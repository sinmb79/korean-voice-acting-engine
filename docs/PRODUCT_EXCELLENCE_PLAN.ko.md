# 최상급 제품화 계획

[English document](PRODUCT_EXCELLENCE_PLAN.md)

KVAE의 다음 목표는 모든 음성 변환이 해결된 것처럼 말하는 것이 아닙니다. 목표는 한국어에 특화된 최상급 음성 제작 엔진이 되도록, 모든 산출물을 측정 가능하고, 검수 가능하고, 안전하고, 개선 가능한 상태로 만드는 것입니다.

## 리서치 요약

검토한 외부 방향:

- [VoxCPM2](https://github.com/OpenBMB/VoxCPM): Apache-2.0, 한국어 공식 지원, voice design, controllable cloning, LoRA, 48kHz 출력이 있어 KVAE의 현재 기본 로컬 백엔드로 유지합니다.
- [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano): CPU/ONNX 경로가 있어 저사양 로컬 fallback 후보로 중요합니다.
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice): Apache-2.0, 한국어 포함 다국어 zero-shot 후보이며 streaming 설계도 참고 가치가 있습니다.
- [F5-TTS](https://github.com/SWivid/F5-TTS): 연구 benchmark로 유용하지만, 저장소가 pretrained model을 CC-BY-NC라고 밝히므로 production 기본값으로 쓰면 안 됩니다.
- [IndexTTS2](https://github.com/index-tts/index-tts): duration control과 emotion control 관점에서 중요하지만, custom model license라 법적 검토가 필요합니다.
- [Fish Speech / Fish Audio S2](https://github.com/fishaudio/fish-speech): 품질 ceiling benchmark로 볼 가치가 있지만, commercial use는 별도 Fish Audio license가 필요합니다.
- [Resemble AI Speech-to-Speech](https://www.resemble.ai/products/speech-to-speech): 연기 타이밍과 감정을 보존하면서 target voice로 바꾸는 외부 production 대안입니다.
- [ElevenLabs Korean TTS / voice cloning](https://elevenlabs.io/text-to-speech/korean): 빠르게 polished Korean voice가 필요할 때 쓸 수 있는 cloud external fallback입니다.
- [iZotope RX Dialogue Isolate](https://www.izotope.com/en/products/rx/features/dialogue-isolate)와 [Adobe Enhance Speech](https://podcast.adobe.com/en/enhance-speech-v2): KVAE가 억지로 복원하려 들면 안 되는 심한 노이즈/반향 복원 전문 도구입니다.

## 제품 원칙

최상급 KVAE의 조건:

- 한국어 대본 정규화와 발음 계획을 먼저 한다.
- 개인 목소리는 기본적으로 로컬에 보호한다.
- 백엔드 후보는 많이 보되, 한국어 evidence를 통과한 것만 승격한다.
- 자동 리뷰와 사람 청취 리뷰를 함께 요구한다.
- 로컬 엔진, 외부 cloud service, 연구-only 모델을 명확히 구분한다.
- 공개 산출물마다 동의, 출처, 라이선스, AI 음성 고지를 남긴다.

## 새 제품 게이트

이제 KVAE는 다음 명령을 제공합니다.

```powershell
python -m kva_engine eval-suite --out-dir outputs\korean-eval-suite
python -m kva_engine product-quality --backend voxcpm2 --use-case shorts --review outputs\sample.review.json --human-scores outputs\sample.human.json
```

release state:

- `ready`: 모든 gate 통과
- `conditional`: hard failure는 없지만 warning 존재
- `needs_evidence`: audio review나 사람 청취 리뷰가 없음
- `blocked`: non-commercial backend를 제품 release에 쓰려는 등 hard gate 실패

## 평가 suite

한국어 평가 suite는 다음을 포함합니다.

- 날짜, 시간, 숫자, 금액, 전화번호, 주소
- 한국어와 영어 model name, acronym 혼합
- 숏츠 one-take narration
- 드라마식 호흡과 감정
- 다큐멘터리 pacing
- 받침 발음 최소대립쌍
- 동의와 AI 고지 문장
- backend 반복 안정성

백엔드 후보는 승격 전에 같은 문장을 모두 렌더해야 합니다.

## 사람 청취 점수

최상급 release에는 사람 청취 점수 파일이 필요합니다.

```json
{
  "korean_pronunciation": 4.5,
  "naturalness": 4.4,
  "emotion_fit": 4.2,
  "artifact_control": 4.5,
  "use_case_fit": 4.3,
  "overall": 4.4
}
```

점수 기준:

- 1: 사용 불가
- 2: 나쁨
- 3: 초안으로는 가능
- 4: 제품 사용 가능
- 5: 우수

## 최상급 제품으로 가는 순서

1. 보스의 private voice로 VoxCPM2를 평가 suite 전체에 실행하되, 산출물은 git 밖에 저장합니다.
2. 모든 sample에 `kva review-audio`를 실행합니다.
3. 보스가 직접 듣고 human listening score를 남깁니다.
4. `kva product-quality`로 release 가능 여부를 판정합니다.
5. MOSS-TTS-Nano와 CosyVoice3는 별도 local environment 설치 후 같은 방식으로 비교합니다.
6. F5-TTS, IndexTTS2, Fish Audio S2는 production 권리 문제가 해결되기 전까지 non-commercial/license gate 뒤에 둡니다.
7. 백엔드 품질이 안정적으로 통과한 뒤, 비개발자용 로컬 UI를 붙입니다.
