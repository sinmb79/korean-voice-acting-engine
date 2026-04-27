# Research Review: Korean Voice Acting Engine

메타 설명: 공개 TTS 엔진, 한국어 TTS 연구, 국내 서비스 사례, 사용자 피드백을 검토해 KVA Engine 구현서에 반영한 근거 문서.

작성자: 22B Labs · 제4의 길 (The 4th Path)

태그: TTS research, Korean TTS, VibeVoice, voice acting engine, text normalization, speech synthesis, safety

조사일: 2026-04-27

---

## 1. 핵심 판단

한국어 TTS의 병목은 "음성 생성 모델" 하나가 아니다. 한국어는 숫자, 영어 약어, 외래어, 조사, 받침, 연음, 경음화, 호흡, 문장 끝 억양이 함께 얽히기 때문에, 모델 앞단의 한국어 엔진이 약하면 큰 모델도 어색하게 읽는다.

성우 엔진은 보이스 클로닝과 다르다. 보이스 클로닝은 음색을 닮게 하는 기술이고, 성우 엔진은 발성, 호흡, 속도, 감정 압력, 쉼, 캐릭터 해석을 조절하는 연기 계획 시스템이다.

따라서 KVA Engine의 순서는 유지한다.

```text
Korean Engine
-> Voice Acting Engine
-> Neural Speech Engine
-> Review & Correction Engine
```

## 2. VibeVoice 검토

출처:

- https://github.com/microsoft/VibeVoice
- https://arxiv.org/abs/2508.19205
- https://openreview.net/pdf?id=FihSkzyxdv
- https://github.com/microsoft/VibeVoice/blob/main/docs/vibevoice-realtime-0.5b.md

관찰:

- VibeVoice는 장문 대화형, 다화자 podcast generation을 주요 목표로 한다.
- continuous acoustic/semantic tokenizers, ultra-low frame rate 7.5 Hz, next-token diffusion, speaker turn labels가 핵심이다.
- 장문에서 화자 일관성, 자연스러운 turn-taking, breath/lip-smack 같은 비언어 cue를 중요하게 본다.
- Realtime 0.5B는 영어 중심이고, 한국어 등 다국어는 탐색용이며 예측 불가능할 수 있다고 밝힌다.
- TTS 코드 제거 이력이 있어 제품 의존성으로 삼기에는 위험하다.
- GitHub 이슈에는 own voices, new language training, skipped words 문제가 올라와 있다.

반영:

- VibeVoice는 제품 백엔드가 아니라 long-form multi-speaker 연구 레퍼런스로 둔다.
- scene/turn context, speaker turn labels, speaker consistency 평가를 KVA 데이터 포맷에 넣는다.
- long-form track을 별도 개발 트랙으로 둔다.
- Realtime 모델의 short input/symbol instability 경고를 반영해 짧은 입력과 특수기호 처리 가드레일을 만든다.

## 3. 한국어 전처리와 데이터셋

출처:

- g2pK: https://github.com/Kyubyong/g2pK
- CoreaSpeech: https://openreview.net/forum?id=8nHq0IIwpd
- KSS Dataset: https://huggingface.co/datasets/Bingsu/KSS_Dataset
- Korean FastSpeech2: https://github.com/HGU-DLLAB/Korean-FastSpeech2-Pytorch

관찰:

- g2pK는 영어 단어 한글 변환, 문맥 기반 숫자 읽기, 자모 출력, 규칙 예외 사전을 지원한다.
- g2pK 문서도 규칙만으로 모든 예외를 덮을 수 없다고 본다.
- CoreaSpeech는 한국어 TTS 부족의 원인으로 rigorous preprocessing, Korean-specific benchmarks, Korean-optimized models 부족을 지적한다.
- CoreaSpeech는 숫자와 영어 용어 정규화, 자모 기반 coreset selection을 강조한다.
- Korean FastSpeech2는 한국어 TTS에서도 duration alignment가 중요함을 보여준다.

반영:

- Korean Engine은 `speech_text`, `phoneme_text`, `normalization_trace`를 모두 출력해야 한다.
- benchmark는 학습 데이터와 분리한다.
- hard Korean benchmark는 jamo coverage, final consonant coverage, number pattern coverage, English-mixed pattern coverage를 가져야 한다.
- 사용자 발음 사전은 모든 규칙보다 우선한다.

## 4. 공개 TTS 엔진 사용자 피드백

출처:

- F5-TTS spelling/number issue: https://github.com/SWivid/F5-TTS/issues/409
- F5-TTS cross-lingual accent issue: https://github.com/SWivid/F5-TTS/issues/315
- CosyVoice Korean-focused fine-tuning issue: https://github.com/FunAudioLLM/CosyVoice/issues/1470
- Chatterbox: https://github.com/resemble-ai/chatterbox
- CosyVoice: https://github.com/FunAudioLLM/CosyVoice
- MeloTTS: https://github.com/myshell-ai/MeloTTS
- Supertonic: https://github.com/supertone-inc/supertonic

관찰:

- F5-TTS issue에서는 숫자와 철자가 누락되거나 너무 빠르게 읽히고, 출력 일관성이 흔들리는 문제가 보고되었다.
- cross-lingual voice cloning에서는 reference language와 target language가 다를 때 accent transfer가 발생할 수 있다.
- Chatterbox는 reference clip과 target language 불일치 시 accent risk가 있음을 팁으로 제시한다.
- CosyVoice는 Korean 포함 다국어, text normalization, pronunciation inpainting, streaming을 제공하지만, 한국어 특화 fine-tuning 전략은 사용자들이 별도로 질문할 만큼 불확실성이 남아 있다.
- Supertonic은 ONNX 기반 on-device TTS와 Korean support를 내세워 로컬 배포 방향을 참고할 만하다.

반영:

- 한국어 출력에는 한국어 reference clip을 기본 요구한다.
- `accent_risk` 필드를 manifest에 넣는다.
- 숫자/철자/전화번호/버전/짧은 입력은 별도 회귀 테스트로 관리한다.
- spelling은 글자 사이 pause와 rate를 강제할 수 있어야 한다.
- ONNX export와 local-first deployment는 장기 목표로 둔다.

## 5. 국내 기업 사례

출처:

- KT Voice AI: https://ai.kt.com/resources/detail03
- Humelo: https://humelo.com/
- Humelo comparison: https://humelo.com/insights/korean-tts-api-comparison-2026
- Kakao SSML: https://developers.kakao.com/assets/guide/kakao_ssml_guide.pdf
- SELVAS: https://www.selvasai.com/tts
- ReadSpeaker Korea: https://www.readspeaker.co.kr/assets/files/%EB%A6%AC%EB%93%9C%EC%8A%A4%ED%94%BC%EC%BB%A4%EC%BD%94%EB%A6%AC%EC%95%84_TTS_%EC%8B%A0%EC%86%8C%EA%B0%9C%EC%9E%90%EB%A3%8C_2024v2.0.pdf
- Soree: https://getsoree.com/

관찰:

- KT는 TTS에서 숫자, 기호, 약어 자동 변환 text normalization을 한국어 자연성의 핵심으로 본다.
- Humelo는 한국어 음운 규칙, 조사/어미 억양, 단어장, 감정, 쉼표, 템포를 제품 가치로 내세운다.
- Kakao SSML은 `say-as`, `sub`, `prosody`, `break`, `voice`를 통해 발음과 호흡을 제어한다.
- Soree 같은 소형 서비스도 `JSON -> 제이슨`, `API -> 에이피아이`, 숫자 변환, 발음 사전을 핵심 기능으로 내세운다.
- 국내 TTS 플레이어들은 "한국어 전처리"를 숨은 기술이 아니라 상품의 전면 가치로 보고 있다.

반영:

- KVA Engine의 v0.1은 모델 없이도 독립 배포 가능한 Korean reading package가 되어야 한다.
- `say_as`, `substitution`, `break`, `formality`, `tone`, `tempo`, `pause`를 내부 스크립트 필드로 둔다.
- 발음 사전은 핵심 UX다. 나중에 붙이는 설정 파일로 취급하지 않는다.

## 6. 보정된 위험 등록부 요약

| 위험 | 영향 | 대응 |
|---|---|---|
| 숫자/영어 예외 폭발 | 오독 증가 | normalization trace, 사용자 사전, unknown token 검수 |
| cross-lingual accent transfer | 한국어 억양 악화 | 한국어 reference 우선, accent risk 표시 |
| identity와 role 충돌 | 모든 배역이 같거나 내 목소리 상실 | identity_strength와 role_strength 분리 |
| 장문 일관성 붕괴 | 긴 영상 제작 불가 | scene context, speaker state, turn labels |
| 짧은 입력/기호 불안정 | 누락, 이상 발음 | input guardrail, symbol normalization |
| 데이터 라이선스 위험 | 공개 배포 불가 | dataset manifest, allowed_use 검사 |
| 사칭/악용 | 프로젝트 지속 불가 | consent manifest, watermark, disclosure metadata |
| 로컬 추론 비용 | 일반 사용자 접근성 저하 | model-free v0.1, ONNX/quantization 장기 목표 |

## 7. 최종 반영 결정

- VibeVoice는 의존하지 않고 배운다.
- Korean Engine은 모델보다 먼저 만든다.
- 성우 엔진은 보이스 체인저가 아니라 acting planner다.
- 데이터는 양보다 coverage와 license가 먼저다.
- 공개 배포는 safety by design으로 시작한다.
- 첫 공개 가치는 "한국어를 제대로 읽는 오픈소스 엔진"이다.

마지막 문장:

> 한국어는 모델에 얹는 옵션이 아니라, 엔진이 출발하는 땅이다.
