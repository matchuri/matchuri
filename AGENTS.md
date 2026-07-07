# Matchuri Agent Router

이 파일은 에이전트가 처음 읽는 최소 라우터입니다. 상세 규칙은 `docs/`의 현재 개발 기준 문서를 필요한 만큼만 엽니다.

## 기본 원칙

- Matchuri는 맛집 검색 서비스가 아니라 점심 메뉴 결정 비용을 줄이는 서비스입니다.
- MVP의 핵심 흐름은 `후보 3개 안팎 + 투표 + 최종 메뉴 확정`입니다.
- 현재 개발 기준 문서는 `docs/`와 코드입니다.
- 사람이 읽는 소개, 포트폴리오, 협업 안내 문서는 GitHub Wiki에서 관리합니다.
- 반복되는 에이전트 작업 절차는 `.agents/skills/`의 repo-local skill로 관리합니다.
- 기계적으로 검증할 수 있는 문서 규칙은 harness script나 테스트로 관리합니다.
- 운영 런북, 실행 계획, 개인 도구 설정은 공개 문서가 아니라 내부 `secrets/` 영역에서 관리합니다.
- 일반 개발 작업에서 GitHub Wiki나 로컬 Wiki 폴더는 구현 기준으로 읽지 않습니다.

## 문서 진입점

- 개발 문서 홈: `docs/README.md`
- 백엔드 작업 라우터: `backend/AGENTS.md`
- 프론트엔드 작업 라우터: `frontend/AGENTS.md`
- 제품 판단: `docs/product/index.md`
- 프론트엔드 작업: `docs/frontend/index.md`
- 백엔드 작업: `docs/backend/index.md`
- API 계약/상태: `docs/api/index.md`
- 데이터 모델: `docs/data/index.md`
- 설계 결정: `docs/decisions/index.md`

## 작업 규칙

- 작업 전에 모든 문서를 읽지 말고, 작업 종류에 맞는 진입점부터 엽니다.
- 하위 영역에 `AGENTS.md`가 있으면 루트 라우터 다음으로 해당 파일을 확인합니다.
- 동작, API 계약, 데이터 구조, 도메인 용어가 바뀌면 관련 `docs/` 문서를 함께 갱신합니다.
- 프로젝트 소개, 포트폴리오 서사, 협업 방식처럼 사람이 읽을 맥락은 GitHub Wiki에 남깁니다.
- GitHub Wiki는 루트 프로젝트와 별도의 문서 저장소로 취급합니다. 루트 저장소 문서에서는 추적하지 않는 로컬 위키 경로를 링크하지 않습니다.
- 명시적인 Wiki 산출/수정 작업이 아니면 로컬 Wiki 폴더를 열거나 검색하지 않습니다.
- 일반 검색은 `AGENTS.md`, `docs/`, `backend/`, `frontend/`, 관련 코드 경로를 대상으로 합니다.
- Wiki 내용은 구현 기준이 아닙니다. 구현 판단은 코드와 `docs/`를 기준으로 합니다.
- 반복 절차를 문서로 길게 쓰기 전에 skill로 만들 수 있는지 확인합니다.
- 검사 가능한 규칙은 prose보다 harness script를 우선합니다.
- 운영 절차나 실행 계획처럼 공개가 부적절한 맥락은 내부 문서에 남깁니다.
- 문서만 변경한 경우에도 링크 경로, 중복 내용, 오래된 가정 여부를 직접 확인합니다.

## 검증

- Backend: `backend`에서 `./gradlew test`
- API 계약 변경: OpenAPI 메타데이터, Swagger 산출물, 관련 `docs/api/` 문서 확인
- 데이터 모델 변경: 엔티티/마이그레이션 기준과 `docs/data/` 확인
- 문서 거버넌스: `python .agents\skills\matchuri-doc-governance\scripts\audit_docs.py --root . --strict`
- API 계약 동기화: `python .agents\skills\matchuri-api-contract-sync\scripts\audit_api_contract.py --root .`
