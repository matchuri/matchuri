# Matchuri Architecture

Matchuri는 개인 취향과 그룹 취향을 함께 반영해 점심 메뉴 결정 비용을 줄이는 서비스입니다. 아키텍처 판단의 기준은 추천 정확도만이 아니라 그룹이 빠르게 합의하는 흐름을 안정적으로 지원하는 것입니다.

## 운영 전제

- 팀은 `BE 1 + FE 1` 규모입니다.
- 백엔드 담당자는 API 서버, 인프라, 배포, 일부 프론트 연동 운영까지 함께 봅니다.
- 따라서 대규모 팀 기준의 분산 구조보다 소수 인원이 이해하고 복구할 수 있는 단순한 구조를 우선합니다.
- 새 기술은 확장성보다 현재 운영 부담을 먼저 평가합니다.

## 저장소 경계

- `app/backend/`: Spring Boot 4, Java 21, Gradle Kotlin DSL 기반 API 서버.
- `docs/`: 현재 개발 기준 문서. 문서 진입점은 `docs/README.md`.
- GitHub Wiki: 사람이 읽는 프로젝트 소개, 포트폴리오, 협업 안내.
- `docs/api/`: API 계약 설명과 상태표.
- `docs/data/`: 엔티티 구조만으로 알 수 없는 데이터 정책과 검증 진입점.
- 내부 운영 문서: 배포/운영 런북과 인프라 세부 절차.
- `app/frontend/`: 프론트엔드 애플리케이션. 백엔드 작업에서는 API 연동 계약이 필요할 때만 확인합니다.

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

스키마 진입점은 `docs/data/index.md`입니다. 실제 구조는 JPA Entity를, 구조만으로 알 수 없는 판단은 `docs/data/policies.md`를 기준으로 봅니다.

## 백엔드 런타임 구조

8개 Gradle 모듈을 하나의 Spring Boot 애플리케이션과 하나의 DB로 실행합니다. 모듈 ID와 공개 인터페이스는 Spring Modulith 2.0.3으로 선언하며 전체 테스트에서 경계를 검증합니다.

```text
app/backend/
├─ backend-app       # HTTP API, 공통 설정, 시드, 단일 실행 JAR
├─ identity          # 인증, 회원, 약관, 취향, Spring Security
├─ catalog           # 메뉴, 속성, 재료, 메뉴 이미지 연결
├─ recommendation    # 개인·비회원 추천, 행동 기록, 공통 추천 알고리즘
├─ group-decision    # 그룹, 초대, 추천 진행, 투표, 최종 확정
├─ media             # 이미지 자산, 프리셋, 오브젝트 스토리지
├─ realtime          # SSE 연결과 커밋 후 이벤트 전송
└─ shared-kernel     # 공통 응답·예외·영속성·트랜잭션 지원
```

- `backend-app`은 모든 모듈을 조립하고 `build/libs/backend-<version>.jar` 하나를 생성합니다. 기존 배포의 JAR 탐색·health 경로·환경 설정을 유지합니다.
- 의존 방향은 `shared-kernel ← media ← catalog ← identity ← recommendation ← group-decision ← realtime`입니다. 각 모듈은 필요한 하위 모듈의 named interface만 참조합니다.
- 공개 서비스·조회·저장 인터페이스와 command/result, 이벤트, 현재 JPA 연관에 필요한 모델을 명시적으로 공개합니다. 서비스 구현·repository는 내부입니다. 테이블·FK·Entity 필드는 유지하며 모델 공유 축소는 별도 작업으로 남깁니다.
- `identity`의 열린 개인 추천 ID 조회는 소비자 소유 조회 인터페이스를 `recommendation`이 구현합니다. 기존 조회 조건과 조회 중 저장 동작을 유지하며 순환 의존성을 제거합니다.
- 초기 데이터 조립인 `backend-app/application/seed`만 bootstrap repository 접근을 허용합니다. 업무 코드의 foreign repository 접근은 추가 구조 테스트로 금지합니다.
- 회귀 테스트는 루트 `src/test`에 유지해 전체 모듈·HTTP·JPA 경계를 함께 검증합니다. `ModuleStructureTest`는 8개 모듈의 실제 탐지와 순환·내부 접근·허용 의존성을 검사합니다.

새 도메인이나 리팩토링 대상은 `service`, `command`, `result`, `support`, `exception`, `entity`, `repository` 기준을 따릅니다. 자세한 구현 규칙은 `docs/backend/guide.md`를 봅니다.

### 모듈 이벤트와 완료 시점

| 이벤트 | 소비 모듈 | 처리 시점과 원자성 |
| --- | --- | --- |
| `MemberWithdrawn` | group-decision | 동기 `@EventListener` + `MANDATORY`. 회원 탈퇴·토큰 제거·소유 그룹 삭제를 같은 트랜잭션으로 완료 |
| `PresetProfileImageDeleted` | identity | 동기 `@EventListener` + `MANDATORY`. 삭제한 이미지 사용 회원 모두를 활성 기본 이미지로 재지정하고 함께 커밋 |
| 그룹 참여·초대·추천·투표·삭제 이벤트 | realtime | `AFTER_COMMIT`. 기존 SSE event type과 payload 유지 |

동기 소비자가 실패하면 발행 측 업무 변경도 롤백됩니다. API 성공 응답의 완료 의미는 유지합니다. 비동기 소비, 이벤트 저장소, 자동 재시도·보상은 도입하지 않습니다.

### SSE 수신자 정책

- 일반 그룹 이벤트는 전송 시점의 활성 계정·활성 멤버십·삭제되지 않은 그룹을 다시 조회합니다. 자격을 잃은 그룹 연결은 종료합니다.
- 그룹 삭제는 삭제 직전 대상 스냅샷 중 현재 활성 계정에 삭제 payload를 전송한 뒤 해당 그룹의 모든 연결을 종료합니다.
- 초대는 지정 대상에게만 보내며, 아직 유효한 `PENDING` 초대인지 확인합니다. 개인 전송에서도 계정 활성 상태를 확인합니다.
- 투표 완료는 원래 이벤트 대상이 현재도 활성 OWNER인 경우에만 전송합니다. OWNER 변경 후 새 OWNER로 재전송하지 않습니다.
- 커밋 후 조회는 별도의 읽기 트랜잭션을 사용합니다. 전송 실패에 대한 보상·재시도와 동시성 고도화는 이후 별도 범위입니다.

### 트랜잭션 실패 경계

- 인증·개인 추천·그룹 추천 서비스는 업무 예외에도 일반 롤백 규칙을 적용합니다. 포괄적인 `noRollbackFor`로 업무 변경을 커밋하지 않습니다.
- 보존할 실패 기록은 [데이터 정책](../data/policies.md#실패-시-기록-보존)에 한정합니다. 도메인이 기록 내용을 정하고 `RollbackRecordExecutor`가 업무 트랜잭션의 `afterCompletion(ROLLED_BACK)` 이후 `REQUIRES_NEW`로 실행합니다. 외부 유스케이스의 트랜잭션에 참여한 경우에도 최종 롤백 뒤 실행합니다.
- 별도 트랜잭션은 실패한 트랜잭션의 엔티티를 병합하지 않고 ID·불변 값으로 다시 조회하거나 새 실패 기록을 만듭니다. 업무 커밋 시에는 실패 기록을 추가로 저장하지 않습니다.
- 실패 기록 저장 자체가 실패하면 오류 로그를 남기고 기존 API 오류 응답을 유지합니다. 자동 재시도·보상·outbox는 이후 별도 설계 범위입니다.
- API 경로, Request/Response 필드·검증·오류 코드와 성공 응답의 업무 완료 의미는 유지합니다. 대표 HTTP 계약과 업무 롤백·기록 보존은 실제 서비스·JPA 경계를 포함한 통합 테스트로 검증합니다.

## 추천 흐름

개인·비회원·그룹 점수의 의미, 선호 평가 단위와 정규화 정책은 [추천 점수 계약](./recommendation-scoring.md)을 봅니다.

### 개인 추천

1. 사용자가 로그인하거나 비회원 상태로 취향을 입력합니다.
2. 백엔드는 회원 취향, 제한 재료, 비선호 메뉴, 메뉴 속성을 바탕으로 후보를 계산합니다.
3. 후보 목록과 추천 사유 힌트를 반환합니다.
4. 선택, 스킵, 클릭 같은 후속 행동은 추천 개선용 데이터로 남길 수 있습니다.

### 그룹 추천

1. 사용자가 그룹 방을 만들고 다른 사용자가 UUID 초대 링크 또는 닉네임 초대 수락으로 참여합니다. 고정 초대 코드는 데이터와 참여 API에 유지하지만 실 서비스에서는 사용하지 않습니다.
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
- 그룹 추천 상태 전이의 API/DB 제약 세부 기준.
- 운영 환경 변수와 배포 스크립트의 최신 source of truth.
