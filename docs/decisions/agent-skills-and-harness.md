# Agent Skills와 Harness 도입 기준

이 문서는 Matchuri에서 `docs/`가 무거워지는 문제를 줄이기 위해 agent skill과 harness를 어떤 기준으로 도입할지 정리합니다.

## 배경

사람이 읽는 프로젝트 문서는 GitHub Wiki로 분리합니다.

`docs/`는 구현과 함께 갱신해야 하는 개발 기준 문서로 유지하되, 반복 작업 절차와 자동 검증 가능한 규칙까지 모두 담으면 에이전트가 읽어야 할 문맥이 계속 커집니다.

## 결정

- `AGENTS.md`는 짧은 라우터와 필수 검증 명령만 담습니다.
- 반복되는 에이전트 작업 절차는 repo-local skill인 `.agents/skills/`에 둡니다.
- 기계적으로 판정 가능한 규칙은 harness script나 테스트로 둡니다.
- `docs/`는 개발 기준, 계약 인덱스, ADR급 결정만 남기는 방향으로 줄입니다.
- GitHub Wiki는 사람이 읽는 프로젝트 설명과 포트폴리오 서사를 담당합니다.

## 현재 도입 항목

- 문서 거버넌스 스킬: `.agents/skills/matchuri-doc-governance/SKILL.md`
- 문서 인벤토리 하네스: `.agents/skills/matchuri-doc-governance/scripts/audit_docs.py`
- 현재 인벤토리 reference: `.agents/skills/matchuri-doc-governance/references/current-docs-inventory.md`

## 분류 기준

| 분류 | 의미 | 위치 |
| --- | --- | --- |
| KEEP | 개발 기준이나 계약으로 계속 유지 | `docs/` |
| SKILL | 반복되는 에이전트 작업 절차 | `.agents/skills/` |
| HARNESS | 자동 검증 가능한 규칙 | scripts/tests/CI |
| WIKI | 사람이 읽는 설명과 포트폴리오 서사 | GitHub Wiki |
| REMOVE | 중복, 오래된 가정, 대체된 문서 | 삭제 검토 |

## 다음 후보

- API 상세 장문 문서는 OpenAPI metadata, API 상태표, drift harness 중심으로 줄입니다.
- 데이터 스키마 장문 문서는 엔티티/마이그레이션 기반 생성 또는 검증 harness로 전환합니다.
- 백엔드 보안, 신뢰성, 품질 점수 문서는 review skill과 검증 스크립트로 분리합니다.
- 제품 서사는 GitHub Wiki로 옮기고 `docs/product/`는 제품 판단 기준만 남깁니다.
