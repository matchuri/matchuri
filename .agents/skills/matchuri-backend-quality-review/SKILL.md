---
name: matchuri-backend-quality-review
description: Matchuri backend 품질을 점수표 기반으로 리뷰한다. 백엔드 기능 구현, 리팩터링, PR 리뷰, 테스트/문서/운영 준비도 점검, 후속 작업 우선순위 선정이 필요할 때 사용한다.
---

# Matchuri Backend 품질 리뷰

## 개요

backend 변경이 Matchuri의 제품 목표, 도메인 구조, 테스트, 문서, 운영 가능성과 맞는지 점검한다. 점수 자체보다 다음 작업 우선순위를 정하는 데 집중한다.

## 먼저 읽을 것

1. root `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/backend/index.md`
4. `docs/backend/guide.md`
5. `docs/backend/architecture.md`
6. `docs/decisions/backend-code-quality.md`
7. 변경이 제품 흐름에 닿으면 `docs/product/product-sense.md`

구현 기준을 찾기 위해 GitHub Wiki나 local Wiki folder를 읽지 않는다.

## 평가 축

각 항목을 `0-5점`으로 채점한다. 점수는 확인 가능한 근거와 함께 적는다.

| 항목 | 핵심 질문 |
| --- | --- |
| 제품 적합성 | 이 변경이 빠른 메뉴 합의에 기여하는가 |
| 도메인/용어 일관성 | 문서, code, API의 용어와 경계가 일치하는가 |
| 구조 단순성 | 2인 팀이 이해하고 운영하기 쉬운가 |
| 변경 용이성 | 다음 기능 추가나 수정이 안전한가 |
| 테스트/검증 가능성 | 회귀를 빠르게 잡을 수 있는가 |
| 문서/계약 명확성 | 구현 의도와 외부 계약이 명확한가 |
| 운영 준비도 | 배포 후 문제 파악과 복구가 가능한가 |

점수 기준:

- `0`: 기준, 구현, 검증이 거의 없다.
- `1`: 최소 형태만 있고 유지보수에 쓰기 어렵다.
- `2`: 동작은 보이나 누락과 수동 의존이 많다.
- `3`: 현재 팀 규모에서 운영 가능한 기본 수준이다.
- `4`: 구조, 검증, 문서가 잘 맞물린다.
- `5`: 현재 단계의 기대치를 넘고 회귀 위험이 낮다.

## 절차

1. 변경 범위를 확인한다.
   - touched files
   - affected package
   - public API 여부
   - data model 변경 여부
   - 운영 또는 security 영향 여부

2. 자동화 근거를 먼저 수집한다.
   - `backend`에서 `./gradlew test`
   - 필요하면 `./gradlew test jacocoTestReport`
   - API 계약 변경이면 `python .agents\skills\matchuri-api-contract-sync\scripts\audit_api_contract.py --root .`
   - 실행하지 못한 명령은 이유를 보고한다.

3. code 구조를 확인한다.
   - `api -> domain -> infra` 의존 방향을 확인한다.
   - `service`, `command`, `result`, `support`, `exception`, `entity`, `repository` 책임을 확인한다.
   - business rule이 Controller, Mapper, docs DTO에 숨어 있지 않은지 확인한다.
   - 과한 추상화, 넓은 변경 범위, 큰 함수 증가를 확인한다.

4. 테스트와 계약을 확인한다.
   - 핵심 success/failure path가 테스트되는지 확인한다.
   - API 변경이면 OpenAPI metadata와 `docs/api`를 확인한다.
   - data 변경이면 `docs/data`와 migration/entity 정합성을 확인한다.
   - error code와 response envelope가 실제 구현과 일치하는지 확인한다.

5. 항목별 점수를 매긴다.
   - 자동화 근거로 설명 가능한 항목을 먼저 채점한다.
   - 사람 판단이 필요한 항목은 짧은 근거를 적는다.
   - 미확정 판단은 `가정(Assumption):`으로 적는다.

6. 후속 작업을 고른다.
   - `0-1점`: 즉시 수정 후보로 둔다.
   - `2점`: 기술 부채 후보로 두고 이유를 남긴다.
   - 같은 점수라면 사용자 흐름과 테스트/검증 가능성 리스크가 큰 항목을 먼저 고른다.
   - 운영 복잡도를 크게 늘리는 개선은 한 번 더 검토한다.

## 보고 형식

리뷰를 끝낼 때 아래 형식으로 보고한다.

| 항목 | 점수 | 근거 | 후속 액션 |
| --- | ---: | --- | --- |
| 제품 적합성 |  |  |  |
| 도메인/용어 일관성 |  |  |  |
| 구조 단순성 |  |  |  |
| 변경 용이성 |  |  |  |
| 테스트/검증 가능성 |  |  |  |
| 문서/계약 명확성 |  |  |  |
| 운영 준비도 |  |  |  |

추가로 실행한 명령, 실패한 검증, 남은 risk를 짧게 적는다.
