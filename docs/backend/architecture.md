# Matchuri Architecture

Matchuri는 개인 취향과 그룹 취향을 함께 반영해 점심 메뉴 결정 비용을 줄이는 서비스입니다. 아키텍처 판단의 기준은 추천 정확도만이 아니라 그룹이 빠르게 합의하는 흐름을 안정적으로 지원하는 것입니다.

## 운영 전제

- 팀은 `BE 1 + FE 1` 규모입니다.
- 백엔드 담당자는 API 서버, 인프라, 배포, 일부 프론트 연동 운영까지 함께 봅니다.
- 따라서 대규모 팀 기준의 분산 구조보다 소수 인원이 이해하고 복구할 수 있는 단순한 구조를 우선합니다.
- 새 기술은 확장성보다 현재 운영 부담을 먼저 평가합니다.

## 저장소 경계

- `backend/`: Spring Boot 4, Java 21, Gradle Kotlin DSL 기반 API 서버.
- `docs/`: 현재 개발 기준 문서. 문서 진입점은 `docs/README.md`.
- GitHub Wiki: 사람이 읽는 프로젝트 소개, 포트폴리오, 협업 안내.
- `docs/api/`: API 계약 설명과 상태표.
- `docs/data/`: 현재 데이터 모델과 스키마 설명.
- 내부 운영 문서: 배포/운영 런북과 인프라 세부 절차.
- `frontend/`: 프론트엔드 애플리케이션. 백엔드 작업에서는 API 연동 계약이 필요할 때만 확인합니다.

## 서버 책임

- 회원, 인증, 약관, 취향 프로필 관리.
- 메뉴 카탈로그와 기준 데이터 제공.
- 개인 추천 실행, 후보 저장, 선택/행동 로그 저장.
- 그룹 방, 초대, 멤버십, 그룹 추천, 후보, 투표, 최종 메뉴 확정 관리.
- API 계약, 에러 코드, 인증/인가 경계 유지.
- 배포와 장애 대응이 단순한 런타임 구조 유지.

## 클라이언트 책임

- 온보딩, 취향 입력, 그룹 합의 화면 표현.
- 지도, 가게 검색, 장소 상세 표시.
- 그룹 추천 진행 상태를 사용자가 이해하기 쉽게 표시.

장소/place 정보는 현재 서버의 핵심 영속 데이터가 아니라 메뉴 결정 이후 보조 레이어로 봅니다.

## 핵심 도메인

- `Member`: 계정, 로그인 상태, 권한, 상태.
- `Member Taste Profile`: 선호 속성, 제한 재료, 비선호 메뉴.
- `Menu Catalog`: `menu_items`, `attribute_categories`, `ingredients`, 메뉴-속성/재료 매핑.
- `Personal Recommendation`: 개인 추천 실행 단위, 후보, 선택 결과, 후속 행동.
- `Group Decision`: `group room`, 초대, 멤버, `group recommendation`, 후보, 투표, 최종 메뉴.

용어 기준은 `docs/decisions/domain-language.md`를 봅니다.

## 데이터 모델 원칙

- 회원 취향과 메뉴 특성은 공통 `attribute category` 마스터를 공유합니다.
- 취향 정보는 JSON 덩어리보다 정규화된 매핑 테이블을 우선합니다.
- 개인 추천과 그룹 추천은 상태 흐름이 다르므로 별도 실행 모델로 다룹니다.
- 추천 후보와 최종 선택은 구분합니다.
- 중복 투표, 권한 없는 투표, 닫힌 추천에 대한 투표 같은 상태 충돌은 DB 제약과 서비스 검증을 함께 고려합니다.

스키마 진입점은 `docs/data/index.md`, 현재 요약은 `docs/data/implemented-jpa-data-model.md`입니다.

## 백엔드 런타임 구조

패키지는 아래 축을 기준으로 나눕니다.

```text
backend/src/main/java/matchuri/backend
├─ api
├─ domain
├─ global
└─ infra
```

- `api`: Controller, request/response/docs DTO, Mapper, Swagger/OpenAPI 메타데이터.
- `domain`: 유스케이스, 도메인 지원 로직, 엔티티, repository, 도메인 예외.
- `global`: 공통 응답, 공통 예외 처리, 보안 공통 설정, 전역 설정.
- `infra`: 외부 시스템 연동과 기술 구현 세부사항.

새 도메인이나 리팩토링 대상은 `service`, `command`, `result`, `support`, `exception`, `entity`, `repository` 기준을 따릅니다. 자세한 구현 규칙은 `docs/backend/guide.md`를 봅니다.

## 추천 흐름

### 개인 추천

1. 사용자가 로그인하거나 비회원 상태로 취향을 입력합니다.
2. 백엔드는 회원 취향, 제한 재료, 비선호 메뉴, 메뉴 속성을 바탕으로 후보를 계산합니다.
3. 후보 목록과 추천 사유 힌트를 반환합니다.
4. 선택, 스킵, 클릭 같은 후속 행동은 추천 개선용 데이터로 남길 수 있습니다.

### 그룹 추천

1. 사용자가 그룹 방을 만들고 다른 사용자가 초대 코드/링크로 참여합니다.
2. 구성원은 저장된 취향을 불러오거나 필요한 취향을 입력합니다.
3. 그룹 추천 실행 단위가 열리고 후보 메뉴 3개 안팎을 생성합니다.
4. 참여자는 후보에 투표합니다.
5. 투표 결과로 최종 메뉴를 확정하고 추천 실행 단위를 닫습니다.

그룹 추천의 핵심은 실시간성보다 상태 흐름의 명확성과 합의 완료입니다.

## 인프라 방향

현재 채택:

- Backend: GitHub Actions + AWS IAM OIDC + SSM Run Command 기반 EC2 배포.
- Secret: Infisical source of truth + GitHub Actions OIDC.
- DB: 초기에는 EC2 내부 MySQL.
- 배포 단위: JAR 중심.

당장 채택하지 않음:

- Redis 즉시 도입.
- Docker/ECS 기반 운영 전환.
- 다중 인스턴스 운영.
- 관리형 DB 분리.

Redis, RDS, Docker, 다중 인스턴스는 실제 병목, 복구 요구, 배포 재현성 문제가 분명해질 때 단계적으로 검토합니다.

## 현재 우선순위

- MVP에서는 `후보 3개 안팎 + 투표 + 최종 선택` 흐름 완결이 가장 중요합니다.
- 추천 알고리즘 고도화보다 API 계약, 상태 전이, 저장 구조의 추적 가능성을 우선합니다.
- API 문서 운영 기준은 `docs/decisions/api-docs-strategy.md`와 `docs/api/index.md`를 따릅니다.
- 실행 계획이 필요한 작업은 내부 실행 계획 기록에 남깁니다.

## 더 명확히 할 것

- 비회원 추천과 회원 추천의 장기 관계.
- 추천 알고리즘 v1의 세부 점수 규칙.
- 그룹 추천 상태 전이의 API/DB 제약 세부 기준.
- 운영 환경 변수와 배포 스크립트의 최신 source of truth.
