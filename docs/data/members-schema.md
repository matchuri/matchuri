# 회원 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: member
- 기준 소스:
  - JPA Entity: `Member`, `MemberRole`, `MemberStatus`, `SocialProviderType`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: `docs/api/member*.md`, `docs/api/auth*.md`

## 기준 소스 우선순위

1. JPA Entity와 enum
2. `backend/init/sql/01-schema.sql`
3. Repository query, service write path, 테스트
4. 관련 API 문서
5. 기존 `docs/data/`

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- `members` 테이블의 현재 컬럼, 제약, 상태값을 정의합니다.
- 자체 로그인 회원과 소셜 로그인 회원을 하나의 회원 테이블에서 다루는 기준을 고정합니다.
- 회원 하위 데이터가 참조하는 기준 FK 역할을 설명합니다.

## 현재 확정 전제

- 회원은 자체 로그인과 소셜 로그인을 모두 `members`에 저장합니다.
- 탈퇴는 물리 삭제보다 `status=INACTIVE` 전환을 우선합니다.
- 필수 약관 완료 여부는 `members`가 아니라 `member_agreements` 기준으로 계산합니다.
- 소셜 회원은 가입 직후 닉네임 온보딩이 필요하므로 `nickname_completed=false`로 시작할 수 있습니다.

가정(Assumption):

- DB 레벨 check constraint로 가입 방식별 필수 컬럼 조합을 강제하지 않고 서비스 계층에서 검증합니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `members` | 회원 계정, 인증 방식, 역할, 상태의 기준 테이블 | `Member`, `01-schema.sql` |

## `members`

### 역할

- 서비스 주체인 회원을 식별합니다.
- 자체 로그인 정보, 소셜 제공자 식별자, 이메일, 닉네임, 역할, 상태를 저장합니다.
- 약관, 취향 프로필, 인증 토큰, 추천, 그룹 도메인의 기준 FK가 됩니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 회원 ID |
| `login_id` | varchar(50) | Y |  | unique | 자체 로그인 ID |
| `password_hash` | varchar(255) | Y |  |  | 자체 로그인 비밀번호 해시 |
| `nickname` | varchar(100) | Y |  | unique | 표시 닉네임 |
| `nickname_completed` | bit(1) / boolean | N | `false` |  | 닉네임 온보딩 완료 여부 |
| `email` | varchar(150) | Y |  |  | 이메일 |
| `is_social` | bit(1) / boolean | N | `false` |  | 소셜 로그인 여부 |
| `social_provider_type` | varchar(20) | Y |  | unique 조합 | 소셜 제공자 |
| `social_provider_user_id` | varchar(100) | Y |  | unique 조합 | 소셜 제공자 사용자 식별자 |
| `member_role` | varchar(20) | N |  | enum | 회원 역할 |
| `status` | varchar(20) | N |  | enum | 회원 상태 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 회원 식별자 |
| unique | `uk_members_login_id` | `login_id` | 자체 로그인 ID 중복 방지 |
| unique | `uk_members_nickname` | `nickname` | 닉네임 중복 방지 |
| unique | `uk_members_social_provider_user` | `social_provider_type`, `social_provider_user_id` | 동일 소셜 계정 중복 가입 방지 |

### 인덱스

- 현재 명시 보조 인덱스 없음
- unique 제약은 데이터 무결성 기준으로 유지합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `member_role` | `MEMBER` | 일반 회원 |
| `member_role` | `ADMIN` | 관리자 |
| `status` | `ACTIVE` | 활성 회원 |
| `status` | `INACTIVE` | 탈퇴 또는 비활성 회원 |
| `social_provider_type` | `GOOGLE` | Google OAuth2 제공자 |
| `social_provider_type` | `KAKAO` | Kakao OAuth2 제공자 |
| `social_provider_type` | `NAVER` | Naver OAuth2 제공자 |

### 관계

| 기준 | 대상 | 관계 | 설명 |
| --- | --- | --- | --- |
| `members.id` | `member_agreements.member_id` | 1 : N | 약관 동의 이력 |
| `members.id` | `member_taste_profiles.member_id` | 1 : 0..1 | 회원 취향 프로필 |
| `members.id` | `auth_refresh_tokens.member_id` | 1 : N | refresh token |
| `members.id` | `auth_exchange_codes.member_id` | 1 : N | OAuth2 exchange code |
| `members.id` | `personal_recommendations.member_id` | 1 : N | 개인 추천 |
| `members.id` | `group_rooms.host_member_id` | 1 : N | 그룹 방장 |
| `members.id` | `group_room_members.member_id` | 1 : N | 그룹 멤버십 |

### 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 | 주의점 |
| --- | --- | --- | --- |
| 자체 로그인 | `login_id` | 회원 조회 후 비밀번호 검증 | `status=ACTIVE` 확인 |
| 소셜 로그인 | `social_provider_type`, `social_provider_user_id` | 회원 조회 또는 신규 생성 | 제공자 enum 허용 범위 확인 |
| 닉네임 변경 | `nickname` | 중복 검사 후 저장 | 저장 시 `nickname_completed=true` |
| 탈퇴 | `id` | `status=INACTIVE` 전환 | 하위 이력은 물리 삭제하지 않음 |

### 운영 기준

- 자체 로그인 회원은 `login_id`, `password_hash`, `nickname`, `email`을 가진 상태로 생성합니다.
- 소셜 회원은 `login_id`, `password_hash`가 없을 수 있고, 닉네임 온보딩 전까지 `nickname_completed=false`일 수 있습니다.
- 관리자 로그인은 `member_role=ADMIN`, `status=ACTIVE`, `is_social=false`, `password_hash` 존재 회원을 대상으로 봅니다.

### 현재 제외 범위

- 회원 상세 프로필 확장 컬럼
- DB check constraint 기반 가입 방식 검증
- 소셜 계정 다중 연결 테이블

## 영역 공통 판단

- `members`는 인증 방식별 테이블을 분리하지 않고 서비스 주체를 단일화합니다.
- 서비스 이용 가능 여부 중 약관 완료는 `member_agreements`에서 파생 계산합니다.

## 코드 변경 시 확인할 것

- `Member` 필드와 `01-schema.sql` 컬럼이 일치하는지 확인합니다.
- `SocialProviderType` 값 추가 시 OAuth2 설정, exchange code 문서, API 문서를 함께 확인합니다.
- 회원 상태값 추가 시 인증 필터, 탈퇴/복구 정책, API 응답을 확인합니다.

## 함께 볼 문서

- [회원 약관 동의 테이블 정의서](./member-agreements-schema.md)
- [회원 취향 프로필 테이블 정의서](./member-taste-profiles-schema.md)
- [인증 refresh token 테이블 정의서](./auth-refresh-tokens-schema.md)
- [인증 exchange code 테이블 정의서](./auth-exchange-codes-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
