# 외부 검토: Quark 음향효과, Narrator AI CLI Skill, Open Generative AI

[English document](EXTERNAL_REVIEW_QUARK_NARRATOR_OPEN_GENERATIVE.md)

이 문서는 KVAE가 무엇을 직접 흡수하고, 무엇을 외부 도구나 라이선스 확인 대상으로 남겨야 하는지 정리합니다.

## 1. Quark 공유 음향효과 라이브러리

출처: https://pan.quark.cn/s/86e913fbb254

확인한 공유 정보:

- 공유 제목: `百万剪辑狮的音效库`
- 대략적 크기: 2.98GB
- 확인된 전체 파일/폴더 수: 2,368개
- 확인된 파일 수: 2,125개
- 상위 분류에는 동물 음향, 네트워크 음향, 장면 음향, 효과음, 스포츠, 악기, 무기, 동작 음향 등이 포함됩니다.

라이선스 판단:

- 검사한 공유 메타데이터 안에서는 재배포권이나 상업적 사용권이 명확히 보이지 않았습니다.
- KVAE 안에 이 음원을 직접 넣거나 재배포하면 안 됩니다.

KVAE에 가져올 점:

- 폴더 분류 방식은 사운드 라이브러리 taxonomy 참고자료로 쓸 수 있습니다.
- 크리처/폴리 제작은 동물, 신체, 충격, 공간, 기계, 합성, 음성 컨트롤러 레이어를 분리해야 합니다.
- 실제 제작에 쓸 음원은 파일별 출처, 라이선스, 저작자 표기, 재배포 가능 여부가 있어야 합니다.

안전한 반영 방식:

- `kva capabilities`에 `sound_effect_library_intake` 경로를 추가합니다.
- 사용자가 합법적으로 내려받았거나 구매한 로컬 폴더만 `kva source-library --scan-dir <licensed-sfx-folder>`로 스캔합니다.
- Quark 공유자료는 라이선스 증거가 생기기 전까지 분류 참고자료로만 봅니다.
- 제3자 SFX 파일은 공개 KVAE 저장소 밖에 둡니다.

## 2. Narrator AI CLI Skill

저장소: https://github.com/NarratorAI-Studio/narrator-ai-cli-skill

로컬 검토 스냅샷:

- 이 저장소 밖의 외부 검토 폴더에 clone해서 확인했습니다.
- Git commit: `32076844614836812cedbffd1b69010b1e8c26e8`
- License: MIT

성격:

- 외부 `narrator-ai-cli`를 AI 에이전트가 다룰 수 있게 만든 skill 문서입니다.
- 영화, 드라마, 숏폼 내레이션 영상 제작 흐름을 대상으로 합니다.
- `narrator-ai-cli`와 `NARRATOR_APP_KEY`가 필요합니다.
- 외부 파이프라인은 소스 선택, BGM, 더빙 목소리, 내레이션 템플릿, 대본 생성, 클립 데이터, 영상 합성, 선택적 영상 템플릿 생성을 다룹니다.

KVAE에 가져올 점:

- 소스 자료, BGM, 더빙 목소리, 템플릿은 자동 선택하지 않고 사용자 확인을 받아야 합니다.
- 더빙 목소리 언어, 대본 생성 언어, 영상 템플릿 텍스트 언어가 일치해야 합니다.
- 자료 목록은 끝까지 페이지네이션한 뒤 검색해야 하며, 잘린 터미널 출력만 믿으면 안 됩니다.
- 외부 비동기 작업은 완료될 때까지 poll해야 합니다.
- 외부 task/order identifier는 handoff manifest에 정확히 남겨야 합니다.

안전한 반영 방식:

- `kva capabilities`에 `external_video_narration_api` 경로를 추가합니다.
- `video_dubbing_editing`의 외부 대체 도구로 Narrator AI CLI Skill을 추가합니다.
- KVAE는 한국어 대본, 음성, SRT, 검수 메타데이터를 준비하고, 외부 결과물을 다시 검수합니다.
- KVAE가 자체적으로 영상 소스 라이브러리, 유료 task 제출, 영상 합성 API를 제공한다고 말하면 안 됩니다.

## 3. Open Generative AI

저장소: https://github.com/Anil-matcha/Open-Generative-AI

로컬 검토 스냅샷:

- 이 저장소 밖의 외부 검토 폴더에 clone해서 확인했습니다.
- Git commit: `894b520516ca5c87d62ec5bfd840d13ec71e3a04`
- 라이선스 판단: README에는 MIT라고 되어 있지만, 검토한 스냅샷에서는 루트 `LICENSE` 파일과 GitHub license metadata가 확인되지 않았습니다.

성격:

- 이미지, 영상, 시네마 샷, 워크플로, 립싱크를 다루는 별도 제작 스튜디오입니다.
- Muapi 기반 hosted API와 일부 모델의 로컬 데스크톱 inference 경로를 제공합니다.
- 립싱크 기능은 음성으로 인물 이미지나 기존 영상의 입 움직임을 맞추는 용도입니다.

KVAE에 가져올 점:

- KVAE가 손질한 한국어 WAV, 대본, 타이밍 노트, 고지 메타데이터를 시각/립싱크 단계로 넘길 수 있습니다.
- 립싱크와 영상 생성은 한국어 음성 품질 엔진과 분리해야 합니다.
- 로컬/원격 모델 선택, 하드웨어 조건, 산출물 출처 정보가 사용자에게 보여야 합니다.

안전/라이선스 경계:

- 해당 프로젝트는 unrestricted 또는 no-filter 생성을 강하게 내세웁니다. KVAE는 이 태도를 가져오면 안 됩니다.
- KVAE는 동의, 초상권, 출처, AI 고지, 공개 전 검수 원칙을 유지해야 합니다.
- 저장소 라이선스가 명확해지기 전까지 코드를 KVAE에 복사하지 않습니다.

안전한 반영 방식:

- `kva capabilities`에 `visual_generation_lipsync` 경로를 추가합니다.
- 최종 시각/립싱크 조립의 외부 대체 도구로 Open Generative AI를 추가합니다.
- KVAE와 외부 도구 사이에는 WAV, TXT, SRT, JSON, 타이밍 노트, 검수된 결과 경로만 주고받습니다.
