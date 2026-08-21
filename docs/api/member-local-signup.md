# 자체 회원가입 통합 API

이 문서는 Matchuri의 자체 회원가입 통합 API 계약을 정리합니다.
목적은 자체 회원가입에서 `loginId`, `password`, `nickname`, 검증된 `email`, 필수 약관 동의와 초기 취향 프로필을 하나의 원자적 요청으로 처리하는 현재 기준을 백엔드와 프론트가 같은 기준으로 이해하도록 만드는 것입니다.

## 범위

- 자체 회원가입 통합 요청
- 이메일 인증 완료 여부 확인
- 필수 약관 동의 동시 제출
- 닉네임 필수 확정
- 취향 프로필 초기 생성
- 성공 시 비로그인 상태 유지

## 비범위

- 소셜 로그인 회원가입 플로우 변경
- 로그인 API 응답 형식 변경
- 약관 버전 관리 구조 변경
- 프론트 회원가입 화면 구현 상세

## 현재 확정 결정

- 신규 자체 회원가입은 취향 프로필을 포함하는 `POST /api/v2/members/signup`을 기본 경로로 사용합니다.
- 요청에는 `loginId`, `password`, `nickname`, `email`, `emailVerificationToken`, `agreements`, `tasteProfile` 7가지를 모두 포함합니다.
- 닉네임은 기본값 없이 필수 입력입니다.
- 이메일은 회원 생성 전에 `SIGNUP` 목적 인증을 완료해야 합니다.
- 한 이메일에 여러 자체 로그인 ID를 허용하지 않습니다.
- 약관 입력은 `agreementType + agreementVersion` 구조를 유지합니다.
- 회원가입 성공 시 자동 로그인되지 않습니다.
- 회원 생성, 약관 동의 저장, 닉네임 반영, 취향 프로필 초기화는 하나의 트랜잭션으로 처리합니다.
- 처리 중 하나라도 실패하면 회원, 약관 동의, 취향 프로필 기록은 남지 않아야 합니다.
- 기존 `POST /api/v1/members/signup`과 `POST /api/v1/members`는 안정화 기간 동안 호환용으로 유지합니다.

## 엔드포인트

### 자체 회원가입 통합

- Method: `POST`
- URL: `/api/v2/members/signup`
- 권한: 비회원

요청 body 예시:

```json
{
  "loginId": "tester01",
  "password": "P@ssw0rd!",
  "nickname": "점심탐험가",
  "email": "tester@example.com",
  "emailVerificationToken": "ev_eyJhbGciOiJIUzI1NiJ9...",
  "agreements": [
    {
      "agreementType": "TERMS_OF_SERVICE",
      "agreementVersion": "2026-04-10"
    },
    {
      "agreementType": "PRIVACY_POLICY",
      "agreementVersion": "2026-04-10"
    }
  ],
  "tasteProfile": {
    "attributeCategoryIds": [1, 2],
    "restrictionIngredientIds": [101],
    "dislikedMenuItemIds": [1001, 1002]
  }
}
```

응답 payload 예시:

```json
{
  "memberId": 1,
  "loginId": "tester01",
  "email": "tester@example.com",
  "nickname": "점심탐험가",
  "createdAt": "2026-04-14T20:15:30"
}
```

## 요청값 기준

### `loginId`

- 필수
- 기존 `POST /api/v1/members`와 같은 제약을 사용합니다.
- 영문, 숫자, 점(.), 밑줄(_), 하이픈(-)만 허용합니다.

### `password`

- 필수
- 기존 자체 회원가입과 같은 길이 제약을 사용합니다.

### `nickname`

- 필수
- 공백만으로 구성될 수 없습니다.
- 최대 길이는 현재 `members.nickname` 제약을 따릅니다.
- 자체 회원가입에서는 기본값을 제공하지 않습니다.

### `email`

- 필수
- 신규 자체 회원가입의 계정 복구 기준 이메일입니다.
- 회원 생성 전에 이메일 인증을 완료해야 합니다.

### `emailVerificationToken`

- 필수
- `SIGNUP` 목적의 이메일 인증 확인 API에서 발급받은 단기 token입니다.
- 요청의 `email`과 token의 이메일이 일치해야 합니다.

### `agreements`

- 필수
- 현재 필수 약관 2종을 모두 포함해야 합니다.
- 각 항목은 아래 필드를 가집니다.
  - `agreementType`
  - `agreementVersion`

### `tasteProfile`

- 필수 객체입니다.
- 아래 세 ID 목록을 모두 포함해야 하며, 선택 항목이 없으면 빈 배열을 보냅니다.
  - `attributeCategoryIds`
  - `restrictionIngredientIds`
  - `dislikedMenuItemIds`
- 각 목록 안의 중복 ID는 허용하지 않습니다.
- 존재하며 활성화된 attribute category, restriction ingredient, menu item ID만 허용합니다.
- 가입 성공 시 회원별 `member_taste_profiles` 헤더와 선택 매핑을 신규 생성합니다.

## 동작 기준

1. 서버는 `loginId`, `nickname` 중복 여부를 확인합니다.
2. 서버는 `emailVerificationToken`이 `SIGNUP` 목적이고 요청 `email`과 일치하는지 확인합니다.
3. 서버는 요청 `email`이 기존 자체 로그인 계정에 이미 사용 중인지 확인합니다.
4. 서버는 회원 레코드를 생성하며 검증된 `email`을 저장합니다.
5. 서버는 요청된 필수 약관 2종과 버전을 검증합니다.
6. 서버는 `member_agreements`에 필수 약관 동의 기록을 저장합니다.
7. 서버는 취향 ID의 중복과 활성 참조 데이터 여부를 검증합니다.
8. 서버는 회원의 초기 취향 프로필과 선택 매핑을 신규 저장합니다.
9. 모든 단계가 성공하면 회원가입을 완료합니다.
10. 응답 후 로그인 세션이나 토큰은 발급하지 않습니다.

주의:

- 회원 생성 이후 약관 또는 취향 프로필 검증·저장 단계에서 실패하더라도 트랜잭션 전체가 롤백되어야 합니다.
- 즉, 성공 응답이 아니면 `members`, `member_agreements`, `member_taste_profiles`와 취향 선택 매핑에 흔적이 남지 않는 것이 현재 기준입니다.

## 성공 이후 프론트 처리 기준

- 회원가입 성공 후 즉시 로그인 상태로 보지 않습니다.
- 프론트는 로그인 화면으로 이동하거나, 같은 `loginId/password`로 `POST /api/v1/auth/login`을 호출합니다.
- 새 통합 회원가입으로 생성된 회원은 필수 약관 동의가 이미 완료된 상태이므로, 로그인 후 별도 약관 동의 화면으로 보내지 않습니다.

## 레거시 API와의 관계

### 기존 통합 `POST /api/v1/members/signup`

- `loginId`, `password`, `nickname`, 검증된 `email`, 필수 약관 동의를 함께 처리합니다.
- 취향 프로필을 생성하지 않습니다.
- v2 안정화 기간 동안 기존 클라이언트 호환용으로 유지하며 신규 연동의 기본 경로로 보지 않습니다.

### 레거시 `POST /api/v1/members`

- 현재는 `loginId`, `password`만으로 회원을 생성합니다.
- 필수 약관 동의와 닉네임 설정은 포함하지 않습니다.
- 기존 클라이언트 호환을 위해 유지하지만, 신규 구현의 기본 경로로 보지 않습니다.

### `POST /api/v1/member-agreements/consents`

- 소셜 로그인 신규 가입
- 레거시 자체 회원가입 흐름
- 기존 미동의 회원 보정

위 경우에는 계속 필요합니다.

## 이메일 인증 연계 결정

로그인 ID 찾기와 비밀번호 재설정을 제공하려면 자체 로그인 계정에 검증된 이메일이 필요하므로, 신규 자체 회원가입 요청에는 `email`과 `emailVerificationToken`을 포함합니다.
신규 자체 회원가입은 회원 생성 전에 `SIGNUP` 목적의 이메일 인증을 완료해야 합니다.
구현에서는 회원가입 트랜잭션 안에서 `emailVerificationToken`을 검증하고, 성공 시 token을 사용 완료 처리합니다.
약관 검증 등 후속 단계가 실패하면 회원 생성과 token 사용 완료 처리는 함께 롤백됩니다.

관련 설계는 `docs/decisions/email-verification-and-account-recovery.md`, 목표 API 계약은 `docs/api/auth-email-verification.md`를 봅니다.

## 실패 시나리오 초안

- `MEMBER_DUPLICATE_LOGIN_ID`
- `MEMBER_DUPLICATE_NICKNAME`
- `MEMBER_DUPLICATE_EMAIL`
- `AUTH_EMAIL_VERIFICATION_FAILED`
- `MEMBER_AGREEMENT_REQUIRED_TYPES_MISSING`
- `MEMBER_AGREEMENT_INVALID_TYPE`
- `MEMBER_AGREEMENT_VERSION_MISMATCH`
- `MEMBER_DUPLICATE_TASTE_ATTRIBUTE_CATEGORY`
- `MEMBER_DUPLICATE_TASTE_RESTRICTION_INGREDIENT`
- `MEMBER_DUPLICATE_TASTE_DISLIKED_MENU_ITEM`
- `MEMBER_INVALID_TASTE_ATTRIBUTE_CATEGORY`
- `MEMBER_INVALID_TASTE_RESTRICTION_INGREDIENT`
- `MEMBER_INVALID_TASTE_DISLIKED_MENU_ITEM`

## 검증 시나리오 초안

- 유효한 요청이면 회원, 필수 약관 동의 2건, 초기 취향 프로필과 선택 매핑이 함께 저장된다.
- 유효한 요청이면 검증된 이메일이 회원에 저장된다.
- `SIGNUP` 목적의 유효한 `emailVerificationToken`이 없으면 회원가입 전체가 실패한다.
- 이미 자체 로그인 계정에 사용 중인 이메일이면 회원가입이 실패한다.
- 성공 시 로그인 세션이나 refresh token 쿠키가 발급되지 않는다.
- 로그인 후에는 별도 약관 동의 없이 보호 API 접근이 가능하다.
- 약관 버전이 잘못되면 회원가입 전체가 실패하고 회원 레코드가 남지 않는다.
- 필수 약관 타입이 누락되면 회원가입 전체가 실패한다.
- 중복 `loginId` 또는 `nickname`이면 회원가입이 실패한다.
- 중복되거나 유효하지 않은 취향 ID가 포함되면 회원가입 전체가 실패하고 회원·약관·취향 프로필 레코드가 남지 않는다.
