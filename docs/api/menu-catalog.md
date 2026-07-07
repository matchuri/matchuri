# 메뉴 카탈로그 API

이 문서는 사용자와 추천 엔진이 직접 사용하는 메뉴 카탈로그 조회 API를 정리합니다.
`attribute category`, `restriction ingredient` 선택 목록은 `docs/api/menu-reference.md`를 기준으로 봅니다.

## 범위

- 공개 메뉴 목록 조회
- 공개 메뉴 상세 조회
- 관리자 메뉴 목록 조회
- 관리자 메뉴 수정
- 관리자 메뉴 대표 이미지 업로드
- 관리자 메뉴 대표 이미지 삭제
- 관리자 메뉴 대표 이미지 업로드
- 관리자 메뉴 대표 이미지 삭제
- 관리자 메뉴 비활성화

## 비범위

- 관리자 메뉴 생성
- 음식점/장소 검색
- 추천 알고리즘
- 썸네일 파일 별도 생성
- 썸네일 파일 별도 생성

## 공통 응답 형식

```json
{
  "success": true,
  "data": [],
  "error": null
}
```

## 공개 API

### 1. 메뉴 목록 조회

- Method: `GET`
- URL: `/api/v1/menu-items`
- 권한: 비회원

Query parameter:

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `query` | N | 메뉴명 부분 검색어 |
| `attributeCategoryIds` | N | 속성 카테고리 ID 목록 |
| `ingredientIds` | N | 재료 ID 목록 |

동작 기준:

- 활성 메뉴만 반환합니다.
- 목록 응답은 `id`, `code`, `name`만 포함합니다.
- 목록 응답에는 이미지 URL을 포함하지 않습니다.
- 목록 응답에는 이미지 URL을 포함하지 않습니다.
- `query`는 메뉴명 기준 부분 검색입니다.
- `attributeCategoryIds` 내부는 OR 조건으로 처리합니다.
- `ingredientIds` 내부는 OR 조건으로 처리합니다.
- `query`, `attributeCategoryIds`, `ingredientIds` 그룹 간 조합은 AND 조건으로 처리합니다.
- 존재하지 않거나 비활성화된 `attributeCategoryIds`, `ingredientIds`가 포함되면 4xx로 거절합니다.
- 정렬 기준은 `id` 오름차순입니다.
- `ingredientIds`는 "해당 재료가 포함된 메뉴를 찾는 필터"이며, 추천 단계의 `restriction ingredient` 기반 제외 규칙과 다릅니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": [
    {
      "id": 1001,
      "code": "PORK_CUTLET",
      "name": "돈까스"
    }
  ],
  "error": null
}
```

대표 실패 기준:

- 존재하지 않거나 비활성화된 `attributeCategoryIds`가 포함되면 `MENU_INVALID_FILTER`
- 존재하지 않거나 비활성화된 `ingredientIds`가 포함되면 `MENU_INVALID_FILTER`

### 2. 메뉴 상세 조회

- Method: `GET`
- URL: `/api/v1/menu-items/{menuItemId}`
- 권한: 비회원

동작 기준:

- 활성 메뉴만 조회할 수 있습니다.
- 비활성 메뉴 또는 존재하지 않는 메뉴 ID는 404로 응답합니다.
- 메뉴 기본 정보와 연결된 활성 `attribute category`, `ingredient` 목록을 반환합니다.
- 메뉴 대표 이미지가 있으면 `thumbnailUrl`에 공개 이미지 URL을 반환합니다.
- 대표 이미지가 없으면 `thumbnailUrl=null`을 반환합니다.
- 메뉴 대표 이미지가 있으면 `thumbnailUrl`에 공개 이미지 URL을 반환합니다.
- 대표 이미지가 없으면 `thumbnailUrl=null`을 반환합니다.
- 비활성 `attribute category`, `ingredient` 연결은 응답에서 제외합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 1001,
    "code": "PORK_CUTLET",
    "name": "돈까스",
    "description": "돼지고기를 튀겨 소스와 함께 먹는 바삭한 메뉴입니다.",
    "thumbnailUrl": "https://asset.matchuri.com/menu-items/1001/sample.jpg",
    "thumbnailUrl": "https://asset.matchuri.com/menu-items/1001/sample.jpg",
    "attributeCategories": [
      {
        "id": 1,
        "categoryType": "TEXTURE",
        "code": "CRISPY",
        "name": "바삭함",
        "sortOrder": 10
      }
    ],
    "ingredients": [
      {
        "id": 101,
        "code": "PORK",
        "name": "돼지고기",
        "allergen": false,
        "sortOrder": 10
      }
    ]
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않거나 비활성화된 `menuItemId`이면 `MENU_NOT_FOUND`

## 프론트 사용 기준

- 비선호 메뉴 선택 UI는 이 API의 `query` 검색 결과를 사용합니다.
- 메뉴 목록 화면 또는 추천 후보 선택 전 탐색 화면은 이 API를 사용합니다.
- 메뉴 설명, 속성, 재료 연결 정보가 필요하면 메뉴 상세 조회 API를 사용합니다.

## 관리자 API

### 3. 관리자 메뉴 목록 조회

- Method: `GET`
- URL: `/api/v1/admin/menu-items`
- 권한: `ADMIN`

동작 기준:

- 활성/비활성 메뉴를 모두 반환합니다.
- 별도 `includeInactive` 파라미터 없이 전체 운영 상태를 기본으로 조회합니다.
- 정렬 기준은 `id` 오름차순입니다.
- 응답에는 운영 판단을 위한 `isActive`가 포함됩니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": [
    {
      "id": 1001,
      "code": "PORK_CUTLET",
      "name": "돈까스",
      "description": "돼지고기를 튀겨 소스와 함께 먹는 바삭한 메뉴입니다.",
      "isActive": true
    },
    {
      "id": 1002,
      "code": "SUSHI",
      "name": "초밥",
      "description": "초밥용 밥 위에 생선이나 재료를 올린 메뉴입니다.",
      "isActive": false
    }
  ],
  "error": null
}
```

대표 실패 기준:

- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 4. 관리자 메뉴 상세 조회

- Method: `GET`
- URL: `/api/v1/admin/menu-items/{menuItemId}`
- 권한: `ADMIN`

동작 기준:

- 메뉴 기본 정보, 대표 이미지 URL, attribute category 연결, ingredient 연결을 함께 반환합니다.
- 연결 목록에는 관리자 판단을 위해 `isActive`를 포함합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 1001,
    "code": "PORK_CUTLET",
    "name": "돈까스",
    "description": "돼지고기를 튀겨 소스와 함께 먹는 바삭한 메뉴입니다.",
    "isActive": true,
    "thumbnailUrl": "https://asset.matchuri.com/menu-items/1001/sample.jpg",
    "attributeCategories": [
      {
        "id": 1,
        "categoryType": "FOOD_CATEGORY",
        "code": "JAPANESE",
        "name": "일식",
        "sortOrder": 10,
        "isActive": true
      }
    ],
    "ingredients": [
      {
        "id": 10,
        "code": "PORK",
        "name": "돼지고기",
        "allergen": false,
        "sortOrder": 10,
        "isActive": true
      }
    ]
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `menuItemId`이면 `MENU_NOT_FOUND`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 5. 관리자 메뉴 생성

- Method: `POST`
- URL: `/api/v1/admin/menu-items`
- 권한: `ADMIN`

요청 body:

```json
{
  "code": "KIMCHI_FRIED_RICE",
  "name": "김치볶음밥",
  "description": "김치와 밥을 볶은 한식 메뉴입니다.",
  "attributeCategoryIds": [1, 2],
  "ingredientIds": [10, 11]
}
```

동작 기준:

- 생성 직후 `isActive=true`입니다.
- `code`는 생성 이후 안정적인 비즈니스 키로 보고 수정하지 않습니다.
- 중복 `code`는 `MENU_DUPLICATE`로 거절합니다.
- `attributeCategoryIds`, `ingredientIds`는 중복을 거절합니다.
- 연결 대상은 활성 데이터만 허용합니다.
- 성공 시 관리자 메뉴 상세 응답을 반환합니다.

대표 실패 기준:

- 중복 `code`이면 `MENU_DUPLICATE`
- 중복된 attribute category ID이면 `MENU_DUPLICATE_MENU_ATTRIBUTE_CATEGORY`
- 비활성 또는 존재하지 않는 attribute category ID이면 `MENU_INVALID_MENU_ATTRIBUTE_CATEGORY`
- 중복된 ingredient ID이면 `MENU_DUPLICATE_MENU_INGREDIENT`
- 비활성 또는 존재하지 않는 ingredient ID이면 `MENU_INVALID_MENU_INGREDIENT`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 6. 관리자 메뉴 수정

- Method: `PATCH`
- URL: `/api/v1/admin/menu-items/{menuItemId}`
- 권한: `ADMIN`

요청 body:

```json
{
  "name": "새 돈까스",
  "description": "돼지고기를 튀겨 소스와 함께 먹는 바삭한 메뉴입니다.",
  "isActive": false
}
```

동작 기준:

- 수정 가능 필드는 `name`, `description`, `isActive`입니다.
- `code`는 안정적인 비즈니스 키로 보고 수정하지 않습니다.
- 요청에 포함하지 않은 필드는 유지합니다.
- `name`, `description`은 앞뒤 공백을 제거한 뒤 저장합니다.
- `isActive=true`를 보내면 비활성 메뉴를 다시 활성화할 수 있습니다.
- 성공 시 최신 관리자 메뉴 단건 상태를 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 1001,
    "code": "PORK_CUTLET",
    "name": "새 돈까스",
    "description": "돼지고기를 튀겨 소스와 함께 먹는 바삭한 메뉴입니다.",
    "isActive": false
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `menuItemId`이면 `MENU_NOT_FOUND`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 7. 관리자 메뉴 연결 수정

- Method: `PATCH`
- URL: `/api/v1/admin/menu-items/{menuItemId}/references`
- 권한: `ADMIN`

요청 body:

```json
{
  "attributeCategoryIds": [1, 2, 3],
  "ingredientIds": [10, 11]
}
```

동작 기준:

- 메뉴의 attribute category 연결과 ingredient 연결을 최신 입력 기준으로 전체 교체합니다.
- 빈 배열은 해당 연결을 모두 제거한다는 의미입니다.
- 연결 대상은 활성 데이터만 허용합니다.
- 성공 시 관리자 메뉴 상세 응답을 반환합니다.
- 이 변경은 공개 메뉴 상세와 추천 알고리즘 입력 데이터에 영향을 줍니다.

대표 실패 기준:

- 존재하지 않는 `menuItemId`이면 `MENU_NOT_FOUND`
- 중복된 attribute category ID이면 `MENU_DUPLICATE_MENU_ATTRIBUTE_CATEGORY`
- 비활성 또는 존재하지 않는 attribute category ID이면 `MENU_INVALID_MENU_ATTRIBUTE_CATEGORY`
- 중복된 ingredient ID이면 `MENU_DUPLICATE_MENU_INGREDIENT`
- 비활성 또는 존재하지 않는 ingredient ID이면 `MENU_INVALID_MENU_INGREDIENT`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 8. 관리자 메뉴 대표 이미지 업로드

- Method: `POST`
- URL: `/api/v1/admin/menu-items/{menuItemId}/images`
- 권한: `ADMIN`
- Content-Type: `multipart/form-data`

Form field:

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `file` | Y | 업로드할 메뉴 이미지 파일 |

동작 기준:

- 서버 중계 업로드 방식으로 R2에 이미지를 저장합니다.
- 허용 MIME type은 `image/jpeg`, `image/png`, `image/webp`입니다.
- 최대 파일 크기는 5 MiB입니다.
- 허용 해상도는 최소 300x300, 최대 4096x4096입니다.
- 실제 이미지로 디코딩되지 않는 파일은 거절합니다.
- object key는 `menu-items/{menuItemId}/{uuid}.{ext}` 형식으로 생성합니다.
- R2 public base URL은 `https://asset.matchuri.com`입니다.
- 응답의 `thumbnailUrl`은 첫 구현에서 원본 이미지 URL입니다.
- 이미 대표 이미지가 있으면 새 이미지로 교체하고, 기존 R2 객체는 커밋 이후 best-effort로 삭제합니다.
- DB 저장 실패 시 방금 업로드한 R2 객체는 best-effort로 삭제합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "menuId": 1001,
    "imageAssetId": 2001,
    "thumbnailUrl": "https://asset.matchuri.com/menu-items/1001/sample.jpg",
    "objectKey": "menu-items/1001/sample.jpg",
    "contentType": "image/jpeg",
    "contentLength": 152000,
    "width": 1200,
    "height": 900
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `menuItemId`이면 `MENU_NOT_FOUND`
- 빈 파일이면 `IMAGE_UPLOAD_FILE_EMPTY`
- 파일 크기 초과이면 `IMAGE_UPLOAD_FILE_TOO_LARGE`
- 지원하지 않는 MIME type이면 `IMAGE_UNSUPPORTED_CONTENT_TYPE`
- 실제 이미지로 읽을 수 없으면 `IMAGE_INVALID_CONTENT`
- 해상도 제한을 벗어나면 `IMAGE_INVALID_RESOLUTION`
- R2 업로드 실패이면 `IMAGE_STORAGE_UPLOAD_FAILED`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 9. 관리자 메뉴 대표 이미지 삭제

- Method: `DELETE`
- URL: `/api/v1/admin/menu-items/{menuItemId}/images/primary`
- 권한: `ADMIN`

동작 기준:

- 메뉴 대표 이미지 연결을 제거합니다.
- 연결된 `image_assets.status`는 `DELETED`로 변경합니다.
- 연결된 R2 객체는 커밋 이후 best-effort로 삭제합니다.
- 대표 이미지가 없어도 실패시키지 않고 성공으로 처리합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": null,
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `menuItemId`이면 `MENU_NOT_FOUND`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 10. 관리자 메뉴 비활성화

- Method: `DELETE`
- URL: `/api/v1/admin/menu-items/{menuItemId}`
- 권한: `ADMIN`

동작 기준:

- 물리 삭제가 아니라 `isActive=false` 비활성화로 처리합니다.
- 이미 비활성 상태여도 실패시키지 않고 현재 상태를 그대로 반환합니다.
- 공개 메뉴 목록/상세 조회에서는 비활성 메뉴가 제외됩니다.
- 회원 취향 프로필의 `dislikedMenuItemIds` 저장 검증에서도 비활성 메뉴 ID는 거절됩니다.
- 성공 시 최신 관리자 메뉴 단건 상태를 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 1001,
    "code": "PORK_CUTLET",
    "name": "돈까스",
    "description": "돼지고기를 튀겨 소스와 함께 먹는 바삭한 메뉴입니다.",
    "isActive": false
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `menuItemId`이면 `MENU_NOT_FOUND`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`
