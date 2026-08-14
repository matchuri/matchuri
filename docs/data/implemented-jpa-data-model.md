# 현재 구현 테이블 정의서 인덱스

## 문서 상태

- 상태: 현재 구현 기준 인덱스
- 기준일: 2026-07-13
- 담당 영역: data docs
- 기준 소스:
  - JPA Entity: `backend/src/main/java/matchuri/backend/domain/**/entity/*.java`
  - 개별 테이블 정의서: `docs/data/*-schema.md`

## 문서 목적

- 현재 JPA Entity 기준으로 운영 중인 테이블과 담당 정의서를 매핑합니다.
- JPA가 빈 DB에 생성하는 현재 데이터 모델의 탐색 경로를 제공합니다.

## 현재 범위

현재 JPA Entity 기준 운영 테이블은 30개입니다.

| 영역 | 테이블 | 정의서 |
| --- | --- | --- |
| 회원 | `members` | [회원](./members-schema.md) |
| 회원 | `member_agreements` | [회원 약관 동의](./member-agreements-schema.md) |
| 회원 | `member_locations` | [회원 개인 위치](./member-locations-schema.md) |
| 회원 취향 | `member_taste_profiles` | [회원 취향 프로필](./member-taste-profiles-schema.md) |
| 회원 취향 | `member_taste_profile_categories` | [회원 취향 프로필](./member-taste-profiles-schema.md) |
| 회원 취향 | `member_taste_profile_restriction_ingredients` | [회원 취향 프로필](./member-taste-profiles-schema.md) |
| 회원 취향 | `member_taste_profile_disliked_menu_items` | [회원 취향 프로필](./member-taste-profiles-schema.md) |
| 인증 | `auth_refresh_tokens` | [인증 refresh token](./auth-refresh-tokens-schema.md) |
| 인증 | `auth_exchange_codes` | [인증 exchange code](./auth-exchange-codes-schema.md) |
| 인증 | `auth_email_verifications` | [인증 이메일 검증](./auth-email-verifications-schema.md) |
| 메뉴 | `attribute_categories` | [메뉴 카탈로그](./menu-catalog-schema.md) |
| 메뉴 | `ingredients` | [메뉴 카탈로그](./menu-catalog-schema.md) |
| 메뉴 | `menu_items` | [메뉴 카탈로그](./menu-catalog-schema.md) |
| 메뉴 | `menu_attribute_categories` | [메뉴 카탈로그](./menu-catalog-schema.md) |
| 메뉴 | `menu_ingredients` | [메뉴 카탈로그](./menu-catalog-schema.md) |
| 이미지 | `image_assets` | [이미지 자산](./images-schema.md) |
| 이미지/메뉴 | `menu_item_images` | [이미지 자산](./images-schema.md), [메뉴 카탈로그](./menu-catalog-schema.md) |
| 개인 추천 | `personal_recommendations` | [개인 추천](./personal-recommendations-schema.md) |
| 개인 추천 | `personal_recommendation_candidates` | [개인 추천](./personal-recommendations-schema.md) |
| 개인 행동 | `member_menu_actions` | [개인 추천](./personal-recommendations-schema.md) |
| 그룹 방 | `group_rooms` | [그룹 방](./group-rooms-schema.md) |
| 그룹 방 | `group_room_members` | [그룹 방](./group-rooms-schema.md) |
| 그룹 방 | `group_locations` | [그룹 방](./group-rooms-schema.md) |
| 그룹 방 | `group_invites` | [그룹 방](./group-rooms-schema.md) |
| 그룹 방 | `group_invite_links` | [그룹 방](./group-rooms-schema.md) |
| 그룹 방 | `group_presence_events` | [그룹 방](./group-rooms-schema.md) |
| 그룹 추천 | `group_recommendations` | [그룹 추천](./group-recommendations-schema.md) |
| 그룹 추천 | `group_recommendation_readiness` | [그룹 추천](./group-recommendations-schema.md) |
| 그룹 추천 | `group_recommendation_candidates` | [그룹 추천](./group-recommendations-schema.md) |
| 그룹 추천 | `group_recommendation_votes` | [그룹 추천](./group-recommendations-schema.md) |
| 그룹 추천 | `group_menu_actions` | [그룹 추천](./group-recommendations-schema.md) |

## 스키마 생성 기준

- 별도 init SQL이나 DDL snapshot을 유지하지 않습니다.
- JPA Entity와 연관관계가 스키마의 단일 구현 기준입니다.
- 빈 DB 기동 테스트로 Entity와 생성 스키마의 정합성을 검증합니다.

## 관계 빠른 요약

| 기준 | 대상 | 관계 | 정의서 |
| --- | --- | --- | --- |
| `members` | `member_agreements` | 1 : N | [회원 약관 동의](./member-agreements-schema.md) |
| `members` | `member_taste_profiles` | 1 : 0..1 | [회원 취향 프로필](./member-taste-profiles-schema.md) |
| `members` | `member_locations` | 1 : 0..1 | [회원 개인 위치](./member-locations-schema.md) |
| `member_taste_profiles` | 취향 하위 매핑 3종 | 1 : N | [회원 취향 프로필](./member-taste-profiles-schema.md) |
| `menu_items` | `menu_attribute_categories`, `menu_ingredients` | 1 : N | [메뉴 카탈로그](./menu-catalog-schema.md) |
| `menu_items` | `menu_item_images` | 1 : 0..1 | [이미지 자산](./images-schema.md) |
| `members` | `personal_recommendations` | 1 : N | [개인 추천](./personal-recommendations-schema.md) |
| `personal_recommendations` | `personal_recommendation_candidates` | 1 : N | [개인 추천](./personal-recommendations-schema.md) |
| `group_rooms` | `group_room_members`, `group_locations`, `group_invites`, `group_invite_links` | 1 : N | [그룹 방](./group-rooms-schema.md) |
| `group_rooms` | `group_recommendations` | 1 : N | [그룹 추천](./group-recommendations-schema.md) |
| `group_recommendations` | readiness, candidates, votes, actions | 1 : N | [그룹 추천](./group-recommendations-schema.md) |

## 인덱스 운영 기준

- JPA Entity에는 대부분 명시 보조 인덱스(`@Index`)를 정의하지 않습니다.
- unique 제약은 데이터 무결성 기준으로 유지하고, 보조 인덱스와 분리해 판단합니다.
- DB가 PK, FK, unique 제약을 위해 자동 생성하는 인덱스는 제거 대상인 성능 목적 보조 인덱스와 구분합니다.
- 조회 성능 개선이 필요해진 시점에 실제 쿼리와 실행 계획으로 인덱스 추가 전후를 비교합니다.

## 함께 볼 문서

- [데이터 문서 인덱스](./index.md)
- [데이터 정의서 템플릿](./template.md)
- [아키텍처 문서](../backend/architecture.md)

## 마지막 갱신

- 2026-07-13
