# 백엔드 문서 인덱스

백엔드 문서는 Spring Boot API 서버의 구조, 구현 규칙, 보안/신뢰성 기준을 정리합니다.

## 현재 기준

- 구현 가이드: `docs/backend/guide.md`
- 아키텍처: `docs/backend/architecture.md`
- 보안 기준: `docs/backend/security.md`
- 신뢰성 기준: `docs/backend/reliability.md`
- 품질 점수 기준: `docs/backend/quality-score.md`
- API 계약: `docs/api/index.md`
- 데이터 모델: `docs/data/index.md`

## 주요 문서

- [백엔드 가이드](./guide.md)
- [아키텍처](./architecture.md)
- [보안 기준](./security.md)
- [신뢰성 기준](./reliability.md)
- [품질 점수 기준](./quality-score.md)

## 작업 기준

- 기본 검증은 `backend`에서 `./gradlew test`입니다.
- API 계약 변경 시 OpenAPI 메타데이터, Swagger 산출물, 관련 `docs/api/` 문서를 함께 확인합니다.
- 데이터 모델 변경 시 엔티티/마이그레이션 기준과 `docs/data/`를 함께 확인합니다.
