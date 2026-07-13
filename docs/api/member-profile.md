# 회원 프로필 및 공개 조회 API

이 문서는 `MemberController`의 현재 API 계약을 정리합니다.
목적은 회원 공개 중복 확인 API와 인증 이후 사용하는 프로필/취향/탈퇴 API를 프론트와 백엔드가 같은 기준으로 이해하도록 만드는 것입니다.

## 범위

- 로그인 ID 중복 확인
- 닉네임 중복 확인
- 내 프로필 조회
- 내 기본 정보 수정
- 내 비밀번호 변경
- 내 취향 프로필 조회
- 내 취향 프로필 전체 교체 저장
- 내 개인 위치 조회
- 내 개인 위치 전체 교체 저장
- 회원 탈퇴

## 비범위

- 자체 회원가입 통합 상세
- 로그인, refresh, 로그아웃
- 필수 약관 상태 조회/제출
- 소셜 로그인 상세

관련 문서:

- 자체 회원가입 통합: `docs/api/member-local-signup.md`
- 인증 세션: `docs/api/auth-session.md`
- 필수 약관: `docs/api/member-required-agreements.md`
- 참조 데이터 조회: `docs/api/menu-reference.md`

## 공통 응답 형식

MemberController 응답도 공통 envelope 구조를 사용합니다.

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

실패 시에는 `data=null`, `error`에 코드와 메시지가 들어갑니다.

## 공개 API

### 1. 로그인 ID 중복 확인

- Method: `GET`
- URL: `/api/v1/members/exists/{loginId}`
- 권한: 비회원

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "loginId": "tester01",
    "exists": true
  },
  "error": null
}
```

입력 기준:

- 1자 이상 50자 이하
- 공백 불가
- 허용 문자: 영문 대소문자, 숫자, 점(.), 밑줄(_), 하이픈(-)
- 서버 정규식: `^[A-Za-z0-9._-]+$`

실패 기준:

- 형식이 잘못되면 `COMMON_INVALID_PATH_VARIABLE`

### 2. 닉네임 중복 확인

- Method: `GET`
- URL: `/api/v1/members/exists/nickname/{nickname}`
- 권한: 비회원

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "nickname": "example_google",
    "exists": true
  },
  "error": null
}
```

입력 기준:

- 공백만으로 구성될 수 없음
- 최대 100자

실패 기준:

- 형식이 잘못되면 `COMMON_INVALID_PATH_VARIABLE`

## 보호 API

### 3. 내 프로필 조회

- Method: `GET`
- URL: `/api/v1/members/me`
- 권한: 회원

요청 기준:

- `Authorization: Bearer <accessToken>` 헤더 필요

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "loginId": "tester01",
    "nickname": "점심탐험가",
    "isSocial": false,
    "email": "tester@example.com"
  },
  "error": null
}
```

현재 응답 기준:

- 최소 프로필만 반환합니다.
- 현재 단계에서는 `id`, `loginId`, `nickname`, `isSocial`, `email`을 사용하면 됩니다.
- `loginId`는 현재 회원의 로그인 ID입니다. 소셜 로그인 전용 회원이면 `null`일 수 있습니다.
- `isSocial=true`이면 소셜 로그인 회원, `false`이면 자체 로그인 회원입니다.
- `email`은 현재 회원의 이메일입니다. 레거시 계정이면 `null`일 수 있습니다.
- 취향 프로필 상세는 이 응답에 포함되지 않습니다.

### 4. 내 기본 정보 수정

- Method: `PATCH`
- URL: `/api/v1/members/me`
- 권한: 회원

요청 body 예시:

```json
{
  "nickname": "점심탐험가"
}
```

동작 기준:

- 현재 단계에서는 `nickname`만 수정합니다.
- 부분 수정 API라서 필요한 필드만 보낼 수 있습니다.
- 약관 또는 닉네임 온보딩 미완료 상태에서도 인증된 회원이면 닉네임 확정을 위해 호출할 수 있습니다.
- 성공 시 `members.nickname_completed=true`로 처리되어 닉네임 온보딩이 완료됩니다.
- 성공 시 최신 수정 시각을 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "updatedAt": "2026-04-07T10:20:45",
    "onboarding": {
      "requiredAgreementsCompleted": true,
      "nicknameCompleted": true,
      "completed": true,
      "nextStep": "READY"
    }
  },
  "error": null
}
```

대표 실패 기준:

- 중복 닉네임이면 `MEMBER_DUPLICATE_NICKNAME`
- 인증이 없으면 `AUTH_TOKEN_MISSING`

### 5. 내 비밀번호 변경

- Method: `PATCH`
- URL: `/api/v1/members/me/password`
- 권한: 회원

요청 body 예시:

```json
{
  "currentPassword": "P@ssw0rd!",
  "newPassword": "N3wP@ssw0rd!"
}
```

동작 기준:

- 로그인 상태의 자체 로그인 회원이 설정 화면 등에서 비밀번호를 변경할 때 사용합니다.
- `currentPassword`가 현재 비밀번호와 일치해야 합니다.
- 성공 시 새 비밀번호를 BCrypt로 해시해 저장합니다.
- 성공 시 현재 access token과 refresh token은 유지합니다.
- 계정 복구용 `POST /api/v1/auth/recovery/password`와 달리 모든 세션을 로그아웃시키지 않습니다.
- 소셜 로그인 전용 회원은 현재 단계의 비밀번호 변경 대상이 아닙니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "passwordChanged": true
  },
  "error": null
}
```

대표 실패 기준:

- 인증이 없으면 `AUTH_TOKEN_MISSING`
- 현재 비밀번호가 일치하지 않으면 `MEMBER_INVALID_PASSWORD`
- 새 비밀번호 형식이 맞지 않으면 `COMMON_INVALID_BODY_FIELD`

### 6. 내 취향 프로필 조회

- Method: `GET`
- URL: `/api/v1/members/me/taste-profile`
- 권한: 회원

동작 기준:

- 현재 회원의 취향 프로필을 조회합니다.
- 프로필이 아직 없어도 빈 배열 기반 응답을 반환합니다.
- 선택된 `attribute category`, `restriction ingredient`, `disliked menu item`은 표시용 메타데이터와 함께 반환합니다.
- `profileVersion`은 현재 프로필 정책/구조가 어떤 버전을 따르는지 나타내는 서버 관리 버전입니다.
- 단순 사용자 입력 변경만으로는 `profileVersion`이 바뀌지 않습니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "memberId": 1,
    "profileVersion": "v1",
    "attributeCategories": [
      {
        "id": 1,
        "categoryType": "FLAVOR",
        "code": "SPICY",
        "name": "매운맛",
        "sortOrder": 10
      }
    ],
    "restrictionIngredients": [
      {
        "id": 101,
        "code": "PEANUT",
        "name": "땅콩",
        "allergen": true,
        "sortOrder": 10
      }
    ],
    "dislikedMenuItems": [
      {
        "id": 1001,
        "code": "PORK_CUTLET",
        "name": "돈까스"
      }
    ],
    "updatedAt": "2026-04-17T12:30:45"
  },
  "error": null
}
```

빈 프로필 응답 예시:

```json
{
  "success": true,
  "data": {
    "memberId": 1,
    "profileVersion": "v1",
    "attributeCategories": [],
    "restrictionIngredients": [],
    "dislikedMenuItems": [],
    "updatedAt": null
  },
  "error": null
}
```

### 7. 내 취향 프로필 전체 교체 저장

- Method: `PATCH`
- URL: `/api/v1/members/me/taste-profile`
- 권한: 회원

요청 body 예시:

```json
{
  "attributeCategoryIds": [1, 2],
  "restrictionIngredientIds": [101],
  "dislikedMenuItemIds": [1001, 1002]
}
```

동작 기준:

- 이 API는 전체 교체형 저장입니다.
- `attributeCategoryIds`, `restrictionIngredientIds`, `dislikedMenuItemIds`는 각각 최신 입력 기준으로 전체 교체됩니다.
- 특정 목록을 비우려면 빈 배열을 보내야 합니다.
- 잘못된 ID나 비활성 참조 데이터는 거절됩니다.
- `dislikedMenuItemIds`는 활성 `MenuItem` 검색/선택 결과의 ID 목록입니다.
- 비선호 메뉴는 취향 프로필에서 저장/조회하며, MVP 5단계 개인 추천에서는 후보 제외 조건으로 사용합니다.
- 취향 수정 시점에 선택 가능한 미종료 개인 추천이 있으면 `openPersonalRecommendationId`를 반환합니다.
- 프론트는 이 ID로 `POST /api/v1/personal/recommendations/{requestId}/reroll`의 `INPUT_CHANGED` 재요청을 호출해, 기존 후보를 `SKIP` 처리하지 않고 취향 변경 기반 추천을 다시 받을 수 있습니다.
- `profileVersion`은 수정 시각 대체값이 아니라 프로필 정책/구조 버전이므로, 단순 저장만으로는 바뀌지 않습니다.

성공 응답:

- 조회 API와 동일한 취향 프로필 구조에 `openPersonalRecommendationId`를 추가로 반환합니다.
- 진행 중인 개인 추천이 없으면 `openPersonalRecommendationId`는 `null`입니다.

```json
{
  "success": true,
  "data": {
    "memberId": 1,
    "profileVersion": "v1",
    "attributeCategories": [
      {
        "id": 1,
        "categoryType": "FLAVOR",
        "code": "SPICY",
        "name": "매운맛",
        "sortOrder": 10
      }
    ],
    "restrictionIngredients": [
      {
        "id": 101,
        "code": "PEANUT",
        "name": "땅콩",
        "allergen": true,
        "sortOrder": 10
      }
    ],
    "dislikedMenuItems": [
      {
        "id": 1001,
        "code": "PORK_CUTLET",
        "name": "돈까스"
      }
    ],
    "updatedAt": "2026-04-20T18:00:00",
    "openPersonalRecommendationId": 9001
  },
  "error": null
}
```

대표 실패 기준:

- 중복 `attribute category` ID면 `MEMBER_DUPLICATE_TASTE_ATTRIBUTE_CATEGORY`
- 중복 `restriction ingredient` ID면 `MEMBER_DUPLICATE_TASTE_RESTRICTION_INGREDIENT`
- 중복 `disliked menu item` ID면 `MEMBER_DUPLICATE_TASTE_DISLIKED_MENU_ITEM`
- 잘못된 `attribute category` ID면 `MEMBER_INVALID_TASTE_ATTRIBUTE_CATEGORY`
- 잘못된 `restriction ingredient` ID면 `MEMBER_INVALID_TASTE_RESTRICTION_INGREDIENT`
- 잘못된 `disliked menu item` ID면 `MEMBER_INVALID_TASTE_DISLIKED_MENU_ITEM`

### 8. 내 개인 위치 조회

- Method: `GET`
- URL: `/api/v1/members/me/location`
- 권한: 회원

동작 기준:

- 현재 인증 회원이 저장한 위치를 반환합니다.
- 위치가 없으면 `404 MEMBER_LOCATION_NOT_FOUND`를 반환합니다.
- 필수 온보딩 미완료 또는 비활성 회원은 `403`으로 거절됩니다.
- 저장 위치를 개인 추천 요청에 자동 적용하는 동작은 현재 범위에 포함하지 않습니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "latitude": 37.498095,
    "longitude": 127.027610,
    "radiusMeters": 1000,
    "address": "서울 강남구 테헤란로 123"
  },
  "error": null
}
```

### 9. 내 개인 위치 전체 교체 저장

- Method: `PUT`
- URL: `/api/v1/members/me/location`
- 권한: 회원

요청 body 예시:

```json
{
  "latitude": 37.498095,
  "longitude": 127.027610,
  "radiusMeters": 1000,
  "address": "서울 강남구 테헤란로 123"
}
```

동작 기준:

- 최초 요청은 위치를 생성하고 이후 요청은 기존 위치를 전체 교체합니다.
- 생성과 수정 모두 `200 OK`와 최신 위치를 반환합니다.
- 네 필드는 모두 필수이며 `null`로 일부 필드만 수정할 수 없습니다.
- 위도는 -90 이상 90 이하, 경도는 -180 이상 180 이하입니다.
- `radiusMeters`는 0 이상입니다.
- `address`는 공백 문자열일 수 없고 최대 255자이며 앞뒤 공백을 제거해 저장합니다.
- 위치 삭제 API와 개인 추천 자동 연동은 현재 범위에 포함하지 않습니다.

대표 실패 기준:

- 필수값 누락, 좌표 범위 위반, 음수 반경, 잘못된 주소는 `COMMON_INVALID_BODY_FIELD`
- 인증이 없으면 `AUTH_TOKEN_MISSING`
- 필수 온보딩 미완료 또는 비활성 회원이면 관련 `403` 오류 코드

### 10. 회원 탈퇴

- Method: `DELETE`
- URL: `/api/v1/members/me`
- 권한: 회원

동작 기준:

- 물리 삭제가 아니라 `status=INACTIVE`로 전환합니다.
- 탈퇴 후 같은 계정으로 다시 로그인할 수 없습니다.
- 이미 발급된 access token이 남아 있더라도 이후 보호 API에서는 비활성 회원으로 거절될 수 있습니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "INACTIVE"
  },
  "error": null
}
```

## 검증 시나리오 초안

- 존재하는 loginId는 `exists=true`, 없는 loginId는 `exists=false`를 반환한다.
- 존재하는 nickname은 `exists=true`, 없는 nickname은 `exists=false`를 반환한다.
- 잘못된 loginId 또는 nickname 형식은 `COMMON_INVALID_PATH_VARIABLE`을 반환한다.
- 인증된 회원은 `/api/v1/members/me`에서 `loginId`를 포함한 최소 프로필을 조회할 수 있다.
- 닉네임 수정 성공 시 `updatedAt`이 갱신된다.
- 닉네임 미완료 회원도 인증된 상태라면 `/api/v1/members/me` 수정으로 닉네임 온보딩을 완료할 수 있다.
- 중복 닉네임 수정은 `MEMBER_DUPLICATE_NICKNAME`을 반환한다.
- 비밀번호 변경 성공 시 기존 refresh token은 유지되고 기존 비밀번호 로그인은 실패한다.
- 현재 비밀번호가 틀리면 비밀번호 변경은 `MEMBER_INVALID_PASSWORD`를 반환한다.
- 프로필이 없는 회원도 `/api/v1/members/me/taste-profile`에서 빈 배열 기반 응답을 받는다.
- 취향 저장 후 재조회 시 최신 선택 상태가 반영된다.
- 중복 ID 또는 잘못된 참조 데이터 저장은 4xx로 실패한다.
- 비선호 메뉴 ID는 활성 `MenuItem` 기준으로 저장되고 조회 응답에 표시용 `id`, `code`, `name`이 포함된다.
- 개인 위치 최초 PUT 후 GET에서 같은 위치를 조회할 수 있다.
- 개인 위치 재 PUT은 기존 row를 추가하지 않고 네 필드를 전체 교체한다.
- 개인 위치가 없으면 GET은 `MEMBER_LOCATION_NOT_FOUND`를 반환한다.
- 개인 위치 요청의 필수값 누락과 값 범위 위반은 `COMMON_INVALID_BODY_FIELD`를 반환한다.
- 회원 탈퇴 후 동일 계정 재로그인은 `MEMBER_INACTIVE_MEMBER`를 반환한다.
