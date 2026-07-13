# 데이터 문서 인덱스

## 문서 상태

- 상태: 현재 구현 기준 인덱스
- 기준일: 2026-07-13
- 담당 영역: data docs
- 기준 소스:
  - 현재 운영 테이블 정의서: `docs/data/*-schema.md`
  - 현재 구현 테이블 인덱스: `docs/data/implemented-jpa-data-model.md`

## 문서 목적

- Matchuri 데이터 모델 문서의 공식 진입점을 제공합니다.
- 현재 운영 테이블 정의서와 과거/초안 문서를 구분합니다.
- 코드 구현이나 리뷰 중 어떤 문서를 먼저 볼지 안내합니다.

## 현재 기준 문서

| 문서 | 역할 |
| --- | --- |
| [데이터 정의서 템플릿](./template.md) | 새 데이터 정의서 작성 양식과 에이전트 작업 기준 |
| [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md) | 현재 JPA 엔티티 기준 테이블 목록과 문서 매핑 |
| [회원 테이블 정의서](./members-schema.md) | `members` |
| [회원 약관 동의 테이블 정의서](./member-agreements-schema.md) | `member_agreements` |
| [회원 취향 프로필 테이블 정의서](./member-taste-profiles-schema.md) | `member_taste_profiles`와 하위 매핑 |
| [회원 개인 위치 테이블 정의서](./member-locations-schema.md) | `member_locations` |
| [인증 refresh token 테이블 정의서](./auth-refresh-tokens-schema.md) | `auth_refresh_tokens` |
| [인증 exchange code 테이블 정의서](./auth-exchange-codes-schema.md) | `auth_exchange_codes` |
| [인증 이메일 검증 테이블 정의서](./auth-email-verifications-schema.md) | `auth_email_verifications` |
| [메뉴 카탈로그 테이블 정의서](./menu-catalog-schema.md) | 메뉴/속성/재료 마스터와 매핑 |
| [이미지 자산 테이블 정의서](./images-schema.md) | `image_assets`, `menu_item_images` |
| [개인 추천 테이블 정의서](./personal-recommendations-schema.md) | 개인 추천, 후보, 회원 메뉴 행동 로그 |
| [그룹 방 테이블 정의서](./group-rooms-schema.md) | 그룹 방, 멤버, 초대, 위치, presence |
| [그룹 추천 테이블 정의서](./group-recommendations-schema.md) | 그룹 추천, 준비, 후보, 투표, 그룹 행동 로그 |

## 참고 문서

| 문서 | 상태 | 사용 기준 |
| --- | --- | --- |
| [회원 필수 약관 동의 데이터 상세 설계 초안](./member-required-agreements-schema.md) | 구현 전 초안 / 참고 | 현재 기준은 [회원 약관 동의 테이블 정의서](./member-agreements-schema.md)를 우선 |

## 먼저 볼 문서

1. [데이터 정의서 템플릿](./template.md)
2. [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)
3. 작업 대상 도메인의 개별 테이블 정의서
4. 필요 시 관련 API 문서와 `docs/backend/architecture.md`

## 읽는 방법

- "현재 어떤 테이블이 운영 중인가?"는 [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)를 봅니다.
- "컬럼, 제약, 인덱스, 상태값이 무엇인가?"는 개별 `*-schema.md` 문서를 봅니다.
- "전체 관계를 빠르게 보고 싶다"면 [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)를 봅니다.
- 구현과 문서가 다르면 엔티티와 init SQL을 먼저 확인하고 문서를 갱신합니다.

## 유지보수 원칙

- 새 테이블이 추가되면 개별 정의서, 이 인덱스, `docs/data/implemented-jpa-data-model.md`를 함께 확인합니다.
- 컬럼, FK, unique, enum, 상태 흐름이 바뀌면 해당 정의서를 갱신합니다.
- 구현 전 초안은 현재 기준 문서처럼 읽히지 않게 문서 상태를 명확히 표시합니다.
- 반복적인 JPA Entity, init SQL, data docs index 정합성 확인은 `docs/decisions/data-schema-drift-harness.md`의 harness 설계를 기준으로 자동화합니다.

## 마지막 갱신

- 2026-07-13
