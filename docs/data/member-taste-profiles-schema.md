# 회원 취향 프로필 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: member
- 기준 소스:
  - JPA Entity: `MemberTasteProfile`, `MemberTasteProfileCategory`, `MemberTasteProfileRestrictionIngredient`, `MemberTasteProfileDislikedMenuItem`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: 취향 프로필 API 문서

## 기준 소스 우선순위

1. JPA Entity
2. `backend/init/sql/01-schema.sql`
3. 취향 저장 service write path와 repository query
4. 관련 API 문서
5. 기존 `docs/data/`

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- 회원 취향 프로필 헤더와 하위 매핑 테이블의 현재 구조를 정의합니다.
- 메뉴 카탈로그 마스터와 취향 입력 데이터가 어떻게 연결되는지 설명합니다.

## 현재 확정 전제

- 회원당 취향 프로필은 최대 1개입니다.
- 취향 상세는 JSON이 아니라 속성 카테고리, 제한 재료, 비선호 메뉴 매핑 테이블로 저장합니다.
- 회원 취향 속성과 메뉴 특성은 `attribute_categories`를 공유합니다.
- 제한 재료와 메뉴 재료는 `ingredients`를 공유합니다.
- 비선호 메뉴는 자유 텍스트가 아니라 `menu_items` 기준으로 저장합니다.

가정(Assumption):

- 현재는 취향 변경 이력과 취향 가중치 테이블을 두지 않습니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `member_taste_profiles` | 회원 취향 프로필 헤더 | `MemberTasteProfile`, `01-schema.sql` |
| `member_taste_profile_categories` | 선호 속성 카테고리 매핑 | `MemberTasteProfileCategory`, `01-schema.sql` |
| `member_taste_profile_restriction_ingredients` | 제한 재료 매핑 | `MemberTasteProfileRestrictionIngredient`, `01-schema.sql` |
| `member_taste_profile_disliked_menu_items` | 비선호 메뉴 매핑 | `MemberTasteProfileDislikedMenuItem`, `01-schema.sql` |

## `member_taste_profiles`

### 역할

- 회원 취향 프로필 존재 여부와 프로필 구조 버전을 저장합니다.
- 하위 취향 매핑 테이블의 부모 row입니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 취향 프로필 ID |
| `member_id` | bigint | N |  | FK, unique | 회원 ID |
| `profile_version` | varchar(20) | N |  |  | 프로필 구조 버전 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 취향 프로필 식별자 |
| FK | `fk_member_taste_profiles_member` | `member_id -> members.id` | 프로필 소유 회원 |
| unique | `uk_member_taste_profiles_member` | `member_id` | 회원당 프로필 1개 강제 |

### 인덱스

- 현재 명시 보조 인덱스 없음

### enum / 상태값

- 없음

### 관계

| 기준 | 대상 | 관계 | 설명 |
| --- | --- | --- | --- |
| `member_taste_profiles.member_id` | `members.id` | 1 : 1 | 프로필 소유 회원 |
| `member_taste_profiles.id` | `member_taste_profile_categories.profile_id` | 1 : N | 선호 속성 |
| `member_taste_profiles.id` | `member_taste_profile_restriction_ingredients.profile_id` | 1 : N | 제한 재료 |
| `member_taste_profiles.id` | `member_taste_profile_disliked_menu_items.profile_id` | 1 : N | 비선호 메뉴 |

## `member_taste_profile_categories`

### 역할

- 취향 프로필과 선호 `attribute_categories`를 연결합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 매핑 ID |
| `profile_id` | bigint | N |  | FK, unique 조합 | 취향 프로필 ID |
| `attribute_category_id` | bigint | N |  | FK, unique 조합 | 속성 카테고리 ID |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 매핑 식별자 |
| FK | `fk_member_taste_profile_categories_profile` | `profile_id -> member_taste_profiles.id` | 부모 프로필 |
| FK | `fk_member_taste_profile_categories_category` | `attribute_category_id -> attribute_categories.id` | 선호 속성 |
| unique | `uk_member_taste_profile_category` | `profile_id`, `attribute_category_id` | 같은 속성 중복 선택 방지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_member_taste_profile_categories_category` | `attribute_category_id` | 속성 기준 역조회 | `01-schema.sql` |

## `member_taste_profile_restriction_ingredients`

### 역할

- 취향 프로필과 피하고 싶은 `ingredients`를 연결합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 매핑 ID |
| `profile_id` | bigint | N |  | FK, unique 조합 | 취향 프로필 ID |
| `ingredient_id` | bigint | N |  | FK, unique 조합 | 제한 재료 ID |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 매핑 식별자 |
| FK | `fk_member_taste_profile_restriction_ingredients_profile` | `profile_id -> member_taste_profiles.id` | 부모 프로필 |
| FK | `fk_member_taste_profile_restriction_ingredients_ingredient` | `ingredient_id -> ingredients.id` | 제한 재료 |
| unique | `uk_member_profile_restriction_ingredient` | `profile_id`, `ingredient_id` | 같은 재료 중복 선택 방지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_member_taste_profile_restriction_ingredients_ingredient` | `ingredient_id` | 재료 기준 역조회 | `01-schema.sql` |

## `member_taste_profile_disliked_menu_items`

### 역할

- 취향 프로필과 비선호 `menu_items`를 연결합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 매핑 ID |
| `profile_id` | bigint | N |  | FK, unique 조합 | 취향 프로필 ID |
| `menu_id` | bigint | N |  | FK, unique 조합 | 비선호 메뉴 ID |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 매핑 식별자 |
| FK | `fk_member_taste_profile_disliked_menu_items_profile` | `profile_id -> member_taste_profiles.id` | 부모 프로필 |
| FK | `fk_member_taste_profile_disliked_menu_items_menu` | `menu_id -> menu_items.id` | 비선호 메뉴 |
| unique | `uk_member_profile_disliked_menu_item` | `profile_id`, `menu_id` | 같은 메뉴 중복 선택 방지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_member_taste_profile_disliked_menu_items_menu` | `menu_id` | 메뉴 기준 역조회 | `01-schema.sql` |

## 영역 공통 판단

- 프로필 저장/수정은 현재 입력 기준으로 하위 매핑을 동기화합니다.
- `profile_version`은 사용자 입력 변경 횟수가 아니라 서버가 관리하는 프로필 구조 버전입니다.
- 활성 기준 데이터 검증은 메뉴 카탈로그 마스터 기준을 따릅니다.

## 코드 변경 시 확인할 것

- 취향 입력 항목이 늘어나면 새 매핑 테이블이 필요한지, 기존 마스터를 공유할 수 있는지 확인합니다.
- `profile_version` 의미가 바뀌면 API 응답과 저장 로직을 함께 갱신합니다.
- 추천 후보 제외 조건 변경 시 비선호 메뉴와 제한 재료 사용 범위를 확인합니다.

## 함께 볼 문서

- [회원 테이블 정의서](./members-schema.md)
- [메뉴 카탈로그 테이블 정의서](./menu-catalog-schema.md)
- [개인 추천 테이블 정의서](./personal-recommendations-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
