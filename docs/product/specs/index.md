# 제품 명세 인덱스

제품 명세는 어떤 사용자 문제를 해결하는지, 무엇을 성공으로 볼지, 어디까지를 범위로 볼지 정의합니다.

이 디렉터리는 코드와 함께 유지해야 하는 공개 가능한 제품 판단 기준만 간결하게 담습니다. 화면·상태·수용 기준을 세분화한 내부 기능명세는 독립 `artifacts/specs/` 저장소에서 관리하며, 명시적인 내부 산출물 작업이 아니면 참조하지 않습니다.

## 관련 문서

- 상위 포털: `docs/README.md`
- 설계 판단: `docs/decisions/index.md`
- 아키텍처 개요: `docs/backend/architecture.md`

## 현재 명세

- [그룹 점심 메뉴 결정](./group-lunch-recommendation.md)
- [신규 사용자 온보딩](./new-user-onboarding.md)

## 최소 명세 구조

- 문제(Problem)
- 사용자(User)
- 목표(Goal)
- 비목표(Non-goals)
- 사용자 흐름(User Flow)
- 완료 기준(Acceptance Criteria)
