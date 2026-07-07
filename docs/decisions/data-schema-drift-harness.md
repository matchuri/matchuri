# Data Schema Drift Harness 설계

이 문서는 Matchuri 데이터 문서가 JPA Entity, init SQL, 개별 `docs/data/*-schema.md`와 어긋나는 문제를 줄이기 위한 harness 방향을 정리합니다.

## 배경

`docs/data/`에는 현재 구현 테이블 정의서가 있지만 일부 문서는 크고 상세합니다. 컬럼, enum, FK, unique, index 설명을 사람이 계속 맞추면 drift가 생기기 쉽습니다.

현재도 `docs/data/implemented-jpa-data-model.md`는 JPA 기준과 init SQL 기준의 충돌을 수동으로 기록합니다. 이 기록은 유용하지만, 반복 확인은 harness가 맡아야 합니다.

## 결정

- JPA Entity를 우선 implementation source로 봅니다.
- `backend/init/sql/01-schema.sql`은 local bootstrap DDL 기준으로 비교합니다.
- `docs/data/implemented-jpa-data-model.md`는 사람이 읽는 index로 유지합니다.
- 개별 `docs/data/*-schema.md`는 상세 prose보다 table contract 요약과 특이 정책만 남기는 방향으로 줄입니다.
- drift 검사는 `.agents/skills`의 script 또는 repo script로 분리합니다.

## 1차 Harness 범위

1차 script는 아래 항목만 검증합니다.

- JPA `@Entity` class와 `@Table(name = "...")` table 목록 추출
- `backend/init/sql/01-schema.sql`의 `CREATE TABLE` 목록 추출
- `docs/data/implemented-jpa-data-model.md`의 table 목록 추출
- JPA에는 있는데 init SQL에 없는 table 보고
- init SQL에는 있는데 JPA에 없는 table 보고
- JPA에는 있는데 data index에 없는 table 보고
- data index에는 있는데 JPA에 없는 table 보고

## 2차 Harness 범위

1차가 안정화된 뒤 아래를 추가합니다.

- column name drift
- nullable drift
- enum value drift
- FK drift
- unique constraint drift
- index drift
- `BaseEntity`/`CreatedAtEntity` 상속에 따른 audit column drift

## 제외

- DB vendor별 완전 DDL parser 구현
- 모든 column type의 완전 일치 판정
- 운영 DB live schema 접근
- private 운영 runbook 검증

## 출력 형식

1차 script는 Markdown report를 출력합니다.

```text
# Data Schema Drift Audit

- JPA tables: N
- init SQL tables: N
- docs index tables: N
- JPA tables missing in init SQL: N
- init SQL tables missing in JPA: N
- JPA tables missing in docs index: N
- docs index tables missing in JPA: N
```

`--strict`는 missing/drift finding이 있을 때 non-zero로 종료합니다.

## 다음 작업

- `.agents/skills/matchuri-data-schema-drift` skill 또는 기존 doc governance skill의 `scripts/` 아래에 1차 script를 추가합니다.
- script가 안정화되면 `docs/data/implemented-jpa-data-model.md`의 충돌 표를 generated report로 대체할지 판단합니다.
- 큰 data schema 문서는 table contract 요약과 특이 정책만 남기고, 반복 검증 항목은 harness report로 옮깁니다.
