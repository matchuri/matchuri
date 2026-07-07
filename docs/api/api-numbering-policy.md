# API 넘버링/버저닝 정책

이 문서는 Matchuri API ID의 부여, 삽입, 변경, 폐기 기준을 정의합니다.
API ID는 FE-BE 간 소통과 Swagger UI 탐색성을 위한 문서 식별자이며, `/api/v1` 같은 경로 버전과는 별개입니다.

## 목표

- FE-BE가 특정 API를 짧고 안정적인 ID로 지칭할 수 있게 합니다.
- Swagger UI에서 사용자 플로우 순서대로 API를 탐색할 수 있게 합니다.
- 요구사항 변경으로 플로우 중간에 API가 추가되어도 기존 ID 변경을 최소화합니다.
- API 경로, 메서드, DTO 이름과 독립적으로 유지되는 문서 식별자를 둡니다.

## 기본 형식

API ID는 플로우 코드와 두 개의 숫자 구간을 `.`으로 구분합니다.

```text
FLOW.NNN.NNN
```

예:

```text
AUTH.020.000
AUTH.020.500
GREC.080.000
```

각 구간의 의미:

| 구간 | 의미 | 예시 |
| --- | --- | --- |
| `FLOW` | 큰 사용자 플로우를 나타내는 고유 영문 코드 | `AUTH` 인증/가입, `GREC` 그룹 추천/투표 |
| 첫 번째 `NNN` | 플로우 안의 기본 API 순서 | `GREC.020.000` 준비 상태 조회 |
| 두 번째 `NNN` | 중간 삽입이나 세부 변형을 위한 여백 | `GREC.020.500` 준비 상태 조회와 다음 단계 사이에 추가 |

## 플로우 코드

현재 기준 플로우 코드는 아래처럼 사용합니다.

| 코드 | 플로우 |
| --- | --- |
| `OPS` | 공통/운영 |
| `AUTH` | 인증/가입 |
| `ONB` | 온보딩/내 정보 |
| `REF` | 메뉴/취향 참조 |
| `REC` | 개인 추천 |
| `GROUP` | 그룹 생성/참여 |
| `GREC` | 그룹 추천/투표 |
| `ADMIN` | 관리자 데이터 운영 |

새로운 큰 사용자 플로우가 생기면 의미가 분명한 새 영문 코드를 추가합니다.
기존 플로우 코드의 의미를 바꾸거나 숫자 순서를 재배치하는 대신 새 플로우 코드를 추가하는 것을 우선합니다.
전체 사용자 플로우 정렬은 API ID가 아니라 `docs/api/api-status.md`의 섹션 순서와 Swagger tag 정렬로 관리합니다.

## 부여 규칙

- `FLOW`는 대문자 영문과 숫자만 사용합니다.
- `FLOW`는 가능한 한 3-6자 정도의 짧은 코드로 둡니다.
- 기본 API는 마지막 숫자 구간을 `000`으로 둡니다.
- 같은 플로우 안에서는 사용자 흐름에서 먼저 호출되는 API가 더 작은 번호를 갖습니다.
- 조회 API가 화면 진입에 먼저 필요하면 생성/수정 API보다 앞설 수 있습니다.
- 관리자 API는 일반 사용자 플로우와 섞지 않고 `ADMIN` 플로우에 둡니다.
- Deprecated API도 API ID를 유지하며, 새 API가 대체하면 새 API는 별도 ID를 받습니다.
- 삭제된 API의 ID는 재사용하지 않습니다.

## 중간 삽입 규칙

기존 API 사이에 새 API가 추가되면 세 번째 구간을 사용합니다.

예:

```text
GREC.020.000  그룹 추천 준비 상태 조회
GREC.030.000  그룹 추천 준비 완료
```

두 API 사이에 준비 세션 취소 API가 추가되면:

```text
GREC.020.000  그룹 추천 준비 상태 조회
GREC.020.500  그룹 추천 준비 세션 취소
GREC.030.000  그룹 추천 준비 완료
```

같은 구간에 추가 삽입이 필요하면 남은 숫자 가운데를 사용합니다.

```text
GREC.020.000
GREC.020.250
GREC.020.500
GREC.020.750
GREC.030.000
```

마지막 숫자 구간이 과도하게 촘촘해지면 기존 ID를 재정렬하기보다 새 플로우 코드 또는 새 기본 순번을 검토합니다.
이미 이슈, PR, 슬랙, 문서에서 공유된 API ID는 바꾸지 않는 것을 원칙으로 합니다.

## Swagger/OpenAPI 반영 기준

API ID는 `OpenApiConfig`의 OpenAPI customizer에서 `path + method` 기준으로 일괄 반영합니다.
이 방식은 Swagger UI 표시 정책을 한 곳에서 관리하고, `GroupApi`처럼 한 인터페이스 안에 여러 플로우가 섞인 경우에도 operation별 태그를 분리하기 위한 기준입니다.

반영 항목:

- `summary` 앞에 API ID prefix를 붙입니다.
- `x-api-id` OpenAPI extension을 추가합니다.
- operation tag를 플로우 정렬용 tag로 교체합니다.
- OpenAPI `paths` 산출 순서를 API ID 매핑 순서에 맞춰 재정렬합니다.

Swagger UI 표시 예:

```text
[GREC.080.000] 그룹 추천 후보 투표
```

주의:

- `operationId`에 `.`이 들어간 API ID를 그대로 넣지 않습니다.
- `operationId`는 코드 생성기 호환성을 위해 영문 식별자 형태를 유지합니다.
- 일부 Swagger UI와 코드 생성기는 문자열 정렬을 사용하므로 숫자 구간은 `010`, `020`, `100`처럼 0을 채웁니다.
- 태그 정렬이 필요하면 태그명에는 `01 Auth`, `06 Group Recommendation` 같은 정렬용 prefix를 붙일 수 있습니다.
- 태그 정렬용 숫자는 API ID의 일부가 아니며, 전체 플로우 순서를 바꾸기 위한 표시값입니다.

## 변경과 폐기

API ID는 API 계약의 커뮤니케이션 키로 취급합니다.

- Path가 바뀌어도 같은 개념의 API가 유지되면 기존 ID 유지 여부를 먼저 검토합니다.
- 요청/응답 계약이 크게 바뀌어 FE-BE 연동 관점에서 다른 API처럼 다뤄야 하면 새 ID를 부여합니다.
- Deprecated API의 ID는 deprecated 상태로 남기고 재사용하지 않습니다.
- 같은 API가 mock에서 real로 바뀌는 경우에는 ID를 바꾸지 않습니다.
- 단순 summary, description, example 수정은 ID 변경 사유가 아닙니다.

## 문서 업데이트 체크리스트

API ID를 추가하거나 바꾸면 아래를 함께 확인합니다.

- `docs/api/api-status.md`
- 관련 `docs/api/*` 상세 문서
- `OpenApiConfig`의 API ID customizer 매핑
- 필요한 경우 관련 `*Api.java` OpenAPI 메타데이터
- `/docs/openapi` 산출물과 Swagger UI 표시
- API 문서 테스트가 summary나 tag를 고정하고 있는지 여부
