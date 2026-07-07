# Seed 데이터 전략

이 문서는 Matchuri 백엔드의 로컬/개발 환경용 시드 데이터 운영 기준을 정리합니다.
목적은 API를 빠르게 검증할 수 있게 하면서도, 운영 환경 오염이나 중복 데이터 누적을 막는 것입니다.

## 목표

- 로컬 환경에서 API를 바로 테스트할 수 있게 한다.
- 기준 데이터와 샘플 데이터를 구분한다.
- 운영 환경에는 자동 시드가 들어가지 않도록 한다.
- 같은 초기화가 반복 실행돼도 데이터가 중복 생성되지 않게 한다.

## 기본 원칙

- 시드 데이터는 `local`, `dev` 같은 개발 환경 전용으로 사용합니다.
- `prod`에서는 자동 실행하지 않습니다.
- 초기화는 멱등하게 작성합니다.
- 기준 데이터와 샘플 데이터를 한 클래스에 무분별하게 섞지 않습니다.

## 데이터 분류

### 1. 기준 데이터

- 의미: 도메인 규칙이나 API 검증의 기준이 되는 데이터
- 예:
  - `attribute_categories`
  - 일부 `ingredients`

특징:

- 서비스 규칙과 강하게 연결됩니다.
- 장기적으로는 Flyway 같은 마이그레이션 기반으로 이동할 수 있습니다.

### 2. 샘플 데이터

- 의미: 로컬 개발과 수동 API 테스트 편의를 위한 데이터
- 예:
  - 테스트 회원
  - 샘플 메뉴
  - 샘플 그룹

특징:

- 개발 편의성 중심입니다.
- 운영 데이터와 동일한 신뢰 수준으로 취급하지 않습니다.

## 권장 구조

로컬 Docker Compose DB 초기화는 MySQL entrypoint SQL로 관리합니다.

```text
backend/init/sql/
  01-schema.sql
  02-reference-seed.sql
  03-local-sample-seed.sql
```

## 실행 조건

- Docker Compose DB volume이 비어 있을 때 `backend/init/sql/*.sql`을 통해 테이블과 기준/샘플 seed를 준비합니다.
- init SQL은 `01-schema.sql`, `02-reference-seed.sql`, `03-local-sample-seed.sql`처럼 실행 순서와 책임이 보이도록 분리합니다.
- MySQL 공식 entrypoint는 `/docker-entrypoint-initdb.d` 직하위 SQL만 실행하므로, compose는 `backend/init/sql`을 직접 마운트합니다.
- 애플리케이션 기동 시점의 ApplicationRunner seed는 사용하지 않습니다.
- `staging`, `production`에서는 기본 비활성화

## 멱등성 기준

- 유니크 키가 있는 데이터는 SQL의 `ON DUPLICATE KEY UPDATE`로 멱등성을 보장합니다.
- 중복 생성이 발생할 수 있는 샘플 데이터는 식별 가능한 키를 기준으로 재사용
- "항상 새로 insert" 방식은 금지

## 초기 시드 데이터 우선순위

### 1차

- `attribute_categories`
- `ingredients`

### 2차

- `menu_items`
- 메뉴-속성/재료 매핑

### 3차

- 테스트 회원 1~2명
- 필요 시 회원 취향 프로필

### 이후

- 그룹 샘플 데이터
- 추천 샘플 데이터

## 현재 로컬 샘플 데이터 범위

- 로컬 샘플 데이터는 `backend/init/sql/03-local-sample-seed.sql`에서 관리합니다.
- 현재 샘플 회원은 `tester01`~`tester04`, `admin01`입니다.
- `tester01`~`tester04`는 개인 추천과 그룹 추천 수동 테스트를 위해 서로 다른 취향 프로필을 가집니다.
- 샘플 그룹은 이미 성사된 `ACTIVE` 그룹과 `ACTIVE` 구성원 중심으로 둡니다.
- 취향 프로필 샘플은 기존 로컬 데이터를 강제로 초기화하지 않고, 누락된 샘플 매핑만 추가합니다.
- 추천 결과, 투표 결과, 재요청 로그는 시드하지 않습니다. 이 데이터는 API 수동 테스트에서 생성합니다.

## 현재 판단

- 지금 단계에서는 `loginId` 중복 확인 API 같은 공개 API 검증을 위해 테스트 회원 시드가 특히 유용합니다.
- 취향/추천/메뉴 API가 늘어날수록 기준 데이터의 가치가 커집니다.
- 운영 데이터 오염을 막기 위해 실행 프로필 제한은 필수입니다.

## 보류 항목

- 기준 데이터를 언제 Flyway 같은 DB 마이그레이션으로 승격할지
