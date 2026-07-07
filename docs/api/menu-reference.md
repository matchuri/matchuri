# 메뉴 참조 데이터 조회 API

이 문서는 취향 입력과 메뉴 분류에 공통으로 사용하는 참조 데이터 조회 API를 정리합니다.
목적은 프론트엔드가 `attribute category`, `restriction ingredient` 선택 UI를 같은 기준으로 구성하게 만드는 것입니다.

## 범위

- `attribute category` 목록 조회
- `restriction ingredient` 목록 조회
- 관리자 `attribute category` 목록 조회
- 관리자 `attribute category` 생성
- 관리자 `attribute category` 수정
- 관리자 `attribute category` 비활성화
- 관리자 `ingredient` 목록 조회
- 관리자 `ingredient` 생성
- 관리자 `ingredient` 수정
- 관리자 `ingredient` 비활성화

## 비범위

- 메뉴 목록/상세 조회
- 메뉴 필터 검색

## 공통 응답 형식

```json
{
  "success": true,
  "data": [],
  "error": null
}
```

## 공개 API

### 1. attribute category 목록 조회

- Method: `GET`
- URL: `/api/v1/attribute-categories`
- 권한: 비회원

Query parameter:

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `categoryTypes` | N | 조회할 `CategoryType` 목록. 허용 값: `FLAVOR`, `COOKING_METHOD`, `FOOD_CATEGORY`, `TEXTURE`, `TEMPERATURE` |

동작 기준:

- 활성 `attribute category`만 반환합니다.
- `categoryTypes`가 있으면 해당 유형의 `attribute category`만 반환합니다.
- 정렬 기준은 `categoryType`, `sortOrder`, `id`입니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "categoryType": "FLAVOR",
      "code": "SPICY",
      "name": "매운맛",
      "sortOrder": 10
    }
  ],
  "error": null
}
```

대표 실패 기준:

- 잘못된 `categoryTypes` 값이면 `COMMON_INVALID_QUERY_PARAMETER`

### 2. restriction ingredient 목록 조회

- Method: `GET`
- URL: `/api/v1/restriction-ingredients`
- 권한: 비회원

Query parameter:

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `query` | N | 재료명 부분 검색어 |
| `allergen` | N | 알레르기 유발 재료 여부. `true` 또는 `false` |

동작 기준:

- 활성 `restriction ingredient`만 반환합니다.
- `query`는 재료명 기준 부분 검색입니다.
- `allergen`이 있으면 알레르기 유발 여부로 필터링합니다.
- `query`와 `allergen` 조합은 AND 조건으로 처리합니다.
- 정렬 기준은 `sortOrder`, `id`입니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "code": "PEANUT",
      "name": "땅콩",
      "allergen": true,
      "sortOrder": 10
    }
  ],
  "error": null
}
```

대표 실패 기준:

- 잘못된 `allergen` 값이면 `COMMON_INVALID_QUERY_PARAMETER`

## 관리자 API

### 3. 관리자 attribute category 목록 조회

- Method: `GET`
- URL: `/api/v1/admin/attribute-categories`
- 권한: `ADMIN`

동작 기준:

- 활성/비활성 `attribute category`를 모두 반환합니다.
- 별도 `includeInactive` 파라미터 없이 전체 운영 상태를 기본으로 조회합니다.
- 정렬 기준은 `categoryType`, `sortOrder`, `id`입니다.
- 응답에는 운영 판단을 위한 `isActive`가 포함됩니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "categoryType": "FLAVOR",
      "code": "SPICY",
      "name": "매운맛",
      "sortOrder": 10,
      "isActive": true
    },
    {
      "id": 2,
      "categoryType": "FLAVOR",
      "code": "MILD",
      "name": "순한맛",
      "sortOrder": 20,
      "isActive": false
    }
  ],
  "error": null
}
```

대표 실패 기준:

- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 4. 관리자 attribute category 생성

- Method: `POST`
- URL: `/api/v1/admin/attribute-categories`
- 권한: `ADMIN`

요청 body 예시:

```json
{
  "categoryType": "FLAVOR",
  "code": "SPICY",
  "name": "매운맛",
  "sortOrder": 10
}
```

동작 기준:

- 생성 직후 `isActive=true` 상태로 저장합니다.
- 중복 기준은 `(categoryType, code)` 조합입니다.
- `categoryType`은 `FLAVOR`, `COOKING_METHOD`, `FOOD_CATEGORY`, `TEXTURE`, `TEMPERATURE`만 허용합니다.
- 성공 시 최신 단건 상태를 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 10,
    "categoryType": "FLAVOR",
    "code": "SPICY",
    "name": "매운맛",
    "sortOrder": 10,
    "isActive": true
  },
  "error": null
}
```

대표 실패 기준:

- 잘못된 `categoryType`이면 `COMMON_INVALID_BODY_FIELD`
- 같은 `(categoryType, code)`가 이미 있으면 `MENU_ATTRIBUTE_CATEGORY_DUPLICATE`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`

### 5. 관리자 attribute category 수정

- Method: `PATCH`
- URL: `/api/v1/admin/attribute-categories/{attributeCategoryId}`
- 권한: `ADMIN`

요청 body 예시:

```json
{
  "name": "순한맛",
  "sortOrder": 20,
  "isActive": false
}
```

동작 기준:

- 수정 가능 필드는 `name`, `sortOrder`, `isActive`입니다.
- 요청에 포함하지 않은 필드는 유지합니다.
- `isActive=true`를 보내면 비활성 데이터를 다시 활성화할 수 있습니다.
- `code`, `categoryType`은 이 API에서 수정하지 않습니다.
- 성공 시 최신 단건 상태를 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 10,
    "categoryType": "FLAVOR",
    "code": "SPICY",
    "name": "순한맛",
    "sortOrder": 20,
    "isActive": false
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `attributeCategoryId`면 `MENU_ATTRIBUTE_CATEGORY_NOT_FOUND`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`

### 6. 관리자 attribute category 비활성화

- Method: `DELETE`
- URL: `/api/v1/admin/attribute-categories/{attributeCategoryId}`
- 권한: `ADMIN`

동작 기준:

- 물리 삭제가 아니라 `isActive=false` 비활성화로 처리합니다.
- 이미 비활성 상태여도 실패시키지 않고 현재 상태를 그대로 반환합니다.
- 성공 시 최신 단건 상태를 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 10,
    "categoryType": "FLAVOR",
    "code": "SPICY",
    "name": "매운맛",
    "sortOrder": 10,
    "isActive": false
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `attributeCategoryId`면 `MENU_ATTRIBUTE_CATEGORY_NOT_FOUND`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`

### 7. 관리자 ingredient 목록 조회

- Method: `GET`
- URL: `/api/v1/admin/ingredients`
- 권한: `ADMIN`

동작 기준:

- 활성/비활성 `ingredient`를 모두 반환합니다.
- 별도 `includeInactive` 파라미터 없이 전체 운영 상태를 기본으로 조회합니다.
- 정렬 기준은 `sortOrder`, `id`입니다.
- 응답에는 운영 판단을 위한 `allergen`, `isActive`가 포함됩니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "code": "PEANUT",
      "name": "땅콩",
      "allergen": true,
      "sortOrder": 10,
      "isActive": true
    },
    {
      "id": 102,
      "code": "PORK",
      "name": "돼지고기",
      "allergen": true,
      "sortOrder": 170,
      "isActive": false
    }
  ],
  "error": null
}
```

대표 실패 기준:

- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`
- 인증 없이 호출하면 `AUTH_TOKEN_MISSING`

### 8. 관리자 ingredient 생성

- Method: `POST`
- URL: `/api/v1/admin/ingredients`
- 권한: `ADMIN`

요청 body 예시:

```json
{
  "code": "PEANUT",
  "name": "땅콩",
  "allergen": true,
  "sortOrder": 10
}
```

동작 기준:

- 생성 직후 `isActive=true` 상태로 저장합니다.
- 중복 기준은 `code`입니다.
- 성공 시 최신 단건 상태를 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 101,
    "code": "PEANUT",
    "name": "땅콩",
    "allergen": true,
    "sortOrder": 10,
    "isActive": true
  },
  "error": null
}
```

대표 실패 기준:

- 같은 `code`가 이미 있으면 `MENU_INGREDIENT_DUPLICATE`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`

### 9. 관리자 ingredient 수정

- Method: `PATCH`
- URL: `/api/v1/admin/ingredients/{ingredientId}`
- 권한: `ADMIN`

요청 body 예시:

```json
{
  "name": "새 땅콩",
  "allergen": false,
  "sortOrder": 20,
  "isActive": false
}
```

동작 기준:

- 수정 가능 필드는 `name`, `allergen`, `sortOrder`, `isActive`입니다.
- 요청에 포함하지 않은 필드는 유지합니다.
- `isActive=true`를 보내면 비활성 데이터를 다시 활성화할 수 있습니다.
- `code`는 이 API에서 수정하지 않습니다.
- 성공 시 최신 단건 상태를 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 101,
    "code": "PEANUT",
    "name": "새 땅콩",
    "allergen": false,
    "sortOrder": 20,
    "isActive": false
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `ingredientId`면 `MENU_INGREDIENT_NOT_FOUND`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`

### 10. 관리자 ingredient 비활성화

- Method: `DELETE`
- URL: `/api/v1/admin/ingredients/{ingredientId}`
- 권한: `ADMIN`

동작 기준:

- 물리 삭제가 아니라 `isActive=false` 비활성화로 처리합니다.
- 이미 비활성 상태여도 실패시키지 않고 현재 상태를 그대로 반환합니다.
- 성공 시 최신 단건 상태를 반환합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "id": 101,
    "code": "PEANUT",
    "name": "땅콩",
    "allergen": true,
    "sortOrder": 10,
    "isActive": false
  },
  "error": null
}
```

대표 실패 기준:

- 존재하지 않는 `ingredientId`면 `MENU_INGREDIENT_NOT_FOUND`
- 비관리자 회원이 호출하면 `AUTH_FORBIDDEN`

## 프론트 사용 기준

- 취향 입력 화면은 먼저 이 두 API를 조회해 선택 목록을 구성합니다.
- 취향 입력 화면에서 필요한 유형만 렌더링할 때는 `GET /api/v1/attribute-categories?categoryTypes=FLAVOR&categoryTypes=TEXTURE`처럼 `categoryTypes`를 사용할 수 있습니다.
- 제한 재료 입력 화면에서 필요한 재료만 찾을 때는 `GET /api/v1/restriction-ingredients?query=땅콩&allergen=true`처럼 `query`, `allergen`을 사용할 수 있습니다.
- 취향 저장 API에는 화면에서 선택한 ID 목록만 전달합니다.
- 비활성 참조 데이터는 응답에서 제외되므로, 클라이언트는 별도 활성 필터를 구현하지 않아도 됩니다.
- 관리자 운영 화면이나 내부 관리 도구는 관리자 목록 조회 API를 사용해 활성/비활성 상태를 함께 확인합니다.
