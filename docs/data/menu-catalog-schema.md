# 메뉴 카탈로그 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: menu
- 기준 소스:
  - JPA Entity: `AttributeCategory`, `Ingredient`, `MenuItem`, `MenuAttributeCategory`, `MenuIngredient`, `MenuItemImage`, `CategoryType`, `MenuImageRole`
  - 관련 seed: `backend/src/main/resources/seed/reference-data.json`
  - seed loader: `ReferenceDataSeedService`
  - 관련 API 문서: 메뉴/참조 데이터 API 문서

## 기준 소스 우선순위

1. JPA Entity와 enum
2. 메뉴 service write path와 repository query
3. `backend/src/main/resources/seed/reference-data.json`
4. 관련 API 문서

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- 메뉴 추천의 기준 데이터인 메뉴, 속성 카테고리, 재료, 매핑 테이블을 정의합니다.
- 회원 취향과 메뉴 특성이 같은 마스터를 공유하는 기준을 설명합니다.
- 메뉴 대표 이미지 연결은 이 문서에서 관계만 설명하고, 이미지 자산 세부 운영은 `images-schema.md`를 봅니다.

## 현재 확정 전제

- Matchuri의 추천 단위는 장소가 아니라 `menu_items`입니다.
- 메뉴 특성과 회원 취향은 `attribute_categories`를 공유합니다.
- 제한 재료와 메뉴 구성 재료는 `ingredients`를 공유합니다.
- `attribute_categories`, `ingredients`, `menu_items`는 삭제보다 비활성화를 우선합니다.
- 기준 seed는 속성, 재료, 메뉴와 매핑을 준비하며 기존 row를 수정하거나 삭제하지 않습니다.
- 메뉴 대표 이미지와 `menu_item_images` 연결은 seed 범위에서 제외합니다.

가정(Assumption):

- 대량 메뉴 카탈로그 운영이나 외부 장소 데이터 연동은 현재 범위가 아닙니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `attribute_categories` | 메뉴 특성과 회원 취향이 공유하는 속성 마스터 | `AttributeCategory` |
| `ingredients` | 메뉴 재료와 회원 제한 재료가 공유하는 재료 마스터 | `Ingredient` |
| `menu_items` | 추천 가능한 메뉴 단위 | `MenuItem` |
| `menu_attribute_categories` | 메뉴-속성 N:M 매핑 | `MenuAttributeCategory` |
| `menu_ingredients` | 메뉴-재료 N:M 매핑 | `MenuIngredient` |
| `menu_item_images` | 메뉴 대표 이미지 연결 | `MenuItemImage` |

## `attribute_categories`

### 역할

- 맛, 조리 방식, 음식 분류, 식감, 온도 같은 공통 속성 카테고리를 저장합니다.
- 회원 취향 선택과 메뉴 특성 연결이 같은 row를 참조합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 속성 카테고리 ID |
| `category_type` | varchar(30) | N |  | enum, unique 조합 | 카테고리 유형 |
| `code` | varchar(50) | N |  | unique 조합 | 안정적인 카테고리 코드 |
| `name` | varchar(100) | N |  |  | 표시명 |
| `sort_order` | int | N |  |  | 정렬 순서 |
| `is_active` | bit(1) / boolean | N | `true` |  | 활성 여부 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 속성 카테고리 식별자 |
| unique | `uk_attribute_categories_type_code` | `category_type`, `code` | 유형 안에서 코드 중복 방지 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `category_type` | `FLAVOR` | 맛 |
| `category_type` | `COOKING_METHOD` | 조리 방식 |
| `category_type` | `FOOD_CATEGORY` | 음식 분류 |
| `category_type` | `TEXTURE` | 식감 |
| `category_type` | `TEMPERATURE` | 온도 |

## `ingredients`

### 역할

- 메뉴 구성 재료와 회원 제한 재료 입력의 기준 마스터입니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 재료 ID |
| `code` | varchar(50) | N |  | unique | 재료 코드 |
| `name` | varchar(100) | N |  |  | 재료명 |
| `is_allergen` | bit(1) / boolean | N |  |  | 알레르기 유발 여부 |
| `sort_order` | int | N |  |  | 정렬 순서 |
| `is_active` | bit(1) / boolean | N | `true` |  | 활성 여부 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 재료 식별자 |
| unique | `uk_ingredients_code` | `code` | 재료 코드 중복 방지 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

## `menu_items`

### 역할

- 추천, 후보, 투표, 비선호가 참조하는 메뉴의 기본 단위입니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 메뉴 ID |
| `code` | varchar(50) | N |  | unique | 메뉴 코드 |
| `name` | varchar(120) | N |  |  | 메뉴명 |
| `description` | varchar(500) | Y |  |  | 메뉴 설명 |
| `is_active` | bit(1) / boolean | N | `true` |  | 활성 여부 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 메뉴 식별자 |
| unique | `uk_menu_items_code` | `code` | 메뉴 코드 중복 방지 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

## `menu_attribute_categories`

### 역할

- 메뉴와 속성 카테고리를 N:M으로 연결합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 매핑 ID |
| `menu_id` | bigint | N |  | FK, unique 조합 | 메뉴 ID |
| `attribute_category_id` | bigint | N |  | FK, unique 조합 | 속성 카테고리 ID |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 매핑 식별자 |
| FK | `fk_menu_attribute_categories_menu` | `menu_id -> menu_items.id` | 메뉴 |
| FK | `fk_menu_attribute_categories_category` | `attribute_category_id -> attribute_categories.id` | 속성 |
| unique | `uk_menu_attribute_category` | `menu_id`, `attribute_category_id` | 같은 메뉴-속성 중복 연결 방지 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

## `menu_ingredients`

### 역할

- 메뉴와 재료를 N:M으로 연결합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 매핑 ID |
| `menu_id` | bigint | N |  | FK, unique 조합 | 메뉴 ID |
| `ingredient_id` | bigint | N |  | FK, unique 조합 | 재료 ID |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 매핑 식별자 |
| FK | `fk_menu_ingredients_menu` | `menu_id -> menu_items.id` | 메뉴 |
| FK | `fk_menu_ingredients_ingredient` | `ingredient_id -> ingredients.id` | 재료 |
| unique | `uk_menu_ingredient` | `menu_id`, `ingredient_id` | 같은 메뉴-재료 중복 연결 방지 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

## `menu_item_images`

### 역할

- 메뉴와 이미지 자산을 연결합니다.
- MVP에서는 메뉴당 대표 이미지 1장만 허용합니다.
- 이미지 자산 컬럼과 파일 운영 기준은 [이미지 자산 테이블 정의서](./images-schema.md)를 봅니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 메뉴 이미지 ID |
| `menu_id` | bigint | N |  | FK, unique | 메뉴 ID |
| `image_asset_id` | bigint | N |  | FK | 이미지 자산 ID |
| `image_role` | varchar(20) | N | `PRIMARY` | enum | 이미지 역할 |
| `sort_order` | int | N | 0 |  | 정렬 순서 |
| `is_primary` | bit(1) / boolean | N | `true` |  | 대표 이미지 여부 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 메뉴 이미지 식별자 |
| FK | `fk_menu_item_images_menu` | `menu_id -> menu_items.id` | 연결 메뉴 |
| FK | `fk_menu_item_images_image_asset` | `image_asset_id -> image_assets.id` | 이미지 자산 |
| unique | `uk_menu_item_images_menu` | `menu_id` | 메뉴당 대표 이미지 1장 강제 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 메뉴 대표 이미지는 seed로 생성하지 않습니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `image_role` | `PRIMARY` | 대표 이미지 |

## 영역 공통 판단

- 마스터 데이터는 삭제보다 `is_active=false`를 우선합니다.
- public 메뉴 조회와 취향 입력 검증은 활성 기준 데이터를 대상으로 합니다.
- 관리자 메뉴 연결 수정은 최신 입력 기준 전체 교체 방식입니다.
- `code`는 표시명 변경과 무관한 안정적인 비즈니스 키입니다.

## 코드 변경 시 확인할 것

- `CategoryType` 추가 시 seed, 참조 데이터 API, 취향 입력 UI 계약을 함께 확인합니다.
- 메뉴/속성/재료 마스터 컬럼 변경 시 `reference-data.json`, seed loader, 관리자 API 문서를 함께 갱신합니다.
- 메뉴 이미지 정책 변경 시 `images-schema.md`와 응답의 `thumbnailUrl` 생성 로직을 확인합니다.

## 함께 볼 문서

- [회원 취향 프로필 테이블 정의서](./member-taste-profiles-schema.md)
- [이미지 자산 테이블 정의서](./images-schema.md)
- [개인 추천 테이블 정의서](./personal-recommendations-schema.md)
- [그룹 추천 테이블 정의서](./group-recommendations-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
