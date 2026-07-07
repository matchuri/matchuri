# 품질 기준

이 문서는 Matchuri backend 품질 판단의 현재 기준만 남깁니다. 실제 리뷰 절차와 기록 형식은 `.agents/skills/matchuri-backend-quality-review/SKILL.md`를 사용합니다.

품질 평가는 점수 자체보다 다음 작업 우선순위를 정하는 데 사용합니다. Matchuri는 맛집 검색 서비스가 아니라 점심 메뉴 결정 비용을 줄이는 서비스이므로, 품질 판단도 제품 흐름, 도메인 일관성, 검증 가능성, 운영 단순성을 함께 봅니다.

## 평가 원칙

- 품질은 통과/실패가 아니라 상대적 점수로 봅니다.
- 점수는 코드 인상비평이 아니라 확인 가능한 근거로 매깁니다.
- 자동화 지표가 있으면 먼저 사용하고, 부족한 부분만 사람 판단으로 보완합니다.
- 구현 복잡도보다 사용자 가치와 운영 단순성을 우선합니다.
- 미확정 판단은 `가정(Assumption):`으로 표시합니다.

## 점수 스케일

모든 항목은 `0-5점`으로 채점합니다.

| 점수 | 의미 | 기준 |
| --- | --- | --- |
| 0 | 없음 | 기준, 구현, 문서, 검증 흔적이 거의 없음 |
| 1 | 매우 부족 | 최소 형태만 있고 유지보수에 쓰기 어려움 |
| 2 | 기초 수준 | 동작은 보이나 누락, 모호함, 수동 의존이 많음 |
| 3 | 실무 가능 | 현재 팀 규모에서 운영 가능한 기본 수준 |
| 4 | 좋음 | 구조, 검증, 문서가 비교적 잘 맞물림 |
| 5 | 매우 좋음 | 현재 단계의 기대치를 넘고 회귀 위험이 낮음 |

## 평가 항목

| 항목 | 질문 | 대표 근거 |
| --- | --- | --- |
| 제품 적합성 | 빠른 메뉴 합의에 기여하는가 | 제품 명세, UX 흐름, 상태 전이 |
| 도메인/용어 일관성 | 문서, code, API의 용어가 일치하는가 | entity, DTO, status, error code |
| 구조 단순성 | 2인 팀이 이해하고 운영하기 쉬운가 | 책임 분리, 의존 방향, 과한 추상화 여부 |
| 변경 용이성 | 이후 기능 추가나 수정이 안전한가 | 응집도, 중복, 결합도, diff 범위 |
| 테스트/검증 가능성 | 회귀를 빠르게 잡을 수 있는가 | tests, lint, CI, 수동 검증 절차 |
| 문서/계약 명확성 | 구현 의도와 외부 계약이 명확한가 | OpenAPI, `docs/api`, ADR, code comment |
| 운영 준비도 | 배포 후 문제 파악과 복구가 가능한가 | log, error handling, env 분리, 보안/신뢰성 기준 |

## 자동화 근거

현재 바로 사용할 수 있는 신호는 아래와 같습니다.

| 영역 | 상태 | 확인 |
| --- | --- | --- |
| Backend tests | 가능 | `backend`에서 `./gradlew test` |
| Backend CI | 있음 | `backend/.github/workflows/backend-ci.yml` |
| Backend coverage | 가능 | `./gradlew test jacocoTestReport` |
| Frontend lint | 가능 | `frontend`에서 `npm run lint` |
| Frontend tests/coverage | 없음 | 추후 도입 후보 |

## 현재 기준선

이 기준선은 정밀 감사 결과가 아니라 현재 문서와 구현 상태에서 출발점을 잡기 위한 값입니다.

| 항목 | 점수 | 메모 |
| --- | ---: | --- |
| 제품 적합성 | 3 | 제품 목표와 핵심 흐름 문서는 비교적 명확함 |
| 도메인/용어 일관성 | 3 | 핵심 용어 기준은 있으나 구현 전반 정합성 점검 필요 |
| 구조 단순성 | 3 | 소수 팀 운영 방향은 명확하나 세부 구조 보강 여지 있음 |
| 변경 용이성 | 2 | 중복과 결합도는 실제 code 기준 점검 필요 |
| 테스트/검증 가능성 | 2 | Backend CI와 JaCoCo 가능, Frontend 자동 테스트 부족 |
| 문서/계약 명확성 | 3 | 상위 기준 문서는 있으나 구현 변경과 동기화 루틴 필요 |
| 운영 준비도 | 2 | 운영 기준은 있으나 실제 복구 절차 구체화 필요 |

## 관련 skill

- backend 품질 리뷰: `.agents/skills/matchuri-backend-quality-review/SKILL.md`
- backend 보안 리뷰: `.agents/skills/matchuri-backend-security-review/SKILL.md`
- backend 신뢰성 리뷰: `.agents/skills/matchuri-backend-reliability-review/SKILL.md`
