# Safety Policy

메타 설명: KVA Engine의 음성 합성, 보이스 캐스팅, 개인 음성 학습 기능을 안전하게 공개하기 위한 정책 초안.

작성자: 22B Labs · 제4의 길 (The 4th Path)

태그: AI safety, voice cloning, consent, watermark, Korean TTS, open source

## 원칙

KVA Engine은 실제 사람의 목소리를 무단 복제하기 위한 도구가 아니다. 사용자가 동의해 제공한 목소리를 바탕으로, 가상의 캐릭터와 창작용 배역을 만드는 도구다.

## 금지

- 타인의 목소리를 동의 없이 학습하거나 배포
- 유명인, 성우, 가족, 지인 목소리 무단 복제
- 실제 인물을 사칭하는 음성 생성
- 금융, 정치, 법률, 의료, 공공기관 사칭
- 보이스피싱, 사기, 협박, 허위 증거 제작
- 출처 불명 음성 데이터로 학습한 모델 공개

## 필수 설계

- voice profile 생성 시 consent manifest 요구
- 생성 결과에 AI-generated metadata 포함
- 공개 AI 음성 사용 시 source, license, attribution, AI voice disclosure를 manifest에 포함
- 워터마크 또는 disclosure hook 제공
- 개인 음성 원본과 개인 모델은 저장소에 포함하지 않음
- 데이터셋별 allowed_use 확인

## 공개 배포 기본값

초기 공개 버전은 한국어 전처리와 성우 planning 중심으로 배포한다. 개인 음성 학습과 고품질 합성 모델은 안전 장치가 구현된 뒤 단계적으로 연다.
