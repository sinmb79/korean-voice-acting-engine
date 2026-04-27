# Dataset License Matrix

메타 설명: 한국어 TTS 개발에 참고할 데이터셋의 라이선스와 사용 경계를 추적하는 문서.

작성자: 22B Labs · 제4의 길 (The 4th Path)

태그: dataset, license, Korean TTS, AI-Hub, KSS, CoreaSpeech

| Dataset | Use | License / Boundary | Project Decision |
|---|---|---|---|
| User self-recorded voice pack | Personal voice profile | User-owned, local-only by default | Never commit raw audio or personal model |
| KSS Dataset | Korean single-speaker baseline research | Check upstream license before redistribution | Reference only until license is confirmed |
| CoreaSpeech | Korean benchmark and preprocessing reference | Check official release and license before training | Use as research reference first |
| AI-Hub speech data | Korean large-scale reference | Requires account, terms, and dataset-specific checks | Do not redistribute |
| Custom volunteer recordings | Multi-style voice acting data | Written consent required | Allowed only with consent manifest |

## Required Manifest Fields

```json
{
  "dataset_id": "user-voice-pack-001",
  "source": "self_recorded",
  "owner": "user",
  "consent_type": "self",
  "allowed_use": ["local_training", "private_generation"],
  "redistribution_allowed": false,
  "notes": "Do not commit raw audio or checkpoints."
}
```

