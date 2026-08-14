# Seed 데이터 전략

이 문서는 Matchuri 백엔드의 기준 데이터와 로컬 샘플 데이터 초기화 기준을 정리합니다.

## 목표

- JPA Entity를 스키마 생성의 단일 기준으로 사용합니다.
- 추천 기능에 필요한 기준 데이터를 모든 런타임 환경에서 준비합니다.
- 로컬 수동 테스트용 샘플 데이터는 운영 환경과 분리합니다.
- 반복 기동에도 기존 데이터를 덮어쓰거나 중복 생성하지 않습니다.

## 데이터 분류

### 기준 데이터

- `attribute_categories`
- `ingredients`
- `menu_items`
- 메뉴-속성/재료 매핑

기준 데이터는 `backend/src/main/resources/seed/reference-data.json`에서 관리합니다.
`ReferenceDataSeedRunner`는 `test`를 제외한 프로필에서 실행하며 자연 키 기준으로 누락 항목만 생성합니다.

### 로컬 샘플 데이터

- `tester01`~`tester04`, `admin01`
- 샘플 약관 동의와 취향 프로필
- 샘플 그룹과 구성원, 위치

로컬 샘플 데이터는 `backend/src/main/resources/seed/local-sample-data.json`에서 관리합니다.
`LocalSampleDataSeedRunner`는 `local`이면서 `test`가 아닌 경우에만 실행합니다.

## 실행 순서와 실패 처리

1. Hibernate `ddl-auto`가 JPA Entity 기준으로 스키마를 준비합니다.
2. 기준 데이터 Runner가 실행됩니다.
3. `local`에서는 로컬 샘플 데이터 Runner가 이어서 실행됩니다.
4. 리소스가 잘못됐거나 참조 데이터가 누락되면 기동을 실패시킵니다.

별도 활성화 프로퍼티는 두지 않고 Spring profile만으로 실행 범위를 제어합니다.

## 멱등성 및 변경 원칙

- category는 `categoryType + code`, ingredient와 menu는 `code`를 자연 키로 사용합니다.
- 매핑은 양쪽 자연 키 조합으로 중복을 방지합니다.
- 기존 행의 이름, 설명, 활성 상태, 정렬 순서는 자동으로 덮어쓰지 않습니다.
- 리소스에 있는 누락 데이터와 누락 매핑만 생성합니다.
- seed 과정에서 기존 행이나 매핑을 삭제하지 않습니다.
- 기준 데이터 변경을 기존 DB에 강제로 동기화해야 하면 관리자 기능이나 별도 변경 작업으로 수행합니다.

## 이미지 제외

- `image_assets`와 `menu_item_images`는 seed 대상이 아닙니다.
- 메뉴 대표 이미지는 관리자 업로드 흐름으로만 생성합니다.
- JSON seed 리소스에는 image, thumbnail, object key를 두지 않습니다.

## 현재 로컬 샘플 범위

- 네 명의 일반 회원과 한 명의 관리자 회원을 생성합니다.
- 일반 회원별 취향, 제한 재료, 비선호 메뉴를 준비합니다.
- 두 개의 활성 그룹과 구성원, 위치를 준비합니다.
- 추천 결과, 투표 결과, 재요청 로그는 생성하지 않습니다.

## 검증

- 기준 데이터와 로컬 샘플 초기화를 각각 두 번 실행해 멱등성을 확인합니다.
- seed 후 기준 데이터와 매핑 건수를 확인합니다.
- `menu_item_images`가 생성되지 않는지 확인합니다.
