# 개인 추천 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: recommendation / behavior
- 기준 소스:
  - JPA Entity: `PersonalRecommendation`, `PersonalRecommendationCandidate`, `MemberMenuAction`, `PersonalRecommendationStatus`, `ActionType`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: 개인 추천 API 문서

## 기준 소스 우선순위

1. JPA Entity와 enum
2. `backend/init/sql/01-schema.sql`
3. 추천 service write path와 repository query
4. 관련 API 문서

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| `personal_recommendations.status` 길이 | JPA `varchar(30)` | init SQL `varchar(20)` | JPA 기준으로 문서화하되 init SQL 정합성 확인 필요 | DDL 보정 검토 |
| `personal_recommendations.close_reason` | JPA 필드 없음 | init SQL 컬럼 존재 | 현재 JPA 미사용 컬럼으로 기록 | DDL 제거 또는 엔티티 반영 여부 결정 |

## 문서 목적

- 개인 추천 실행, 후보, 회원 메뉴 행동 로그의 현재 테이블 구조를 정의합니다.
- 추천 재요청, 후보 선택, 후보 제외 로그가 어떤 테이블에 저장되는지 설명합니다.

## 현재 확정 전제

- 개인 추천은 회원 단위로 생성합니다.
- 추천 후보는 메뉴 단위이며 장소/가게 정보와 분리합니다.
- 후보 이해를 돕기 위해 추천 컨텍스트와 후보 메타데이터는 JSON 컬럼으로 저장할 수 있습니다.
- 회원의 추천 이후 행동은 `member_menu_actions`에 별도 로그로 저장합니다.
- `SKIP` 행동은 일정 기간 후보 제외 조건에 사용할 수 있습니다.

가정(Assumption):

- 개인 추천 후보 수와 추천 알고리즘 상세 점수 구조는 현재 DB 스키마에 강하게 고정하지 않습니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `personal_recommendations` | 개인 추천 실행 세션 | `PersonalRecommendation`, `01-schema.sql` |
| `personal_recommendation_candidates` | 개인 추천 후보 메뉴 | `PersonalRecommendationCandidate`, `01-schema.sql` |
| `member_menu_actions` | 회원 메뉴 행동 로그 | `MemberMenuAction`, `01-schema.sql` |

## `personal_recommendations`

### 역할

- 회원이 실행한 개인 추천 세션의 상태와 컨텍스트를 저장합니다.
- 최종 선택 후보와 종료 시각을 기록합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 개인 추천 ID |
| `member_id` | bigint | N |  | FK | 회원 ID |
| `status` | varchar(30) | N |  | enum | 개인 추천 lifecycle 상태 |
| `closed_at` | datetime | Y |  |  | 추천 종료 시각 |
| `close_reason` | varchar(30) | Y |  | DDL only, JPA 미사용 | 종료 사유 후보 컬럼 |
| `requested_at` | datetime | N |  |  | 추천 실행 시각 |
| `context_json` | json | Y |  | JSON | 추천 컨텍스트 스냅샷 |
| `selected_candidate_id` | bigint | Y |  | FK | 최종 선택 후보 ID |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 개인 추천 식별자 |
| FK | `fk_personal_recommendations_member` | `member_id -> members.id` | 추천 요청 회원 |
| FK | `fk_personal_recommendations_selected_candidate` | `selected_candidate_id -> personal_recommendation_candidates.id` | 최종 선택 후보 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_personal_recommendations_member` | `member_id` | 회원별 추천 조회 | `01-schema.sql` |
| `idx_personal_recommendations_selected_candidate` | `selected_candidate_id` | 선택 후보 역조회 | `01-schema.sql` |

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `status` | `OPEN` | 후보 선택 대기 |
| `status` | `SELECTED` | 후보 선택 완료 |
| `status` | `REROLLED_WITH_SKIP` | 기존 후보 제외 후 재추천 |
| `status` | `REROLLED_WITHOUT_SKIP` | 기존 후보 제외 없이 재추천 |
| `status` | `EXPIRED` | 만료 |
| `status` | `FAILED` | 추천 실패 |

## `personal_recommendation_candidates`

### 역할

- 개인 추천 세션에서 제시된 후보 메뉴를 저장합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 개인 추천 후보 ID |
| `personal_recommendation_id` | bigint | N |  | FK, unique 조합 | 개인 추천 ID |
| `menu_id` | bigint | N |  | FK, unique 조합 | 후보 메뉴 ID |
| `rank_no` | int | N |  |  | 후보 순위 |
| `score` | double | Y |  |  | 0~100 정규화 추천 점수 |
| `candidate_meta_json` | json | Y |  | JSON | 후보 설명/메타데이터 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 후보 식별자 |
| FK | `fk_personal_recommendation_candidates_recommendation` | `personal_recommendation_id -> personal_recommendations.id` | 부모 추천 |
| FK | `fk_personal_recommendation_candidates_menu` | `menu_id -> menu_items.id` | 후보 메뉴 |
| unique | `uk_personal_recommendation_candidate_menu` | `personal_recommendation_id`, `menu_id` | 같은 추천 안에서 같은 메뉴 중복 방지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_personal_recommendation_candidates_menu` | `menu_id` | 메뉴 기준 추천 후보 조회 | `01-schema.sql` |

## `member_menu_actions`

### 역할

- 회원이 메뉴에 대해 발생시킨 클릭, 선호, 비선호, 선택, 제외 행동을 로그로 저장합니다.
- 개인 추천 후보 제외나 행동 분석의 근거가 됩니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 행동 로그 ID |
| `member_id` | bigint | N |  | FK | 회원 ID |
| `menu_id` | bigint | N |  | FK | 메뉴 ID |
| `personal_recommendation_id` | bigint | Y |  | FK | 출처 개인 추천 ID |
| `action_type` | varchar(20) | N |  | enum | 행동 유형 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |

`member_menu_actions`는 `CreatedAtEntity`를 사용하므로 `updated_at`이 없습니다.

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 행동 로그 식별자 |
| FK | `fk_member_menu_actions_member` | `member_id -> members.id` | 행동 회원 |
| FK | `fk_member_menu_actions_menu` | `menu_id -> menu_items.id` | 대상 메뉴 |
| FK | `fk_member_menu_actions_personal_recommendation` | `personal_recommendation_id -> personal_recommendations.id` | 출처 추천 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_member_menu_actions_member` | `member_id` | 회원별 행동 조회 | `01-schema.sql` |
| `idx_member_menu_actions_menu` | `menu_id` | 메뉴별 행동 조회 | `01-schema.sql` |
| `idx_member_menu_actions_personal_recommendation` | `personal_recommendation_id` | 추천별 행동 조회 | `01-schema.sql` |

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `action_type` | `CLICK` | 메뉴 클릭 |
| `action_type` | `LIKE` | 선호 |
| `action_type` | `DISLIKE` | 비선호 |
| `action_type` | `CHOOSE` | 선택 |
| `action_type` | `SKIP` | 후보 제외/건너뜀 |

## 관계

| 기준 | 대상 | 관계 | 설명 |
| --- | --- | --- | --- |
| `personal_recommendations.member_id` | `members.id` | N : 1 | 추천 요청 회원 |
| `personal_recommendation_candidates.personal_recommendation_id` | `personal_recommendations.id` | N : 1 | 추천 후보 |
| `personal_recommendation_candidates.menu_id` | `menu_items.id` | N : 1 | 후보 메뉴 |
| `member_menu_actions.member_id` | `members.id` | N : 1 | 행동 회원 |
| `member_menu_actions.menu_id` | `menu_items.id` | N : 1 | 행동 대상 메뉴 |

## 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 | 주의점 |
| --- | --- | --- | --- |
| 추천 생성 | `member_id` | 추천 row와 후보 row 저장 | 후보 메뉴 중복 방지 |
| 후보 선택 | `personal_recommendation_id`, `candidate_id` | `selected_candidate_id`, `status`, `closed_at` 갱신 | 이미 닫힌 추천 거절 |
| 재추천 | 추천 ID | 기존 추천 종료 후 새 추천 생성 | reroll 타입에 따라 행동 로그 저장 |
| 후보 제외 | `member_id`, `menu_id`, `action_type=SKIP` | 행동 로그 저장 | 기간 기반 제외 정책 확인 |

## 운영 기준

- 개인 추천 미선택 세션은 `requested_at + 24h` 기준 만료 처리 대상입니다.
- 별도 주기 scheduler 없이 생성/조회/상태 변경 접근 시 lazy expire를 적용할 수 있습니다.
- `context_json`과 `candidate_meta_json`은 추천 설명 가능성을 위해 유연하게 둡니다.

## 현재 제외 범위

- 추천 알고리즘 상세 feature table
- 개인 추천 투표 테이블
- 행동 로그 업데이트/수정 모델
- 장소/가게 기반 추천 저장

## 코드 변경 시 확인할 것

- `PersonalRecommendationStatus` 추가 시 상태 전이와 만료 처리를 함께 확인합니다.
- `ActionType` 추가 시 후보 제외 정책과 API 응답을 확인합니다.
- init SQL의 `close_reason` 유지 여부를 엔티티와 맞춰야 합니다.

## 함께 볼 문서

- [회원 테이블 정의서](./members-schema.md)
- [회원 취향 프로필 테이블 정의서](./member-taste-profiles-schema.md)
- [메뉴 카탈로그 테이블 정의서](./menu-catalog-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
