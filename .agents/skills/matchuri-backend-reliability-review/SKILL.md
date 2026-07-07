---
name: matchuri-backend-reliability-review
description: Matchuri backend 신뢰성을 리뷰한다. 배포, 기동 확인, 환경 변수, health check, log, DB 연결, backup/restore, rollback, timeout/retry, Redis 도입 여부, 운영 복구 위험을 점검할 때 사용한다.
---

# Matchuri Backend 신뢰성 리뷰

## 개요

backend 변경이 장애를 빨리 파악하고 단순하게 복구할 수 있는 구조를 유지하는지 확인한다. 고가용성보다 2인 팀이 감당 가능한 운영 단순성을 우선한다.

## 먼저 읽을 것

1. root `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/backend/reliability.md`
4. `docs/decisions/backend-deployment-infrastructure.md`
5. data model 변경이면 `docs/data/index.md`
6. API 실패 응답이 바뀌면 `docs/api/index.md`

구현 기준을 찾기 위해 GitHub Wiki나 local Wiki folder를 읽지 않는다.

## 절차

1. 운영 영향 범위를 식별한다.
   - deploy script 또는 GitHub Actions 변경
   - application startup, port, profile, environment variable 변경
   - DB connection, migration, transaction, data loss risk
   - external integration, timeout, retry 변경
   - log, health check, error handling 변경

2. 기동과 health 확인 경로를 점검한다.
   - 배포 후 application이 정상 기동되는지 확인할 수 있어야 한다.
   - health endpoint 또는 Actuator 확인 경로가 있어야 한다.
   - startup failure 원인을 log에서 좁힐 수 있어야 한다.
   - 환경 변수 누락이 조용히 잘못된 기본값으로 넘어가지 않는지 확인한다.

3. log와 관측 가능성을 점검한다.
   - 최근 error log를 확인할 수 있는 위치가 있어야 한다.
   - 인증 실패, DB 실패, 외부 연동 실패, validation 실패를 구분할 수 있어야 한다.
   - 민감 정보는 log에 남기지 않는다.
   - 복잡한 monitoring보다 원인 축소에 필요한 최소 log를 우선한다.

4. DB와 data risk를 점검한다.
   - DB 연결 실패가 명확히 드러나는지 확인한다.
   - schema 변경은 entity/migration/docs와 함께 맞춘다.
   - 운영 DB를 개발 편의로 덮어쓰는 흐름을 만들지 않는다.
   - backup 주기, 보관 위치, restore 가능성을 확인한다.

5. 배포 실패와 rollback을 점검한다.
   - GitHub Actions 성공과 EC2 반영 성공을 구분한다.
   - 신규 버전 기동 실패 시 이전 버전을 다시 실행할 경로가 있어야 한다.
   - 배포 중 secret 또는 environment rendering 실패를 확인할 수 있어야 한다.
   - SSH `22` 전체 공개 같은 임시 예외가 장기 기준으로 굳지 않게 한다.

6. timeout과 retry를 점검한다.
   - DB나 external integration에 무한 대기가 없어야 한다.
   - 자동 retry는 꼭 필요한 지점에만 제한한다.
   - retry보다 먼저 실패 원인을 추적할 log를 확보한다.
   - 사용자 요청 실패는 4xx/5xx와 error code로 명확히 구분한다.

7. Redis 도입 여부를 판단한다.
   - Redis를 신뢰성 필수 구성요소로 가정하지 않는다.
   - 실시간 상태 동기화, cache 없이는 응답 시간 문제가 큰 경우, session/token 관리 복잡도가 커진 경우에만 검토한다.
   - Redis 도입이 운영 복잡도를 늘리는 비용보다 명확히 큰 이득이 있는지 확인한다.

8. 검증한다.
   - 가능한 경우 `backend`에서 `./gradlew test`를 실행한다.
   - 배포/운영 변경은 local test만으로 충분한지 따로 판단한다.
   - 실행하지 못한 운영 검증은 이유와 남은 risk를 보고한다.

## 장애 모델

우선 아래 장애를 기준으로 확인한다.

- application startup failure
- DB connection failure
- deployment failure
- server resource exhaustion
- external integration failure
- repeated invalid request or business exception

## 보고 형식

신뢰성 리뷰를 끝낼 때 아래를 보고한다.

- 영향 받은 deploy/runtime/data surface
- 확인 가능한 health/log 경로
- DB backup/restore 또는 rollback 영향
- 실행한 test 또는 실행하지 못한 이유
- 즉시 수정할 reliability risk
- 후속 운영 보류 항목
