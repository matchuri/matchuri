# 도메인 용어 사전

이 문서는 Matchuri에서 자주 쓰는 핵심 도메인 용어를 정리합니다.
목적은 사람과 에이전트가 같은 말을 같은 의미로 사용하게 만드는 것입니다.
특히 비슷해 보이는 용어를 섞어 쓰지 않도록 기준을 둡니다.

## 사용 원칙

- 코드, API, 문서, DB에서 가능한 한 같은 용어를 사용합니다.
- 이미 정해진 용어가 있으면 새 표현을 만들기보다 기존 용어를 재사용합니다.
- 아직 미정인 개념은 억지로 확정하지 않고 `TBD`로 남깁니다.

## 핵심 제품 용어

### Matchuri

- 의미: 개인과 그룹이 점심 메뉴를 더 빠르게 결정하도록 돕는 서비스
- 주의: 맛집 검색 서비스로 축소해서 설명하지 않음

### 메뉴 결정

- 의미: 무엇을 먹을지 최종 메뉴를 정하는 과정
- 주의: 단순 추천 결과 노출과 다름

### 그룹 의사결정

- 의미: 여러 사용자의 취향과 투표를 반영해 하나의 메뉴를 정하는 과정
- 주의: 단순 다수결만을 뜻하지 않음

## 회원/인증 영역

### Member

- 의미: 서비스 사용자 계정
- 포함: 로그인 ID, 비밀번호 해시, 이메일, 역할, 상태, 소셜 여부
- 주의: 취향 정보 전체를 `Member` 안에 직접 넣지 않음
- 주의: 필수 약관 동의 이력은 `Member`에 직접 누적하지 않음

### Member Agreement

- 의미: 회원이 특정 약관 타입의 특정 버전에 동의한 기록
- 포함: 약관 종류, 약관 버전, 동의 시각
- 주의: 회원 상태값 자체가 아니라, 서비스 이용 가능 상태를 판단하는 근거 데이터

### Agreement Type

- 의미: 회원이 동의해야 하는 약관의 종류
- 현재 값: `TERMS_OF_SERVICE`, `PRIVACY_POLICY`

### Required Agreement Completion

- 의미: 회원이 현재 필수 약관 2종의 최신 필수 버전에 모두 동의한 상태
- 주의: 로그인 성공과 같은 의미가 아님

### Member Taste Profile

- 의미: 회원의 취향 및 제한 재료 정보를 담는 별도 프로필
- 주의: 회원 계정 정보와 분리된 1:1 구조로 관리

### Role

- 의미: 회원 권한 수준
- 현재 값: `MEMBER`, `ADMIN`

### Status

- 의미: 회원의 현재 상태
- 현재 값: `ACTIVE`, `INACTIVE`

## 취향/메뉴 분류 영역

### Attribute Category

- 의미: 메뉴 특성과 회원 취향이 함께 참조하는 공통 속성 카테고리
- 예: 맛, 조리 방식, 음식 종류, 식감, 온도감
- 주의: 회원 취향과 메뉴 특성을 따로 분리된 분류 체계로 만들지 않음

### Category Type

- 의미: 속성 카테고리의 상위 유형
- 현재 값: `FLAVOR`, `COOKING_METHOD`, `FOOD_CATEGORY`, `TEXTURE`, `TEMPERATURE`

### Restriction Ingredient

- 의미: 사용자가 피하고 싶은 재료 또는 제한 재료
- 주의: 일반 취향 카테고리와 섞지 않고 재료 기준으로 별도 정규화

### Disliked Menu Item

- 의미: 사용자가 선호하지 않는 메뉴 단위 항목
- 주의: MVP 5단계 개인 추천에서는 `restriction ingredient`와 마찬가지로 후보에서 제외하는 조건으로 다룸
- 주의: 자유 텍스트가 아니라 활성 `MenuItem` 검색/선택 결과의 ID 목록으로 저장

### Ingredient

- 의미: 메뉴를 구성하는 재료 마스터
- 주의: 알레르기 여부를 함께 가질 수 있음

### Menu Item

- 의미: 추천 가능한 메뉴의 기본 단위
- 주의: 음식점(place)이 아니라 메뉴(menu) 중심

## 개인 추천 영역

### Personal Recommendation

- 의미: 개인 추천 실행 이력
- 주의: 단순 조회 요청이 아니라 상태를 가지는 추천 실행 단위

### Recommendation Context

- 의미: 개인 추천이나 그룹 추천마다 달라질 수 있는 상황 정보
- 예: `mealTime`
- 현재 `MealTime` 값: `BREAKFAST`, `LUNCH`, `DINNER`, `NIGHT_SNACK`
- 주의: 회원 취향 프로필의 `attribute category`가 아니며, 추천 실행 단위 입력으로 다룸

### Personal Recommendation Candidate

- 의미: 개인 추천에서 생성된 후보 메뉴
- 주의: 최종 선택 결과와 구분

### Selected Candidate

- 의미: 사용자가 최종적으로 선택한 후보
- 주의: 후보 목록 중 하나여야 하며 임의 메뉴가 아님

### Member Menu Action

- 의미: 추천 이후 사용자의 클릭, 좋아요, 선택, 스킵 같은 행동 로그
- 주의: 추천 엔진 개선을 위한 후속 데이터이기도 함

## 그룹 영역

### Group Room

- 의미: 함께 메뉴를 정하기 위한 그룹 방
- 포함: 그룹명, 방장, 위치 정보, 상태
- 주의: 일반 채팅방 개념과 비슷하지만 목적은 메뉴 결정

### Group Member

- 의미: 그룹 방에 속한 회원의 멤버십 정보
- 포함: 역할, 상태, 입장/퇴장 시각

### Group Invite

- 의미: 그룹 참여를 위한 초대 코드 또는 초대 링크 정보
- 주의: 만료/폐기 상태를 가질 수 있음

## 그룹 추천/투표 영역

### Group Recommendation

- 의미: 그룹 단위 추천과 투표가 진행되는 실행 단위
- 현재 상태값: `OPEN`, `CLOSED`, `FINALIZED`, `CANCELED`
- 주의: 그룹 방 자체와 그룹 추천 실행 단위는 다름

### Group Recommendation Candidate

- 의미: 그룹 추천에서 제시된 후보 메뉴
- 주의: 그룹 추천 단위로 관리되며, 같은 메뉴라도 그룹 추천이 다르면 별도 후보임

### Group Recommendation Vote

- 의미: 그룹 멤버가 특정 후보에 남긴 투표 기록
- 주의: 중복 투표 방지 제약이 필요함

### Final Menu

- 의미: 그룹 추천에서 최종 확정된 메뉴
- 주의: 추천 후보 중 하나여야 함

## 상태/흐름 관련 용어

### Personal Recommendation

- 의미: 개인 사용자가 시작한 추천 실행 단위
- 예: `personal_recommendations`

### Group Recommendation

- 의미: 여러 참여자와 상태 전이가 포함된 그룹 추천 실행 단위
- 예: `group_recommendations`

### Candidate

- 의미: 추천 결과로 제시되는 후보 항목
- 주의: 최종 결과와 구분

### Vote

- 의미: 후보에 대한 사용자 선택 기록
- 주의: 추천 결과 자체가 아니라 합의 과정의 데이터

## 혼용하지 말아야 할 표현

- `group room`과 `group recommendation`을 같은 의미로 쓰지 않음
- `menu`와 `place`를 같은 의미로 쓰지 않음
- `taste profile`과 `member`를 같은 데이터 덩어리로 보지 않음
- `candidate`와 `selected candidate`를 같은 의미로 쓰지 않음
- `attribute category`와 `ingredient`를 같은 분류 체계로 보지 않음
- MVP 5단계 개인 추천에서는 `restriction ingredient`와 `disliked menu item`을 모두 후보 제외 조건으로 본다.

## 현재 기준에서 미정인 표현

- `refresh token`의 저장/무효화 정책
- `logout`의 정확한 서버 의미
- 실시간 상태 공유 관련 세부 용어

이 항목들은 추후 확정되면 이 문서에 추가합니다.
