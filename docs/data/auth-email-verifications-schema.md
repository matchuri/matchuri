# 인증 이메일 검증 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: auth
- 기준 소스:
  - JPA Entity: `EmailVerification`, `EmailVerificationPurpose`, `EmailVerificationStatus`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: `docs/api/auth-email-verification.md`
  - 관련 설계 문서: `docs/decisions/email-verification-and-account-recovery.md`

## 기준 소스 우선순위

1. JPA Entity와 enum
2. `backend/init/sql/01-schema.sql`
3. 이메일 인증 service write path와 repository query
4. 관련 API 문서와 설계 문서

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- `auth_email_verifications` 테이블의 현재 컬럼, 제약, 보안 기준을 정의합니다.
- 회원가입, 로그인 ID 찾기, 비밀번호 재설정에서 공통으로 쓰는 이메일 소유 확인 구조를 설명합니다.

## 현재 확정 전제

- 인증 코드 원문과 verification token 원문은 DB에 저장하지 않고 해시를 저장합니다.
- 같은 이메일/목적의 재발송 이력을 보존할 수 있도록 이메일+목적 unique 제약은 두지 않습니다.
- 인증 성공 후 계정 복구 단계에서 사용할 verification token hash와 만료/사용 완료 시각을 저장합니다.

가정(Assumption):

- 초기에는 별도 정리 배치 없이 만료 여부를 요청 시점에 판단합니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `auth_email_verifications` | 이메일 인증 코드와 verification token 상태 저장 | `EmailVerification`, `01-schema.sql` |

## `auth_email_verifications`

### 역할

- 이메일 인증 코드 발급 이력을 저장합니다.
- 인증 코드 검증 상태, 실패 시도 횟수, 만료 시각을 관리합니다.
- 인증 성공 후 일회성 verification token 상태를 관리합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 이메일 인증 ID |
| `email` | varchar(150) | N |  |  | 인증 대상 이메일 |
| `login_id` | varchar(50) | Y |  |  | 비밀번호 재설정 목적에서 사용하는 로그인 ID |
| `purpose` | varchar(30) | N |  | enum | 인증 목적 |
| `code_hash` | varchar(255) | N |  |  | 인증 코드 해시 |
| `status` | varchar(20) | N |  | enum | 인증 상태 |
| `expires_at` | datetime | N |  |  | 인증 코드 만료 시각 |
| `verified_at` | datetime | Y |  |  | 인증 성공 시각 |
| `verification_token_hash` | varchar(255) | Y |  | unique | 인증 성공 후 발급 token 해시 |
| `verification_token_expires_at` | datetime | Y |  |  | verification token 만료 시각 |
| `verification_token_used_at` | datetime | Y |  |  | verification token 사용 완료 시각 |
| `attempt_count` | int | N | 0 |  | 검증 실패 시도 횟수 |
| `last_sent_at` | datetime | N |  |  | 마지막 발송 시각 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 이메일 인증 식별자 |
| unique | `uk_auth_email_verifications_token_hash` | `verification_token_hash` | verification token 중복 방지 |

### 인덱스

- 현재 명시 보조 인덱스 없음
- 이메일+목적 조회 성능이 문제가 되면 별도 작업으로 인덱스를 추가합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `purpose` | `SIGNUP` | 자체 회원가입 이메일 인증 |
| `purpose` | `FIND_LOGIN_ID` | 로그인 ID 찾기 |
| `purpose` | `RESET_PASSWORD` | 비밀번호 재설정 |
| `status` | `PENDING` | 발급 후 검증 대기 |
| `status` | `VERIFIED` | 검증 완료 |
| `status` | `EXPIRED` | 만료 또는 새 코드 발급으로 폐기 |
| `status` | `FAILED` | 시도 횟수 초과 또는 실패 처리 |

### 관계

- DB FK는 없습니다.
- `login_id`는 비밀번호 재설정 흐름에서 `members.login_id` 확인에 사용되는 loose reference입니다.
- 회원가입 이메일 중복 여부는 `members.email`과 서비스 계층에서 확인합니다.

### 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 | 주의점 |
| --- | --- | --- | --- |
| 인증 코드 발급 | `email`, `purpose`, `login_id` | 기존 `PENDING` row 만료 후 새 row 저장 | 재발송 이력 보존 |
| 인증 코드 확인 | 최신 `PENDING` row | code hash 비교, 실패 횟수 증가 | 성공 시 token hash 저장 |
| token 소비 | `verification_token_hash` | 만료/사용 여부 확인 후 사용 완료 기록 | token 원문은 응답 시 한 번만 제공 |

### 운영 기준

- 새 인증 코드를 발급할 때 같은 `email + purpose + login_id`의 기존 `PENDING` row는 `EXPIRED`로 바꿉니다.
- 인증 코드는 평문으로 저장하지 않습니다.
- verification token은 한 번 사용하면 `verification_token_used_at`을 기록하고 재사용을 거절합니다.
- 이메일과 인증 코드/token 원문은 로그에 남기지 않습니다.

### 현재 제외 범위

- 오래된 인증 이력 정리 배치
- 이메일/목적 단위 DB unique 제약
- 회원 FK 직접 연결

## 코드 변경 시 확인할 것

- `EmailVerificationPurpose` 추가 시 API 문서, service 분기, 보안 정책을 함께 확인합니다.
- 인증 코드 만료 시간, 최대 시도 횟수, token 만료 시간이 바뀌면 운영 기준을 갱신합니다.
- 조회 성능 문제가 생기면 이메일/목적/상태 인덱스 추가를 검토합니다.

## 함께 볼 문서

- [회원 테이블 정의서](./members-schema.md)
- [이메일 인증과 계정 복구 설계](../decisions/email-verification-and-account-recovery.md)
- [인증 이메일 검증과 계정 복구 API](../api/auth-email-verification.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
