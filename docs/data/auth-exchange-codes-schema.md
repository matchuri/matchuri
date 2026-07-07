# 인증 exchange code 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: auth
- 기준 소스:
  - JPA Entity: `AuthExchangeCode`, `SocialProviderType`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: OAuth2 인증 API 문서

## 기준 소스 우선순위

1. JPA Entity와 enum
2. `backend/init/sql/01-schema.sql`
3. OAuth2 login / exchange service flow
4. 관련 API 문서

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- `auth_exchange_codes` 테이블의 현재 컬럼, 제약, 일회성 code 소비 기준을 정의합니다.
- OAuth2 로그인 직후 프론트엔드가 서버 token으로 교환하는 임시 code와 refresh token의 역할 차이를 설명합니다.

## 현재 확정 전제

- exchange code는 OAuth2 로그인 완료 후 짧은 시간 동안만 유효한 일회성 code입니다.
- code 원문은 현재 DB에 저장되며, `code` unique 제약으로 중복을 막습니다.
- 사용 완료 시 `used_at`을 기록합니다.
- `provider`는 `SocialProviderType` 문자열 enum을 사용합니다.

가정(Assumption):

- exchange code 해시 저장 전환은 별도 보안 개선 작업으로 검토합니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `auth_exchange_codes` | OAuth2 로그인 후 token 교환용 일회성 code 저장 | `AuthExchangeCode`, `01-schema.sql` |

## `auth_exchange_codes`

### 역할

- OAuth2 인증 완료 후 프론트엔드가 access/refresh token으로 교환할 code를 저장합니다.
- code 만료와 사용 여부를 서버가 검증할 수 있게 합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | exchange code ID |
| `member_id` | bigint | N |  | FK | 회원 ID |
| `provider` | varchar(20) | N |  | enum | 소셜 제공자 |
| `code` | varchar(128) | N |  | unique | 교환용 code |
| `expires_at` | datetime | N |  |  | 만료 시각 |
| `used_at` | datetime | Y |  |  | 사용 완료 시각 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | exchange code 식별자 |
| FK | `fk_auth_exchange_codes_member` | `member_id -> members.id` | code 소유 회원 |
| unique | `uk_auth_exchange_codes_code` | `code` | code 중복 방지 |

### 인덱스

| 이름 | 컬럼 | 목적 | 기준 소스 |
| --- | --- | --- | --- |
| `idx_auth_exchange_codes_member` | `member_id` | 회원 기준 code 조회/정리 | `01-schema.sql` |

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `provider` | `GOOGLE` | Google OAuth2 제공자 |
| `provider` | `KAKAO` | Kakao OAuth2 제공자 |
| `provider` | `NAVER` | Naver OAuth2 제공자 |

### 관계

| 기준 | 대상 | 관계 | 설명 |
| --- | --- | --- | --- |
| `auth_exchange_codes.member_id` | `members.id` | N : 1 | code 소유 회원 |

### 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 | 주의점 |
| --- | --- | --- | --- |
| code 발급 | `member_id`, `provider`, `code`, `expires_at` | 새 code row 저장 | 짧은 만료 시간 유지 |
| code 소비 | `code` | row 조회 후 만료/사용 여부 확인 | 성공 시 `used_at` 기록 |

### 운영 기준

- `expires_at`이 현재 시각보다 과거이면 소비를 거절합니다.
- `used_at`이 존재하면 재사용을 거절합니다.
- refresh token은 `auth_refresh_tokens`에 별도로 저장합니다.

### 현재 제외 범위

- exchange code 해시 저장
- provider별 별도 exchange code 테이블
- 사용 완료 code 정리 배치

## 코드 변경 시 확인할 것

- `SocialProviderType` 값이나 OAuth2 지원 범위가 바뀌면 회원 문서와 인증 API 문서를 함께 갱신합니다.
- code 발급/소비 정책이 바뀌면 만료 시간, 재사용 방지, 보안 로그 정책을 확인합니다.

## 함께 볼 문서

- [회원 테이블 정의서](./members-schema.md)
- [인증 refresh token 테이블 정의서](./auth-refresh-tokens-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
