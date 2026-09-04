# API 쿼리 성능 Before 기준선

이 문서는 QueryDSL 기반 조회 개선 전 API 쿼리 상태를 기록한다.
수치는 test 프로필의 H2 데이터베이스와 datasource-proxy 요청 단위 카운터로 측정했다.

## 측정 기준

- 측정일: 2026-09-04
- 측정 범위: 정상 응답을 반환하는 핵심 메뉴, 회원 취향, 추천, 그룹 조회·생성 API
- 측정 경계: HTTP 요청 진입부터 응답 완료까지 실행된 JDBC statement
- 데이터 준비와 검증용 repository 호출은 요청 전에 실행하므로 집계에서 제외
- total, select, insert, update, delete, other, jdbcMs를 요청별 한 줄 로그로 기록
- H2의 jdbcMs는 기능 회귀를 위한 참고값일 뿐 MySQL 성능 비교 기준으로 사용하지 않음
- 실제 반환 행 수, rows examined, 실행계획과 카테시안 곱 여부는 MySQL EXPLAIN ANALYZE 단계에서 별도 측정

계측 로그 형식은 다음과 같다.

~~~text
API_QUERY_BEFORE method=GET uri=/api/v1/... status=200 total=... select=... insert=... update=... delete=... other=... jdbcMs=...
~~~

## N+1 규모 측정

| API | 작은 fixture | SQL | 큰 fixture | SQL | 판정 |
| --- | --- | ---: | --- | ---: | --- |
| GET /api/v1/menu-items/{id} | category 1, ingredient 1 | 6 SELECT | category 12, ingredient 12 | 28 SELECT | N+1 확인, 연관 항목 1개마다 SELECT 1회씩 증가 |
| POST /api/v1/guest/recommendations | menu 1, 반환 후보 1 | 7 SELECT | menu 12, 반환 후보 3 | 20 SELECT | N+1 확인, 메뉴 profile 조립과 후보 이미지 조회 영향 |
| GET /api/v1/personal/recommendations/{id}/candidates | candidate 1 | 5 SELECT | candidate 12 | 27 SELECT | N+1 확인, 후보 1개 증가마다 SELECT 2회 증가 |
| GET /api/v1/groups | group 1 | 5 SELECT | group 12 | 16 SELECT | N+1 확인, 그룹별 최신 추천 상태 조회가 1회씩 증가 |

현재 측정식은 다음과 같이 재현됐다.

~~~text
메뉴 상세              Q(category, ingredient) = 4 + category + ingredient
개인 추천 후보 목록    Q(candidate)            = 3 + 2 * candidate
내 그룹 목록           Q(group)                = 4 + group
~~~

비회원 추천은 반환 후보가 최대 3개로 제한되므로 메뉴 profile 조립 쿼리와 반환 후보 이미지 쿼리가 함께 증가한다.

### 확인된 반복 조회 지점

- 메뉴 상세는 mapping 목록을 조회한 뒤 각 mapping의 attributeCategory와 ingredient 지연 연관을 접근한다. 현재 상세용 repository 메서드에는 fetch join이 없다.
- 비회원 추천은 전체 메뉴를 순회하며 menuAttributeCategories를 접근하고, 반환 후보마다 MenuThumbnailUrlResolver.resolve를 호출한다.
- 개인 추천 후보 목록은 각 candidate의 menuItem을 접근하고 후보마다 MenuThumbnailUrlResolver.resolve를 호출한다.
- 내 그룹 목록은 각 room마다 GroupRecommendationExpirationManager.latestRecommendationStatus를 호출한다.

## 대표 API Before

아래 값은 명시된 fixture에 대한 현재 정상 흐름의 단일 실행 결과다.
상태나 page size가 다른 요청은 별도 기준선으로 취급한다.

### Menu·Member

| API | 대표 fixture | Total | SELECT | 비고 |
| --- | --- | ---: | ---: | --- |
| GET /api/v1/attribute-categories | active 3, inactive 1 | 1 | 1 | 단일 목록 조회 |
| GET /api/v1/restriction-ingredients | active 3, inactive 1 | 1 | 1 | 단일 목록 조회 |
| GET /api/v1/menu-items | 필터 없음, active menu 2 | 1 | 1 | 단일 검색 조회 |
| GET /api/v1/menu-items | category·ingredient 필터 사용 | 3 | 3 | 필터 ID 검증 2회 포함 |
| GET /api/v1/menu-items/{id} | category 1, ingredient 1 | 6 | 6 | 규모 증가 시 N+1 |
| GET /api/v1/members/me/taste-profile | category·restriction·dislike 선택값 존재 | 5 | 5 | profile과 세 종류 매핑 조회 |

### Personal recommendation·Home

| API | 대표 fixture | Total | SELECT | INSERT | UPDATE | 비고 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| POST /api/v1/guest/recommendations | menu 4, 반환 후보 2 | 11 | 11 | 0 | 0 | 메뉴 수 증가 시 N+1 |
| POST /api/v1/personal/recommendations | menu 3, 반환 후보 2 | 15 | 12 | 3 | 0 | 추천 및 후보 저장 포함 |
| GET /api/v1/personal/recommendations/{id} | candidate 2, OPEN | 6 | 6 | 0 | 0 | 상세 응답 |
| GET /api/v1/personal/recommendations/{id}/candidates | candidate 2 | 7 | 7 | 0 | 0 | 후보 수 증가 시 N+1 |
| GET /api/v1/personal/recommendations | recommendation 1, page size 10 | 3 | 3 | 0 | 0 | content와 count 포함 |
| PATCH /api/v1/personal/recommendations/{id} | 후보 선택 | 5 | 3 | 1 | 1 | 행동 로그와 추천 상태 변경 |
| GET /api/v1/home | 최근 선택 추천 3개와 그룹 활동 포함 | 13 | 13 | 0 | 0 | 조합 API 중 높은 고정 비용 |

### Group

| API | 대표 fixture | Total | SELECT | INSERT | 비고 |
| --- | --- | ---: | ---: | ---: | --- |
| POST /api/v1/groups/{id}/recommendations | OWNER가 PREPARING 생성 | 9 | 8 | 1 | 준비 세션 생성 |
| GET /api/v1/groups | group 1 | 5 | 5 | 0 | 그룹 수 증가 시 N+1 |
| GET /api/v1/groups/{id} | 최근 OPEN 추천 포함 | 15 | 15 | 0 | 현재 가장 높은 조회 비용 |
| GET /api/v1/groups/{id}/recommendations | recommendation page | 5 | 5 | 0 | content와 count 포함 |
| GET /api/v1/groups/{id}/recommendations/{sessionId} | PREPARING | 6 | 6 | 0 | readiness progress 포함 |
| GET /api/v1/groups/{id}/recommendations/{sessionId} | OPEN | 13 | 13 | 0 | 후보·투표·멤버 조립 |
| GET /api/v1/groups/{id}/recommendations/{sessionId}/candidates | 후보와 투표 수 포함 | 8 | 8 | 0 | 후보 응답 조립 |
| GET /api/v1/groups/{id}/recommendations/{sessionId}/readiness | 활성 멤버 readiness 포함 | 9 | 9 | 0 | 멤버·준비 상태·진행률 |
| GET /api/v1/groups/invites/me | PENDING page | 3 | 3 | 0 | content와 count 포함 |

## 우선 개선 대상

1. GET /api/v1/personal/recommendations/{id}/candidates
2. GET /api/v1/menu-items/{id}
3. GET /api/v1/groups
4. POST /api/v1/guest/recommendations
5. GET /api/v1/groups/{id}와 OPEN 그룹 추천 상세
6. GET /api/v1/home

1~4번은 fixture 규모 증가에 따라 SQL 수가 선형 증가하는 것이 확인됐다.
5~6번은 현재 단일 요청의 고정 SELECT 수가 높아 쿼리 통합 후보로 분류한다.

## 재현

규모별 baseline 테스트:

~~~powershell
./gradlew test --tests "*measure*BeforeOptimization" --quiet
Select-String -Path "build/test-results/test/*.xml" -Pattern "API_QUERY_BEFORE" |
    ForEach-Object { [regex]::Match($_.Line, "API_QUERY_BEFORE.*").Value }
~~~

rg가 설치된 환경에서는 기존과 같이 다음 명령을 사용할 수 있다.

~~~powershell
rg "API_QUERY_BEFORE" build/test-results/test
~~~

대표 정상 흐름은 다음 통합 테스트에서 재현한다.

- MenuReferenceIntegrationTest
- MemberAuthIntegrationTest
- GuestRecommendationIntegrationTest
- PersonalRecommendationIntegrationTest
- GroupIntegrationTest
- HomeIntegrationTest

로컬 실행에서 동일한 요청 단위 집계를 사용하려면 다음 속성을 활성화한다.

~~~text
--matchuri.query-monitor.enabled=true
~~~

## After 비교 규칙

- 같은 fixture와 API 상태를 사용한다.
- 응답 payload와 정렬 순서를 유지한다.
- 작은 fixture와 큰 fixture의 SQL 수가 같거나, 페이지 count처럼 명시된 고정 차이만 허용한다.
- 여러 to-many 연관을 한 쿼리로 합칠 때는 MySQL actual rows가 연관 크기의 곱으로 증가하지 않는지 확인한다.
- H2 jdbcMs의 단발성 증감으로 개선 여부를 판단하지 않는다.
