# 홈 API

홈 화면은 별도 영속 도메인을 만들지 않고 회원, 개인 추천, 그룹 도메인의 현재 데이터를 조합합니다. 정확한 경로, API ID, schema와 예시는 backend의 `CommonApi.java`, `HomeResponse.java` 및 Swagger/OpenAPI를 기준으로 확인합니다.

## 접근과 구성

- Bearer 인증과 필수 약관·닉네임 온보딩을 완료한 활성 회원만 조회할 수 있습니다.
- `CommonController -> CommonApplicationService -> MemberService / RecommendationService / GroupService -> 각 repository` 흐름을 사용합니다.
- `CommonApplicationService`가 각 도메인 서비스의 Result를 수집하고 `HomeMapper`를 호출해 `HomeResponse`를 반환합니다. 중간 집계 모델인 HomeResult는 사용하지 않습니다.
- `CommonController`는 application service가 반환한 Response를 공통 envelope로 감싸기만 하며 Mapper를 직접 호출하지 않습니다.
- application service는 repository에 직접 접근하지 않습니다. 각 도메인 서비스의 Result 경계는 유지하고, 화면용 Response 조립 책임만 application service가 가집니다.
- 전체 응답은 기존 `success/data/error` envelope를 유지합니다. 일부 도메인 조회가 실패하면 빈 성공 데이터로 숨기지 않고 전체 요청이 실패합니다.
- 조회 중 개인/그룹 추천의 lazy expiration을 반영할 수 있으므로 application service의 트랜잭션은 read-only가 아닙니다.

## 화면 컴포넌트 계약

- `user`: 사용자명은 nickname이며 현재 프로필 이미지 URL을 포함합니다. 프로필 이미지 미설정은 null입니다. 이메일·로그인 ID는 포함하지 않습니다.
- `personalRecommendation`: 상태와 무관한 최신 개인 추천의 ID·상태입니다. 추천 요청 시각 내림차순, 같은 시각은 ID 내림차순으로 결정합니다. 이력이 없으면 두 필드는 null입니다.
- `location`: 저장된 검색 기준 위치의 경도·위도·주소입니다. GPS 현재 위치가 아니며 미설정이면 섹션 전체가 null입니다. 검색 반경은 이번 계약에서 제외합니다.
- `tasteProfile.attributeCategories`: 선택한 취향 카테고리 전체를 기존 취향 조회 표시 순서로 제공합니다. 제한 재료·비선호 메뉴는 제외합니다. 육류 선호 등 새 분류는 추가하지 않습니다.
- `personalRecommendationHistory.items`: SELECTED 추천만 추천 요청 시각 내림차순, 같은 시각은 ID 내림차순으로 최대 3개 제공합니다. 페이징 입력·메타데이터는 없습니다. `createdAt`은 추천 요청 시각(requestedAt)이며 선택 완료 시각이 아닙니다.
- 개인 기록의 `selectedMenu.name`은 조회 당시 최신 메뉴명입니다. `selectedMenu.attributeCategories`는 해당 메뉴의 현재 활성 속성 전체이며 categoryType, sortOrder, ID 순서입니다. 한식 등 음식 분류만 필요한 UI는 FOOD_CATEGORY를 선택해서 표시할 수 있습니다. 비활성 메뉴라도 선택 이력은 유지합니다. 메뉴 이미지 URL이나 자동 수식어는 제공하지 않습니다.
- `recentGroupActivities.items`: 현재 ACTIVE 가입 상태이고 삭제되지 않은 모든 그룹을 대상으로 그룹별 최신 추천 1건씩 제공합니다. 추천이 없는 그룹, 탈퇴·강퇴된 그룹은 제외합니다. 그룹 방의 CLOSED 상태 자체는 제외 조건이 아닙니다. 그룹 수 제한·페이징은 없으며 추천 준비 세션 시작 시각 내림차순, 같은 시각은 추천 ID 내림차순입니다.
- 모든 목록은 데이터가 없으면 빈 배열입니다. 화면 문구·색상·아이콘·상대시간·이동 URL은 클라이언트 책임이며 그룹 상세 이동에는 groupId를 사용합니다.

## 그룹 타입 해석

그룹 활동은 과거 이벤트 타임라인이 아니라 최신 추천 상태의 요약입니다. 같은 그룹의 여러 사건을 각각 쌓아 반환하지 않습니다.

| type | 의미 | details.selectedMenuName |
| --- | --- | --- |
| PREPARING | 그룹 추천 준비 중 | null |
| OPEN | 후보 생성 완료, 투표/최종 확정 대기 | null |
| FINALIZED | 그룹장이 최종 확정 | 최신 확정 메뉴명 |
| EXPIRED | 미완료 추천이 24시간 이후 만료 | null |
| CANCELED / FAILED / REROLLED_WITH_SKIP / REROLLED_WITHOUT_SKIP | 해당 종료 상태 | null |

- `details`는 추천 ID, startedAt, endedAt, selectedMenuName의 고정 구조입니다. 타입별 해당하지 않는 선택 메뉴명은 null입니다.
- startedAt은 준비 세션 시작 시각이며 투표 시작 시각을 의미하지 않습니다.
- endedAt은 저장된 종료 시각입니다. lazy expiration이면 API가 만료를 처리한 시각이지 최초 만료 예정 시각이나 투표 종료 시각이 아닙니다.
- 전원 투표 완료도 그룹장이 확정하기 전에는 OPEN입니다. 이 API만으로 전원 투표 완료 여부를 표시하지 않습니다.
- 시간은 기존 API와 동일한 LocalDateTime 직렬화를 사용합니다. 상대시간 표시는 클라이언트가 담당하고, 별도 시간대/offset 필드는 추가하지 않습니다.

## 구현과 후속 범위

- 개인 기록은 DB에서 SELECTED 필터와 3개 제한을 적용합니다. 전체 이력을 가져온 뒤 자르지 않습니다.
- 선택 메뉴 카테고리는 일괄 조회하고 그룹 최신 추천은 한 번의 조회로 가져옵니다. 그룹마다 상세 API를 반복 호출하지 않습니다.
- 새로운 엔티티·스키마 migration은 없습니다. 기존 API의 응답 계약은 변경하지 않습니다.
- frontend 연동은 별도 작업입니다. 컴포넌트별 DTO 매핑, OPEN일 때 이어보기, null/빈 배열 상태, 그룹 타입 분기 및 저장 위치 수정 후 Home 재조회가 필요합니다.
- 알림함·읽음 상태·영속 활동 이력·투표 시작 시각·전원 투표 완료 표시가 필요하면 별도 계약 확장이 필요합니다.
- 그룹 수가 많아지면 응답 크기와 최신 추천 조회 실행 계획을 측정해 인덱스 또는 목록 제한·커서 도입 여부를 결정합니다.
