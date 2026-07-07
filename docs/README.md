# Matchuri Development Docs

`docs/`는 Matchuri의 개발 기준 문서입니다. 제품 판단, 프론트엔드, 백엔드, API, 데이터, 설계 결정처럼 구현과 함께 계속 맞춰야 하는 기준을 한곳에서 찾을 수 있게 유지합니다.

사람이 읽는 프로젝트 소개, 포트폴리오용 설명, 협업 안내는 GitHub Wiki에서 관리합니다. 운영 런북과 실행 계획 기록은 공개 문서에서 제외하고 내부 문서로 관리합니다.

반복되는 에이전트 작업 절차는 `.agents/skills/`로, 기계적으로 검증할 수 있는 문서 규칙은 harness script나 테스트로 분리합니다.

## 빠른 시작

작업 전에 모든 문서를 읽지 말고 목적에 맞는 진입점만 엽니다.

- 제품 판단: `docs/product/index.md`
- 프론트엔드 구현: `docs/frontend/index.md`
- 백엔드 구현: `docs/backend/index.md`
- API 계약/상태: `docs/api/index.md`
- 데이터 모델: `docs/data/index.md`
- 설계 결정: `docs/decisions/index.md`

## 작업별 진입점

### 제품/도메인 판단

1. `docs/product/product-sense.md`
2. `docs/product/specs/index.md`
3. `docs/decisions/domain-language.md`

### 프론트엔드 작업

1. `docs/frontend/guide.md`
2. 관련 API 문서 또는 `docs/api/index.md`

### 백엔드 기능 구현

1. `docs/backend/guide.md`
2. `docs/backend/architecture.md`
3. 관련 도메인의 `docs/api/*.md`
4. 관련 데이터 문서 또는 `docs/data/implemented-jpa-data-model.md`

### API 추가/수정

1. `docs/api/index.md`
2. `docs/api/api-status.md`
3. `docs/decisions/api-docs-strategy.md`
4. 관련 도메인 API 문서
5. `docs/backend/guide.md`의 DTO/Swagger 규칙

### 데이터 모델 변경

1. `docs/data/index.md`
2. `docs/data/implemented-jpa-data-model.md`
3. 관련 테이블 정의서
4. `docs/decisions/domain-language.md`

## 관련 문서 공간

- 사람용 위키: GitHub Wiki
- 에이전트 작업 절차: `.agents/skills/`
- 문서 거버넌스 스킬: `.agents/skills/matchuri-doc-governance/SKILL.md`
- 내부 운영/실행 계획: `secrets/`

## 주요 인덱스

- 제품 기준: `docs/product/index.md`
- 프론트엔드 기준: `docs/frontend/index.md`
- 백엔드 기준: `docs/backend/index.md`
- API 기준: `docs/api/index.md`
- 데이터 기준: `docs/data/index.md`
- 설계 결정: `docs/decisions/index.md`

## 공개 문서 제외 영역

- 운영 런북, 배포 절차, 인프라 식별자, 장애 원문 기록은 내부 운영 문서에서 관리합니다.
- 실행 계획과 작업 이력은 내부 실행 계획 기록에서 관리합니다.
- 공개 문서에는 secret 값, 내부 계정/워크스페이스 ID, 운영 식별자를 남기지 않습니다.

## 유지보수 규칙

- API 계약이 바뀌면 OpenAPI 메타데이터, Swagger 산출물, 관련 `docs/api/` 문서를 함께 확인합니다.
- 데이터 구조가 바뀌면 구현과 `docs/data/`를 함께 맞춥니다.
- 도메인 용어나 제품 판단이 바뀌면 `docs/decisions/domain-language.md` 또는 `docs/product/product-sense.md`를 갱신합니다.
- 내부 실행 계획에서 확정된 규칙은 공개 가능한 개발 기준 문서에만 선별 승격합니다.
- 포트폴리오나 프로젝트 소개에 필요한 요약은 GitHub Wiki에 쓰고, 구현 기준의 원문은 `docs/`에 유지합니다.
- 반복 작업 절차는 `docs/`에 길게 쓰지 말고 repo-local skill로 옮깁니다.
- 검사 가능한 문서 규칙은 harness script로 옮깁니다.
- 개요 문서는 짧게 유지하고 세부 내용은 도메인별 문서로 연결합니다.
