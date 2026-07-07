# 이미지 자산 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: image
- 기준 소스:
  - JPA Entity: `ImageAsset`, `ImageStorageProvider`, `ImageAssetStatus`, `MenuItemImage`, `MenuImageRole`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: 메뉴 이미지 업로드 API 문서

## 기준 소스 우선순위

1. JPA Entity와 enum
2. `backend/init/sql/01-schema.sql`
3. 이미지 업로드 service write path
4. 관련 API 문서

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- R2 이미지 객체 메타데이터를 저장하는 `image_assets`와 메뉴 이미지 연결 기준을 정의합니다.
- 파일 정책과 DB 저장/교체 운영 기준을 코드 구현자가 빠르게 확인할 수 있게 합니다.

## 현재 확정 전제

- 현재 저장소 제공자는 Cloudflare R2입니다.
- 현재 구현 범위는 메뉴 대표 이미지 1장입니다.
- `image_assets`는 범용 이미지 자산 테이블이며 메뉴 전용 이름을 쓰지 않습니다.
- 메뉴 대표 이미지 연결은 `menu_item_images`에서 관리합니다.

가정(Assumption):

- 회원 프로필 이미지, 장소 이미지, 썸네일 파생 파일은 현재 범위가 아닙니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `image_assets` | 업로드된 이미지 객체 메타데이터 | `ImageAsset`, `01-schema.sql` |
| `menu_item_images` | 메뉴와 이미지 자산 연결 | `MenuItemImage`, `01-schema.sql` |

## `image_assets`

### 역할

- R2에 저장된 이미지 객체의 bucket, object key, content type, checksum, 크기, 상태를 저장합니다.
- 메뉴 이미지 교체나 삭제 실패 추적의 기준 row가 됩니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 이미지 자산 ID |
| `storage_provider` | varchar(30) | N |  | enum | 저장소 제공자 |
| `bucket` | varchar(100) | N |  |  | bucket 이름 |
| `object_key` | varchar(512) | N |  | unique | 객체 키 |
| `original_filename` | varchar(255) | Y |  |  | 업로드 원본 파일명 |
| `content_type` | varchar(50) | N |  |  | MIME type |
| `content_length` | bigint | N |  |  | 파일 크기 |
| `checksum` | varchar(64) | N |  |  | SHA-256 checksum |
| `width` | int | N |  |  | 이미지 너비 |
| `height` | int | N |  |  | 이미지 높이 |
| `status` | varchar(20) | N | `ACTIVE` | enum | 이미지 상태 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 이미지 자산 식별자 |
| unique | `uk_image_assets_object_key` | `object_key` | R2 객체 키 중복 방지 |

### 인덱스

- 현재 명시 보조 인덱스 없음

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `storage_provider` | `CLOUDFLARE_R2` | Cloudflare R2 |
| `status` | `ACTIVE` | 사용 중 |
| `status` | `DELETED` | 삭제 처리됨 |

### 관계

| 기준 | 대상 | 관계 | 설명 |
| --- | --- | --- | --- |
| `image_assets.id` | `menu_item_images.image_asset_id` | 1 : 0..1 | 메뉴 대표 이미지 연결 |

## `menu_item_images`

### 역할

- 메뉴와 이미지 자산을 연결합니다.
- 테이블 컬럼/제약은 [메뉴 카탈로그 테이블 정의서](./menu-catalog-schema.md)에도 함께 설명합니다.

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
| FK | `fk_menu_item_images_image_asset` | `image_asset_id -> image_assets.id` | 연결 이미지 자산 |
| unique | `uk_menu_item_images_menu` | `menu_id` | 메뉴당 대표 이미지 1장 강제 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_menu_item_images_image_asset` | `image_asset_id` | 이미지 자산 기준 역조회 | `01-schema.sql` |

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `image_role` | `PRIMARY` | 대표 이미지 |

## 파일 정책

- 허용 MIME type: `image/jpeg`, `image/png`, `image/webp`
- 최대 파일 크기: 5 MiB
- 해상도: 최소 300x300, 최대 4096x4096
- object key: `menu-items/{menuItemId}/{uuid}.{ext}`
- public URL base: `https://asset.matchuri.com`
- cache control: `public, max-age=604800`
- 썸네일 파일은 별도로 생성하지 않고 응답의 `thumbnailUrl`에는 원본 이미지 URL을 넣습니다.

## 운영 기준

- R2 bucket은 현재 `matchuri-image-bucket`을 사용합니다.
- local/dev도 실제 R2를 사용합니다.
- DB 저장 실패 시 방금 업로드한 R2 객체는 best-effort로 삭제합니다.
- 이미지 교체 시 기존 R2 객체는 트랜잭션 커밋 이후 best-effort로 삭제합니다.
- 기존 R2 객체 삭제 실패는 교체 성공을 되돌리지 않고 경고 로그로 남깁니다.

## 현재 제외 범위

- GIF, AVIF
- EXIF 제거와 이미지 재인코딩
- 썸네일 파생 파일 생성
- 환경별 bucket 분리

## 코드 변경 시 확인할 것

- 저장소 제공자를 추가하면 `ImageStorageProvider`, 업로드 service, 환경 변수를 함께 확인합니다.
- 파일 제한 정책을 바꾸면 API 검증, 에러 코드, 운영 문서를 함께 갱신합니다.
- 메뉴당 다중 이미지를 허용하면 `menu_item_images.menu_id` unique 제약을 재검토합니다.

## 함께 볼 문서

- [메뉴 카탈로그 테이블 정의서](./menu-catalog-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
