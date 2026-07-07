# 추천 API

이 문서는 개인 추천 API와 비회원 개인 추천 API의 현재 계약과 구현 상태를 정리합니다.
상세 schema와 예시는 Swagger UI와 `RecommendationApi.java`의 OpenAPI 메타데이터를 함께 봅니다.

## 현재 범위

- 비회원 개인 추천 요청
- 개인 추천 이력 목록 조회
- 개인 추천 요청 생성
- 개인 추천 재요청
- 개인 추천 요청 상세 조회
- 개인 추천 후보 목록 조회
- 개인 추천 후보 선택

## 현재 상태

현재 회원 개인 추천 API는 실제 service/domain 로직과 연결되어 있습니다.
회원 개인 추천 저장 모델은 아래 테이블을 기준으로 합니다.

- `personal_recommendations`
- `personal_recommendation_candidates`
- `member_menu_actions`

비회원 개인 추천 API는 추천 이력을 저장하지 않고, 요청 취향 입력으로 계산한 후보 목록만 동기 반환합니다.

## API 목록

| Method | Path | 상태 | 설명 |
| --- | --- | --- | --- |
| POST | `/api/v1/guest/recommendations` | `real` | 비회원 개인 추천 요청 |
| GET | `/api/v1/personal/recommendations` | `real` | 내 개인 추천 이력 목록 조회 |
| POST | `/api/v1/personal/recommendations` | `real` | 개인 추천 요청 생성 |
| POST | `/api/v1/personal/recommendations/{requestId}/reroll` | `real` | 개인 추천 재요청 |
| GET | `/api/v1/personal/recommendations/{requestId}` | `real` | 개인 추천 요청 상세 조회 |
| GET | `/api/v1/personal/recommendations/{requestId}/candidates` | `real` | 개인 추천 후보 목록 조회 |
| PATCH | `/api/v1/personal/recommendations/{requestId}` | `real` | 개인 추천 후보 선택 |

## 페이지네이션 기준

개인 추천 이력 목록 조회는 공통 `PageResponse` 구조를 사용하며, `page`, `size` query parameter로 페이지를 지정합니다.

| Query parameter | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `page` | N | `0` | 0부터 시작하는 페이지 번호입니다. |
| `size` | N | `20` | 페이지 크기입니다. 최대 100까지 허용합니다. |

응답의 `pageInfo`는 실제 DB 페이지 조회 결과를 반영합니다.

## 구현 기준

- 비회원 추천은 인증 없이 호출할 수 있으며, request ID와 candidate ID를 반환하지 않습니다.
- 비회원 추천 입력의 `attributeCategoryIds`, `restrictionIngredientIds`, `dislikedMenuItemIds`는 null이면 빈 목록으로 처리합니다.
- 비회원 추천 입력에 중복 ID, 존재하지 않는 ID, 비활성 ID가 포함되면 400 응답으로 실패합니다.
- 추천 생성은 회원 취향 프로필, 제한 재료, 비선호 메뉴, 최근 선택 메뉴를 함께 반영합니다.
- 후보 저장은 `personal_recommendation_candidates` 기준으로 구현합니다.
- `PersonalRecommendationStatus`는 개인 추천 lifecycle 상태입니다. 열린 추천은 `OPEN`, 선택/재요청/만료/실패로 닫힌 추천은 각각 `SELECTED`, `REROLLED_WITH_SKIP`, `REROLLED_WITHOUT_SKIP`, `EXPIRED`, `FAILED`로 표현합니다.
- 일반 생성 충돌 판정에서의 열린 개인 추천은 `status=OPEN`, `requestedAt + 24h > now`인 요청입니다.
- 일반 개인 추천 생성은 생성 충돌 기준의 열린 추천이 있으면 `409 PERSONAL_RECOMMENDATION_OPEN_EXISTS`로 실패합니다.
- 일반 개인 추천 생성 시 24시간이 지난 미선택 추천은 요청 시점에 `status=EXPIRED`, `closedAt=now`로 전환한 뒤 새 추천을 생성합니다.
- 미선택 개인 추천은 `requestedAt + 24h` 기준으로 만료되며, 별도 주기 scheduler 없이 생성/조회/상태 변경 API 접근 시점에 lazy expire 처리합니다.
- 선택/재요청 API는 시간 기준 만료를 먼저 확정합니다. `requestedAt + 24h`가 지난 열린 추천은 `EXPIRED`로 전환한 뒤 `409 PERSONAL_RECOMMENDATION_EXPIRED`로 실패합니다.
- 개인 추천 목록/상세 조회는 시간상 만료된 열린 추천을 `EXPIRED`로 전환한 상태로 반환합니다.
- 재요청 API는 source 추천을 먼저 종료한 뒤 새 추천을 생성하므로 열린 추천 단일성 정책과 충돌하지 않습니다.
- `NOT_SATISFIED` 재요청은 source 후보 전체를 후보별 `SKIP` 로그로 저장하고 `REROLLED_WITH_SKIP`으로 종료합니다.
- `SKIP` 로그가 생성된 메뉴는 로그 생성 시각부터 24시간 동안 회원 개인 추천 후보에서 제외됩니다.
- `INPUT_CHANGED` 재요청은 `SKIP` 로그 없이 source 추천을 `REROLLED_WITHOUT_SKIP`으로 종료합니다.
- 종료된 추천은 재요청할 수 없습니다.
- 비회원/회원 추천 후보 응답에는 메뉴 대표 이미지 URL인 `thumbnailUrl`을 포함합니다. 대표 이미지가 없으면 `null`이며, 첫 구현에서는 별도 썸네일 파일 없이 원본 이미지 URL을 반환합니다.
- 사용자의 선택은 추천 결과 갱신, `status=SELECTED`, `closedAt=now`, `member_menu_actions`의 `CHOOSE` 로그 저장을 함께 수행합니다.
- `status=OPEN`이 아닌 개인 추천은 이후 후보 선택을 허용하지 않습니다.
- MVP에서는 후보별 요약 텍스트나 결과 요약 JSON을 생성하지 않습니다.

## 비회원 개인 추천 요청

```http
POST /api/v1/guest/recommendations
```

### Request

```json
{
  "attributeCategoryIds": [101, 102],
  "restrictionIngredientIds": [201],
  "dislikedMenuItemIds": [301],
  "contextJson": {
    "mealTime": "LUNCH",
    "budgetLevel": 2
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "candidates": [
      {
        "menuId": 1001,
        "menuName": "비빔밥",
        "thumbnailUrl": "https://asset.matchuri.com/menu-items/1001/sample.jpg",
        "rankNo": 1,
        "score": 93.5
      }
    ]
  },
  "error": null
}
```

## 회원 개인 추천 응답 공통 필드

생성, 상세, 목록, 선택 응답은 추천 종료 판단을 위해 아래 필드를 포함합니다.

후보 응답의 `score`는 프론트 노출용 0~100 정규화 추천 점수입니다. 알고리즘 원점수는 API에 노출하지 않습니다.

| Field | Type | 설명 |
| --- | --- | --- |
| `status` | `string` | 개인 추천 lifecycle 상태입니다. 현재 enum은 `OPEN`, `SELECTED`, `REROLLED_WITH_SKIP`, `REROLLED_WITHOUT_SKIP`, `EXPIRED`, `FAILED`입니다. |
| `closedAt` | `datetime \| null` | 추천이 선택, 재요청, 만료, 실패 등으로 종료된 시각입니다. `OPEN`이면 `null`입니다. |

사용자가 아직 선택 또는 재요청 가능한지 여부는 `status == OPEN`이고 `requestedAt + 24h > now`인지를 함께 기준으로 판단합니다.

## 개인 추천 요청 생성 실패

열린 개인 추천이 이미 있으면 일반 생성 API는 새 추천을 만들지 않습니다.

```json
{
  "success": false,
  "data": null,
  "error": {
    "status": 409,
    "code": "PERSONAL_RECOMMENDATION_OPEN_EXISTS",
    "message": "이미 열린 개인 추천이 있습니다. personalRecommendationId : 9001",
    "details": []
  }
}
```

시간상 만료된 개인 추천을 선택하거나 재요청하면 아래와 같이 실패합니다.

```json
{
  "success": false,
  "data": null,
  "error": {
    "status": 409,
    "code": "PERSONAL_RECOMMENDATION_EXPIRED",
    "message": "만료된 개인 추천입니다. personalRecommendationId : 9001",
    "details": []
  }
}
```

## 개인 추천 재요청

```http
POST /api/v1/personal/recommendations/{requestId}/reroll
```

### Request

```json
{
  "rerollType": "NOT_SATISFIED",
  "contextJson": {
    "mealTime": "LUNCH",
    "mood": "다른 메뉴"
  }
}
```

`rerollType`은 아래 값을 사용합니다.

| Value | 처리 |
| --- | --- |
| `NOT_SATISFIED` | 이전 추천 후보 전체를 `SKIP` 로그로 저장하고 source 추천을 `REROLLED_WITH_SKIP`으로 종료합니다. 저장된 `SKIP` 메뉴는 24시간 동안 후보에서 제외됩니다. |
| `INPUT_CHANGED` | `SKIP` 로그 없이 source 추천을 `REROLLED_WITHOUT_SKIP`으로 종료합니다. |

### Response

응답 구조는 개인 추천 요청 생성과 동일합니다.
