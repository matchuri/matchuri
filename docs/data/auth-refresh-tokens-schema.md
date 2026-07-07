# 인증 refresh token 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: auth
- 기준 소스:
  - JPA Entity: `AuthRefreshToken`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: 인증 API 문서

## 기준 소스 우선순위

1. JPA Entity
2. `backend/init/sql/01-schema.sql`
3. 인증 service write path와 repository query
4. 관련 API 문서

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- `auth_refresh_tokens` 테이블의 현재 컬럼, 제약, 운영 기준을 정의합니다.
- access token 재발급과 로그아웃에서 refresh token을 서버 저장소로 관리하는 기준을 설명합니다.

## 현재 확정 전제

- refresh token은 서버 DB에 저장해 검증, 회전, 폐기를 제어합니다.
- 회원당 단일 token을 DB 제약으로 강제하지 않습니다.
- token 원문은 현재 컬럼에 저장되며, `token` unique 제약으로 중복을 막습니다.

가정(Assumption):

- token 해시 저장 전환은 별도 보안 개선 작업으로 검토합니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `auth_refresh_tokens` | refresh token 저장과 만료 관리 | `AuthRefreshToken`, `01-schema.sql` |

## `auth_refresh_tokens`

### 역할

- refresh token을 DB에 저장해 access token 재발급 근거로 사용합니다.
- 로그아웃 또는 token 회전 시 기존 refresh token 폐기를 가능하게 합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | refresh token ID |
| `member_id` | bigint | N |  | FK | 회원 ID |
| `token` | varchar(512) | N |  | unique | refresh token 문자열 |
| `expires_at` | datetime | N |  |  | 만료 시각 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | refresh token 식별자 |
| FK | `fk_auth_refresh_tokens_member` | `member_id -> members.id` | token 소유 회원 |
| unique | `uk_auth_refresh_tokens_token` | `token` | token 중복 저장 방지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_auth_refresh_tokens_member` | `member_id` | 회원 기준 token 조회/정리 | `01-schema.sql` |

### enum / 상태값

- 없음

### 관계

| 기준 | 대상 | 관계 | 설명 |
| --- | --- | --- | --- |
| `auth_refresh_tokens.member_id` | `members.id` | N : 1 | token 소유 회원 |

### 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 | 주의점 |
| --- | --- | --- | --- |
| token 검증 | `token` | token row 조회 후 만료 확인 | 만료 시 재발급 거절 |
| token 발급 | `member_id`, `token`, `expires_at` | 새 row 저장 | 회원당 다중 token 허용 |
| 로그아웃 | `token` 또는 `member_id` | 대상 token 삭제 | 클라이언트 재시도 고려 |

### 운영 기준

- 만료 판단은 `expires_at` 기준입니다.
- 회원당 단일 token을 강제하려면 서비스 정책과 unique 제약을 함께 재검토해야 합니다.

### 현재 제외 범위

- refresh token family / reuse detection
- token 해시 저장
- 기기별 세션 메타데이터

## 코드 변경 시 확인할 것

- token 저장 방식을 해시로 바꾸면 조회 기준, 길이, unique 제약, 보안 문서를 함께 갱신합니다.
- 회원당 단일 token 정책으로 바꾸면 `member_id` unique 여부와 로그아웃 동작을 확인합니다.

## 함께 볼 문서

- [회원 테이블 정의서](./members-schema.md)
- [인증 exchange code 테이블 정의서](./auth-exchange-codes-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
