# 회원 프로필 이미지 API

이 문서는 프리셋 기반 회원 프로필 이미지 설정과 관리자 운영 계약을 정리합니다. 모든 endpoint의 상태는 real입니다.

## 핵심 정책

- 회원별 현재 프로필 이미지 연결은 한 건만 유지하며 변경 이력을 저장하지 않습니다.
- 하나의 프리셋 이미지 자산을 여러 회원이 공유합니다.
- 회원이 프리셋을 다시 선택하면 기존 연결 행의 이미지 자산을 교체합니다.
- 프리셋을 삭제하면 해당 이미지를 사용 중인 회원의 프로필을 현재 기본 프리셋으로 자동 변경합니다.
- 활성 기본 프리셋은 최대 한 개입니다.
- 기본 프리셋은 다른 이미지를 기본으로 먼저 지정하기 전에는 삭제할 수 없습니다.
- 자체 회원가입과 최초 OAuth2 회원 생성 시 현재 기본 프리셋을 자동 연결합니다.

## 기준 프리셋 seed

최초 기본 프리셋은 다음 기존 R2 객체를 기준 데이터로 등록합니다.

- 공개 URL: `https://asset.matchuri.com/preset-profile/v1-spaghetti.png`
- object key: `preset-profile/v1-spaghetti.png`
- content type: `image/png`
- content length: `628206` bytes
- resolution: `1254 × 1254`

시드는 이미지 객체를 다시 업로드하지 않습니다. DB에 같은 object key가 없을 때만 자산과 프리셋을 만들고, 현재 기본 프리셋이 없을 때만 이 프리셋을 기본으로 지정합니다. 관리자가 바꾼 기본 상태는 재기동 시 덮어쓰지 않습니다.

## 서비스 API

### 선택 가능한 프리셋 이미지 목록 조회

- API ID: `ONB.120.000`
- Method: `GET`
- URL: `/api/v1/members/profile/preset-image`
- 권한: 필수 온보딩을 완료한 인증 회원

삭제되지 않은 활성 프리셋을 ID 오름차순으로 반환합니다. 사용자 화면에는 `presetProfileImageId`, `imageUrl`, `isDefault`만 노출하며 R2 object key와 원본 파일명 같은 운영 정보는 포함하지 않습니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": [
    {
      "presetProfileImageId": 1,
      "imageUrl": "https://asset.matchuri.com/preset-profile/v1-spaghetti.png",
      "isDefault": true
    },
    {
      "presetProfileImageId": 2,
      "imageUrl": "https://asset.matchuri.com/preset-profile/v1-burger.png.png",
      "isDefault": false
    }
  ],
  "error": null
}
```

인증이 없으면 `AUTH_TOKEN_MISSING`, 필수 약관이나 닉네임 온보딩이 완료되지 않았으면 관련 `403` 오류를 반환합니다.

### 프리셋 이미지 설정

- API ID: `ONB.110.000`
- Method: `PUT`
- URL: `/api/v1/members/profile/preset-image`
- 권한: 필수 약관을 완료한 인증 회원

요청 예시:

```json
{
  "presetProfileImageId": 1
}
```

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "profileImageId": 15,
    "presetProfileImageId": 1,
    "imageUrl": "https://asset.matchuri.com/preset-profile/v1-spaghetti.png",
    "updatedAt": "2026-08-24T12:30:00"
  },
  "error": null
}
```

대표 실패:

- 요청 ID가 없거나 양수가 아니면 `COMMON_INVALID_BODY_FIELD`
- 프리셋이 없거나 삭제됐으면 `IMAGE_PRESET_PROFILE_NOT_FOUND`
- 인증이 없으면 `AUTH_TOKEN_MISSING`
- 필수 약관 미완료 또는 비활성 회원이면 관련 `403` 오류

내 프로필 조회 `GET /api/v1/members/me` 응답에는 현재 공개 URL인 `profileImageUrl`이 포함됩니다. 기능 도입 전 생성되어 아직 연결이 없는 기존 회원은 `null`일 수 있습니다.

## 관리자 REST API

모든 endpoint는 `ADMIN` 역할의 JWT가 필요합니다.

| 기능 | API ID | Method | URL |
| --- | --- | --- | --- |
| 활성 프리셋 목록 | `ADMIN.160.000` | `GET` | `/api/v1/admin/preset-profile-images` |
| 프리셋 추가 | `ADMIN.170.000` | `POST` | `/api/v1/admin/preset-profile-images` |
| 프리셋 삭제 | `ADMIN.180.000` | `DELETE` | `/api/v1/admin/preset-profile-images/{presetProfileImageId}` |
| 기본 프리셋 설정 | `ADMIN.190.000` | `PUT` | `/api/v1/admin/preset-profile-images/{presetProfileImageId}/default` |

프리셋 추가는 `multipart/form-data`의 `file` part를 받습니다. JPEG, PNG, WebP와 공통 이미지 크기·해상도 제한을 적용하며 새 항목은 `isDefault=false`로 등록합니다.

기본 설정은 활성 프리셋 전체를 쓰기 잠금으로 조회한 뒤 기존 기본값을 모두 해제하고 선택 항목만 기본으로 설정합니다.

삭제는 프리셋 연결만 soft delete하고, 해당 프리셋을 사용 중인 회원의 프로필을 현재 기본 프리셋으로 변경합니다. R2 객체와 `ImageAsset`은 삭제하지 않습니다.

## 백오피스 UI

- URL: `/admin/preset-profile-images`
- 권한: form login을 완료한 `ADMIN` 세션
- 기능: 활성 프리셋 목록/미리보기, 이미지 추가, 기본 설정, 비기본 프리셋 삭제
- CSRF: 모든 변경 form에 기존 admin CSRF token을 포함합니다.

## 프론트엔드 연동 기준

- `GET /api/v1/members/profile/preset-image`로 선택 가능한 프리셋과 기본 여부를 조회합니다.
- 사용자가 고른 `presetProfileImageId`를 `PUT /api/v1/members/profile/preset-image` 요청 body에 전달합니다.
- 현재 적용된 공개 이미지 URL은 `GET /api/v1/members/me`의 `profileImageUrl`에서 확인합니다.
- 목록 API와 설정 API는 같은 경로를 사용하고 HTTP Method로 구분합니다.
