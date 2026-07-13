# 회원 개인 위치 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-13
- 담당 영역: member
- 기준 소스:
  - JPA Entity: `MemberLocation`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: `docs/api/member-profile.md`

## 현재 확정 전제

- 회원은 개인 위치를 최대 1개 저장합니다.
- 위치가 없는 회원도 허용하므로 관계는 `members 1 : member_locations 0..1`입니다.
- 저장된 위치는 현재 개인 추천에 자동 적용하지 않습니다.
- 위치 삭제와 변경 이력은 현재 범위에 포함하지 않습니다.

## `member_locations`

### 역할

- 회원이 선택한 개인 추천 기준 위치를 저장합니다.
- PUT API는 최초 생성과 기존 row 전체 교체를 동일한 자원으로 처리합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 회원 개인 위치 ID |
| `member_id` | bigint | N |  | FK, unique | 위치 소유 회원 ID |
| `latitude` | decimal(10,7) | N |  | -90 이상 90 이하를 API에서 검증 | 위도 |
| `longitude` | decimal(10,7) | N |  | -180 이상 180 이하를 API에서 검증 | 경도 |
| `radius_meters` | int | N |  | 0 이상을 API에서 검증 | 반경 거리(미터) |
| `address` | varchar(255) | N |  | blank 불가, 앞뒤 공백 제거 | 주소 문자열 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 회원 개인 위치 식별자 |
| FK | `fk_member_locations_member` | `member_id -> members.id` | 위치 소유 회원 |
| unique | `uk_member_locations_member` | `member_id` | 회원당 위치 최대 1개 강제 |

### 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 |
| --- | --- | --- |
| 내 위치 조회 | `member_id` | 인증 회원 ID로 단건 조회, 없으면 `MEMBER_LOCATION_NOT_FOUND` |
| 내 위치 최초 PUT | `member_id` | 새 row 생성 |
| 내 위치 재 PUT | `member_id` | 기존 row의 네 위치 필드를 전체 교체 |

## 함께 볼 문서

- [회원 테이블 정의서](./members-schema.md)
- [회원 프로필 API](../api/member-profile.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)
