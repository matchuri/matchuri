# 신뢰성 기준

이 문서는 Matchuri backend 신뢰성의 현재 기준만 남깁니다. 실제 변경 리뷰 절차는 `.agents/skills/matchuri-backend-reliability-review/SKILL.md`를 사용합니다.

현재 목표는 대규모 고가용성이 아니라, 2인 팀이 장애를 빨리 파악하고 단순한 절차로 복구할 수 있는 상태를 만드는 것입니다.

## 현재 운영 전제

- Backend는 EC2 단일 서버에 배포합니다.
- DB는 초기에는 EC2 내부 MySQL로 운영합니다.
- Frontend는 Vercel에 배포합니다.
- Redis는 즉시 도입하지 않고, 성능이나 상태 동기화 요구가 분명해질 때 검토합니다.
- 배포 구조의 근거는 `docs/decisions/backend-deployment-infrastructure.md`를 봅니다.
- 실제 운영 절차와 runbook은 공개 `docs/`가 아니라 내부 운영 문서에서 관리합니다.

이 전제는 운영 복잡도를 낮추는 대신 단일 장애 지점을 수용한다는 뜻입니다.

## 신뢰성 목표

- 장애 원인을 빨리 확인할 수 있어야 합니다.
- 배포 실패 시 당황하지 않고 이전 상태로 복구할 수 있어야 합니다.
- 소수 인원이 유지 가능한 수준으로 운영 복잡도를 억제해야 합니다.

## 우선 장애 모델

- application startup failure
- DB connection failure
- deployment failure
- server resource exhaustion
- external integration failure
- repeated invalid request 또는 business exception

## 기본 원칙

- 장애를 완전히 막는 것보다 원인을 빨리 좁힐 수 있는 구조를 우선합니다.
- 복잡한 자동 복구보다 사람이 이해 가능한 단순 복구 절차를 먼저 둡니다.
- 배포와 운영 절차는 반복 가능한 방식으로 유지합니다.
- 새 기술은 신뢰성을 높이는 효과가 운영 복잡도보다 분명할 때 도입합니다.

## 최소 운영 기준

배포:

- 배포는 가능한 한 GitHub Actions 기반 자동화로 수행합니다.
- 배포 후 application 기동 확인 절차가 있어야 합니다.
- 실패 시 이전 버전을 다시 실행할 수 있는 복구 경로를 유지합니다.
- GitHub Actions 성공과 EC2 반영 성공을 구분합니다.

실행:

- application은 서버 재시작 후 다시 올릴 수 있는 방식으로 운영합니다.
- 환경 변수는 code에 hardcoding하지 않고 서버 또는 CI secret으로 관리합니다.
- health endpoint 또는 Actuator 확인 경로를 유지합니다.
- log 확인 위치와 방법을 내부 운영 문서에 남깁니다.

데이터:

- DB backup 주기와 보관 위치를 정합니다.
- schema 변경은 code, migration, `docs/data`와 함께 관리합니다.
- 운영 DB를 개발 편의로 쉽게 덮어쓰는 방식을 피합니다.
- restore 가능성을 주기적으로 확인하는 방향을 유지합니다.

## Log와 관측

초기 단계에서는 복잡한 monitoring보다 아래 수준을 먼저 확보합니다.

- application start success/failure 확인
- 최근 error log 확인
- deploy success/failure 확인
- server 상태 확인
- DB connection failure 확인
- 인증 실패, 권한 실패, validation 실패, business exception 구분

민감 정보는 log에 남기지 않습니다.

## Error handling

- 잘못된 요청은 4xx로 명확히 구분합니다.
- 서버 내부 문제는 5xx로 응답합니다.
- error code는 domain 기준으로 일관되게 관리합니다.
- 예상 가능한 실패는 message를 통일하고, log에는 원인 추적 정보가 남아야 합니다.

## Timeout과 retry

- DB나 external integration 호출은 무한 대기를 피합니다.
- 자동 retry는 꼭 필요한 지점에만 제한적으로 둡니다.
- retry보다 먼저 실패 원인을 추적할 log를 확보합니다.
- 실패를 숨기기보다 명확하게 드러내는 편을 우선합니다.

## Backup과 rollback

- 현재 구조에서 가장 중요한 복구 대상은 MySQL data입니다.
- DB backup 주기와 보관 위치를 정합니다.
- deploy failure 시 이전 application version을 다시 올릴 수 있어야 합니다.
- 운영 서버 접근과 복구 절차는 내부 운영 문서에서 관리합니다.

## Redis 방침

Redis는 현재 신뢰성 필수 구성요소가 아닙니다. Redis 없이도 단순하게 운영 가능한 구조를 먼저 만듭니다.

도입 검토 조건:

- 실시간 상태 동기화 요구가 커질 때
- caching 없이는 응답 시간이 문제가 될 때
- session/token 관리 복잡도가 증가할 때

## 관련 skill

- reliability review: `.agents/skills/matchuri-backend-reliability-review/SKILL.md`
