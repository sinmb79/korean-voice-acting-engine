# Secure Development Notes

메타 설명: 보안환경에서 KVA Engine을 개발하고 실행하기 위한 로컬 우선 원칙과 제한 사항.

작성자: 22B Labs · 제4의 길 (The 4th Path)

태그: secure environment, local-first, no network, Korean TTS, offline development

## 기본 원칙

이 프로젝트의 초기 코어는 보안환경을 전제로 한다. 네트워크가 없거나 제한되어도 한국어 전처리, 발음 사전, 성우 planning, 테스트가 동작해야 한다.

## 개발 기본값

- 외부 API 호출 금지
- 실행 중 자동 모델 다운로드 금지
- 원격 telemetry 금지
- 사용자 음성 원본 업로드 금지
- 표준 라이브러리 우선
- 의존성 추가 시 이유와 대체 경로 문서화
- 개인 음성, 개인 모델, 생성 결과는 기본적으로 로컬 보관

## 현재 구현 상태

현재 `v0.1 Korean Engine MVP`는 Python 표준 라이브러리만 사용한다.

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine normalize "OpenAI API는 3.5초 안에 응답했다."
python -m unittest discover -s tests
```

Windows PowerShell에서 한국어 inline argument가 깨지는 경우가 있다. 이때는 명령줄에 한국어 문장을 직접 넣지 말고 UTF-8 파일을 만든 뒤 `--file`로 처리한다.

## 나중에 모델 학습을 붙일 때의 원칙

- 학습 데이터 경로는 명시적으로 사용자가 지정한다.
- 모델 다운로드는 자동으로 하지 않는다.
- 다운로드가 필요한 경우 문서에 별도 절차로 분리한다.
- 오프라인 wheel/cache 설치 경로를 우선 지원한다.
- checkpoint와 voice profile은 `.gitignore`와 manifest로 보호한다.
