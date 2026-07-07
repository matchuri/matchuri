---
name: matchuri-doc-governance
description: Matchuri 문서 구조와 컨텍스트 무게를 관리한다. docs 감사, docs/GitHub Wiki/AGENTS.md/repo-local skill/harness script 배치 판단, 문서 인벤토리 생성, 추적 문서의 무시된 local wiki 경로 링크 점검이 필요할 때 사용한다.
---

# Matchuri 문서 거버넌스

## 개요

Matchuri 문서를 가볍게 유지한다. 사람용 서사, 지속되는 개발 계약, 재사용 agent workflow, 결정적 검증을 분리한다.

## 분류

각 문서나 추가 제안을 하나의 주 분류로 지정한다.

| Bucket | 의미 | 위치 |
| --- | --- | --- |
| KEEP | repo와 함께 이동해야 하는 현재 개발 계약 또는 index | `docs/` |
| SKILL | 반복되는 agent workflow 또는 절차 checklist | `.agents/skills/<skill>/SKILL.md` |
| HARNESS | 기계적으로 확인할 규칙 | skill `scripts/`, repo scripts, tests, CI |
| WIKI | 사람이 읽는 프로젝트 서사 또는 portfolio 설명 | GitHub Wiki |
| REMOVE | 중복, 오래됨, 대체됨 | 고유 계약이 없음을 확인한 뒤 삭제 |

## 절차

1. root `AGENTS.md`와 가장 가까운 하위 `AGENTS.md`를 읽는다.
2. `docs/`를 감사할 때 inventory harness를 실행한다.

   ```powershell
   python .agents\skills\matchuri-doc-governance\scripts\audit_docs.py --root .
   ```

   저장된 1차 inventory를 갱신할 때 실행한다.

   ```powershell
   python .agents\skills\matchuri-doc-governance\scripts\audit_docs.py --root . --output .agents\skills\matchuri-doc-governance\references\current-docs-inventory.md
   ```

3. 생성된 분류를 최종 진실이 아니라 1차 판단으로 취급한다.
4. `docs/`에는 구현 source of truth, API/data index, ADR급 결정만 남긴다.
5. 반복 절차는 `docs/`를 늘리지 말고 skill로 옮긴다.
6. 기계적으로 확인할 규칙은 prose가 아니라 harness script로 옮긴다.
7. 프로젝트 이야기, portfolio 설명, 읽기 쉬운 요약은 GitHub Wiki로 옮긴다.
8. `matchuri.wiki/...` 같은 무시된 local wiki 경로를 추적 문서에 링크하지 않는다.
9. 현재 작업이 Wiki 생성, 수정, 감사, 이동을 명시하지 않으면 `matchuri.wiki/`를 읽거나 검색하지 않는다.

## `docs/`에 남길 것

아래 질문에 답하는 짧은 문서를 남긴다.

- 현재 구현 계약은 무엇인가?
- 권위 있는 API, data, backend, frontend 진입점은 어디인가?
- 반복 논쟁을 막는 지속적 architectural decision은 무엇인가?
- code, tests, agents가 공유해야 하는 domain language는 무엇인가?

긴 tutorial prose보다 index와 간결한 decision record를 우선한다.

## Skill로 전환할 것

반복되는 agent workflow를 설명하는 내용은 `.agents/skills` 아래 repo-local skill로 만들거나 갱신한다.

- API contract change flow
- Data model change flow
- Backend feature implementation flow
- Frontend API integration flow
- GitHub Wiki writing flow
- Documentation slimming and drift review

`SKILL.md`는 간결하게 유지한다. 결정적 작업은 `scripts/`에 둔다.

## Harness로 전환할 것

사람 판단 없이 확인할 수 있는 규칙은 script, test, CI check로 검증한다.

- tracked docs의 금지 링크
- 오래된 API status entry
- OpenAPI endpoint drift
- schema/index drift
- API 또는 data 변경 시 필수 docs 갱신 여부
- 과도하게 큰 docs 또는 중복 heading

## GitHub Wiki 경계

GitHub Wiki는 별도의 사람용 문서 공간이다. 추적 문서는 GitHub Wiki URL을 링크할 수 있지만, `matchuri.wiki/Home.md` 같은 무시된 local path를 링크하지 않는다.

Wiki 문서는 독립적으로 읽히게 작성한다. `docs/`, `backend/`, `frontend/`로 돌아가는 root-relative link를 사용하지 않는다.

일반 개발, API, data, backend, frontend 작업에서는 local `matchuri.wiki/`를 무시한다. 구현 기준은 code와 `docs/`를 사용한다. 사람용 Wiki content를 만들거나 고칠 때만 Wiki 파일을 연다.

## 보고

감사를 끝낼 때 아래를 보고한다.

- total file count와 total size
- size 기준 largest docs
- bucket counts
- 즉시 반영한 edits
- 다음 migration candidates
