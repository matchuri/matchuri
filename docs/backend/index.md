# 백엔드 문서 인덱스

백엔드 문서는 Spring Boot API 서버의 구조, 구현 규칙, 보안/신뢰성 기준을 정리합니다.
반복되는 리뷰 절차는 `docs/`에 길게 두지 않고 repo-local skill로 관리합니다.

## 현재 기준

- 구현 가이드: `docs/backend/guide.md`
- 아키텍처: `docs/backend/architecture.md`
- 보안 기준: `docs/backend/security.md`
- 신뢰성 기준: `docs/backend/reliability.md`
- 품질 점수 기준: `docs/backend/quality-score.md`
- API 계약: `docs/api/index.md`
- 데이터 모델: `docs/data/index.md`
- 품질 리뷰 스킬: `.agents/skills/matchuri-backend-quality-review/SKILL.md`
- 보안 리뷰 스킬: `.agents/skills/matchuri-backend-security-review/SKILL.md`
- 신뢰성 리뷰 스킬: `.agents/skills/matchuri-backend-reliability-review/SKILL.md`

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
- 인증/인가/시크릿 변경은 보안 리뷰 스킬을 사용합니다.
- 배포/로그/복구/운영 영향이 있으면 신뢰성 리뷰 스킬을 사용합니다.
- PR 리뷰나 리팩터링 우선순위 판단이 필요하면 품질 리뷰 스킬을 사용합니다.
