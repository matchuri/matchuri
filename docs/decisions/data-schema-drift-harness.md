# Data Schema Drift Harness 설계

이 문서는 JPA Entity와 `docs/data/*-schema.md`가 어긋나는 문제를 줄이기 위한 harness 방향을 정리합니다.

## 결정

- JPA Entity를 스키마의 implementation source로 봅니다.
- 별도 init SQL 또는 DDL snapshot은 유지하지 않습니다.
- `docs/data/implemented-jpa-data-model.md`는 사람이 읽는 테이블 index로 유지합니다.
- 기준 데이터 정합성은 `ReferenceDataSeedService` 통합 테스트로 검증합니다.

## Harness 범위

1차 script는 아래 항목을 검증합니다.

- JPA `@Entity`와 `@Table(name = "...")` 테이블 목록 추출
- `docs/data/implemented-jpa-data-model.md`의 테이블 목록 추출
- JPA에는 있는데 data index에 없는 테이블 보고
- data index에는 있는데 JPA에 없는 테이블 보고

통합 테스트는 아래 항목을 검증합니다.

- 기준 데이터와 매핑의 전체 건수
- 기준 데이터 초기화의 멱등성
- 로컬 샘플 데이터 초기화의 멱등성
- 메뉴 대표 이미지 seed 미생성

## 후속 범위

- column name과 nullable drift
- enum 값 drift
- FK와 unique constraint drift
- `BaseEntity`/`CreatedAtEntity` 상속에 따른 audit column drift
- 실제 MySQL에서 생성된 schema와 JPA metadata 비교

성능 인덱스는 사전 선언 목록으로 관리하지 않습니다. 실제 쿼리와 실행 계획을 비교한 뒤 도입합니다.

## 제외

- 별도 SQL DDL snapshot 생성
- DB vendor별 완전 DDL parser 구현
- 운영 DB live schema 접근
- private 운영 runbook 검증
