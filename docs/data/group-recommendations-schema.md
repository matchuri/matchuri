# 그룹 추천 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: group / recommendation
- 기준 소스:
  - JPA Entity: `GroupRecommendation`, `GroupRecommendationReadiness`, `GroupRecommendationCandidate`, `GroupRecommendationVote`, `GroupMenuAction`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: 그룹 추천 API 문서

## 기준 소스 우선순위

1. JPA Entity와 enum
2. `backend/init/sql/01-schema.sql`
3. 그룹 추천 service write path와 repository query
4. 관련 API 문서

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| `group_recommendation_readiness` | JPA Entity 존재 | init SQL 테이블 없음 | 현재 운영 엔티티 기준으로 문서화 | init SQL 생성문/FK/인덱스 추가 필요 |
| `group_recommendation_votes.updated_at` | `BaseEntity`라 `updated_at` 존재 | init SQL에는 `created_at`만 존재 | JPA 기준으로 문서화하되 DDL 정합성 확인 필요 | init SQL 보정 검토 |

## 문서 목적

- 그룹 추천 세션, 준비 상태, 후보, 투표, 그룹 메뉴 행동 로그의 현재 테이블 구조를 정의합니다.
- MVP의 `후보 3개 안팎 + 투표 + 최종 메뉴 확정` 흐름에서 각 테이블이 맡는 책임을 설명합니다.

## 현재 확정 전제

- 그룹 추천은 그룹 방 기준으로 생성합니다.
- `PREPARING` 상태에서는 멤버별 준비 완료를 기다릴 수 있습니다.
- `OPEN` 상태에서는 후보 메뉴와 투표를 진행합니다.
- 투표는 추천 세션별/회원별 1개 row를 유지하고, 재투표 시 같은 row의 후보를 변경합니다.
- 그룹 추천에서 후보가 거절된 맥락은 개인 장기 취향이 아니라 `group_menu_actions`에 그룹 맥락 로그로 남깁니다.

가정(Assumption):

- 그룹 추천 진행 중 세션은 `started_at + 24h` 기준으로 만료되며, 별도 scheduler 없이 API 접근 시 lazy expire 처리합니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `group_recommendations` | 그룹 추천 세션 | `GroupRecommendation`, `01-schema.sql` |
| `group_recommendation_readiness` | 준비 단계의 멤버별 준비 상태 | `GroupRecommendationReadiness`, JPA only |
| `group_recommendation_candidates` | 그룹 추천 후보 메뉴 | `GroupRecommendationCandidate`, `01-schema.sql` |
| `group_recommendation_votes` | 그룹 추천 투표 | `GroupRecommendationVote`, `01-schema.sql` |
| `group_menu_actions` | 그룹 맥락 메뉴 행동 로그 | `GroupMenuAction`, `01-schema.sql` |

## `group_recommendations`

### 역할

- 그룹 방에서 실행된 추천 세션의 상태, 시작/종료 시각, 컨텍스트, 최종 선택 후보를 저장합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 추천 ID |
| `room_id` | bigint | N |  | FK | 그룹 방 ID |
| `status` | varchar(30) | N |  | enum | 그룹 추천 상태 |
| `started_at` | datetime | N |  |  | 시작 시각 |
| `ended_at` | datetime | Y |  |  | 종료 시각 |
| `selected_candidate_id` | bigint | Y |  | FK | 최종 선택 후보 ID |
| `context_json` | json | Y |  | JSON | 그룹 추천 컨텍스트 스냅샷 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 그룹 추천 식별자 |
| FK | `fk_group_recommendations_room` | `room_id -> group_rooms.id` | 추천 대상 그룹 방 |
| FK | `fk_group_recommendations_selected_candidate` | `selected_candidate_id -> group_recommendation_candidates.id` | 최종 선택 후보 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_group_recommendations_room` | `room_id` | 그룹별 추천 조회 | `01-schema.sql` |
| `idx_group_recommendations_selected_candidate` | `selected_candidate_id` | 선택 후보 역조회 | `01-schema.sql` |

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `status` | `PREPARING` | 멤버 준비 단계 |
| `status` | `OPEN` | 후보/투표 진행 |
| `status` | `FINALIZED` | 최종 후보 확정 |
| `status` | `REROLLED_WITH_SKIP` | 후보 제외 후 재요청 |
| `status` | `REROLLED_WITHOUT_SKIP` | 후보 제외 없이 재요청 |
| `status` | `CANCELED` | 취소 |
| `status` | `EXPIRED` | 만료 |
| `status` | `FAILED` | 실패 |

## `group_recommendation_readiness`

### 역할

- `PREPARING` 단계에서 추천 세션별/회원별 준비 완료 또는 취소 상태를 저장합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 준비 상태 ID |
| `group_recommendation_id` | bigint | N |  | FK, unique 조합 | 그룹 추천 ID |
| `member_id` | bigint | N |  | FK, unique 조합 | 회원 ID |
| `status` | varchar(20) | N | `READY` | enum | 준비 상태 |
| `created_at` | datetime | N |  | auditing | 생성 일시 |
| `updated_at` | datetime | N |  | auditing | 수정 일시 |

이 테이블은 JPA Entity에는 존재하지만 `backend/init/sql/01-schema.sql` 생성문이 없습니다.

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 준비 상태 식별자 |
| FK | 미정 | `group_recommendation_id -> group_recommendations.id` | 부모 추천 |
| FK | 미정 | `member_id -> members.id` | 준비 회원 |
| unique | `uk_group_recommendation_readiness_recommendation_member` | `group_recommendation_id`, `member_id` | 세션별 회원 준비 row 1개 유지 |

### 인덱스

- init SQL 테이블 생성문이 없어 명시 보조 인덱스도 아직 없습니다.
- 추가 시 `group_recommendation_id`, `member_id` 조회 패턴을 기준으로 검토합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `status` | `READY` | 준비 완료 |
| `status` | `CANCELED` | 준비 취소 |

## `group_recommendation_candidates`

### 역할

- 그룹 추천 세션에서 제시된 후보 메뉴를 저장합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 추천 후보 ID |
| `group_recommendation_id` | bigint | N |  | FK, unique 조합 | 그룹 추천 ID |
| `menu_id` | bigint | N |  | FK, unique 조합 | 후보 메뉴 ID |
| `rank_no` | int | N |  |  | 후보 순위 |
| `score` | double | N |  |  | 0~100 정규화 추천 점수 |
| `candidate_meta_json` | json | Y |  | JSON | 후보 메타데이터 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 후보 식별자 |
| FK | `fk_group_recommendation_candidates_recommendation` | `group_recommendation_id -> group_recommendations.id` | 부모 추천 |
| FK | `fk_group_recommendation_candidates_menu` | `menu_id -> menu_items.id` | 후보 메뉴 |
| unique | `uk_group_recommendation_candidate_menu` | `group_recommendation_id`, `menu_id` | 같은 추천 안에서 같은 메뉴 중복 방지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_group_recommendation_candidates_menu` | `menu_id` | 메뉴 기준 후보 조회 | `01-schema.sql` |

## `group_recommendation_votes`

### 역할

- 그룹 추천 후보에 대한 회원 투표를 저장합니다.
- 재투표 시 같은 세션/회원 row의 `candidate_id`를 변경합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 추천 투표 ID |
| `group_recommendation_id` | bigint | N |  | FK, unique 조합 | 그룹 추천 ID |
| `candidate_id` | bigint | N |  | FK | 후보 ID |
| `member_id` | bigint | N |  | FK, unique 조합 | 투표 회원 ID |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | JPA `BaseEntity`, init SQL 누락 | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 투표 식별자 |
| FK | `fk_group_recommendation_votes_recommendation` | `group_recommendation_id -> group_recommendations.id` | 부모 추천 |
| FK | `fk_group_recommendation_votes_candidate` | `candidate_id -> group_recommendation_candidates.id` | 투표 후보 |
| FK | `fk_group_recommendation_votes_member` | `member_id -> members.id` | 투표 회원 |
| unique | `uk_group_recommendation_vote_member` | `group_recommendation_id`, `member_id` | 세션별 회원 투표 row 1개 유지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_group_recommendation_votes_candidate` | `candidate_id` | 후보별 투표 집계 | `01-schema.sql` |
| `idx_group_recommendation_votes_member` | `member_id` | 회원별 투표 조회 | `01-schema.sql` |

## `group_menu_actions`

### 역할

- 그룹 추천 맥락에서 거절되거나 제외된 메뉴 행동을 저장합니다.
- 개인 장기 취향이 아니라 해당 그룹 추천 맥락의 의사결정 로그입니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 메뉴 행동 로그 ID |
| `group_room_id` | bigint | N |  | FK | 그룹 방 ID |
| `group_recommendation_id` | bigint | N |  | FK, unique 조합 | 그룹 추천 ID |
| `actor_member_id` | bigint | N |  | FK | 행동 발생 회원 ID |
| `menu_id` | bigint | N |  | FK, unique 조합 | 메뉴 ID |
| `action_type` | varchar(20) | N |  | enum, unique 조합 | 행동 유형 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |

`group_menu_actions`는 `CreatedAtEntity`를 사용하므로 `updated_at`이 없습니다.

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 행동 로그 식별자 |
| FK | `fk_group_menu_actions_room` | `group_room_id -> group_rooms.id` | 그룹 방 |
| FK | `fk_group_menu_actions_recommendation` | `group_recommendation_id -> group_recommendations.id` | 그룹 추천 |
| FK | `fk_group_menu_actions_actor_member` | `actor_member_id -> members.id` | 행동 회원 |
| FK | `fk_group_menu_actions_menu` | `menu_id -> menu_items.id` | 대상 메뉴 |
| unique | `uk_group_menu_action_recommendation_menu_type` | `group_recommendation_id`, `menu_id`, `action_type` | 같은 추천/메뉴/action 중복 로그 방지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_group_menu_actions_room` | `group_room_id` | 그룹별 행동 조회 | `01-schema.sql` |
| `idx_group_menu_actions_actor_member` | `actor_member_id` | 회원별 행동 조회 | `01-schema.sql` |
| `idx_group_menu_actions_menu` | `menu_id` | 메뉴별 행동 조회 | `01-schema.sql` |

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `action_type` | `SKIP` | 그룹 추천 후보 제외 |

## 관계

| 기준 | 대상 | 관계 | 설명 |
| --- | --- | --- | --- |
| `group_recommendations.room_id` | `group_rooms.id` | N : 1 | 추천 대상 그룹 방 |
| `group_recommendation_readiness.group_recommendation_id` | `group_recommendations.id` | N : 1 | 준비 상태 |
| `group_recommendation_candidates.group_recommendation_id` | `group_recommendations.id` | N : 1 | 후보 |
| `group_recommendation_votes.group_recommendation_id` | `group_recommendations.id` | N : 1 | 투표 |
| `group_recommendation_votes.candidate_id` | `group_recommendation_candidates.id` | N : 1 | 선택 후보 |
| `group_menu_actions.group_recommendation_id` | `group_recommendations.id` | N : 1 | 그룹 맥락 행동 로그 |

## 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 | 주의점 |
| --- | --- | --- | --- |
| 추천 준비 시작 | `room_id` | `PREPARING` 추천 생성 | 진행 중 추천 중복 여부 확인 |
| 준비 완료 | `group_recommendation_id`, `member_id` | readiness row 생성/갱신 | init SQL 테이블 누락 주의 |
| 후보 생성 | `group_recommendation_id` | 후보 row 저장 후 `OPEN` 전환 | 후보 메뉴 중복 방지 |
| 투표 | `group_recommendation_id`, `member_id` | 없으면 insert, 있으면 후보 변경 | 추천 상태 `OPEN` 확인 |
| 최종 확정 | `group_recommendation_id`, `candidate_id` | `FINALIZED`, `selected_candidate_id`, `ended_at` 갱신 | 동률/권한 정책 확인 |
| 재요청 | 기존 추천 ID | 기존 추천 종료 후 새 추천 생성 | `NOT_SATISFIED`는 skip 로그 저장 |

## 운영 기준

- `PREPARING`, `OPEN` 세션은 `started_at + 24h` 기준으로 만료 처리합니다.
- `PREPARING` 상태에서는 후보 생성 기준이 확정되지 않았으면 `context_json`을 `null`로 둘 수 있습니다.
- `OPEN` 전환 시 확정 컨텍스트 스냅샷을 `context_json`에 기록합니다.
- 그룹 추천 투표는 세션별/회원별 1개 row를 유지합니다.
- 그룹 후보 거절 로그는 `group_menu_actions`에 저장하며 개인 취향으로 바로 승격하지 않습니다.

## 현재 제외 범위

- 다중 투표권/가중 투표
- 투표 이력 테이블
- 자동 배치 만료 처리
- 장소/가게 최종 선택 저장

## 코드 변경 시 확인할 것

- `GroupRecommendationStatus` 추가 시 상태 전이, 만료 처리, API 응답을 함께 확인합니다.
- `group_recommendation_readiness`를 운영 DB bootstrap에 반영해야 합니다.
- `group_recommendation_votes.updated_at`을 init SQL과 맞춰야 합니다.
- 투표 정책 변경 시 unique 제약과 재투표 write path를 확인합니다.

## 함께 볼 문서

- [그룹 방 테이블 정의서](./group-rooms-schema.md)
- [메뉴 카탈로그 테이블 정의서](./menu-catalog-schema.md)
- [회원 테이블 정의서](./members-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
