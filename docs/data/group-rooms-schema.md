# 그룹 방 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: group
- 기준 소스:
  - JPA Entity: `GroupRoom`, `GroupRoomMember`, `GroupLocation`, `GroupInvite`, `GroupInviteLink`, `GroupPresenceEvent`
  - 관련 API 문서: 그룹 방 API 문서

## 기준 소스 우선순위

1. JPA Entity와 enum
2. 그룹 service write path와 repository query
3. 관련 API 문서

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- 그룹 방, 멤버, 초대, 위치, presence 이벤트 테이블의 현재 구조를 정의합니다.
- 그룹 추천 이전 단계의 협업 단위와 멤버십 관리 기준을 설명합니다.

## 현재 확정 전제

- 그룹 방은 점심 메뉴 합의를 위한 협업 단위입니다.
- 그룹 방은 고정 초대 코드 `invite_code`를 가집니다.
- 그룹 멤버십은 `group_room_members`로 관리하고, 방장도 멤버 row를 가집니다.
- 그룹 위치는 추천 기준 위치를 기억하기 위한 보조 데이터입니다.
- presence 이벤트는 접속/퇴장 이벤트 로그이며 현재 상태 테이블이 아닙니다.

가정(Assumption):

- 운영상 최신 위치 1개를 사용하지만 향후 이력 확장을 위해 `group_rooms`와 `group_locations`는 1:N 구조로 둡니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `group_rooms` | 그룹 방 | `GroupRoom` |
| `group_room_members` | 그룹 방 멤버십 | `GroupRoomMember` |
| `group_locations` | 그룹 추천 기준 위치 | `GroupLocation` |
| `group_invites` | nickname 기반 직접 초대 요청 | `GroupInvite` |
| `group_invite_links` | UUID 토큰 기반 링크 초대 | `GroupInviteLink` |
| `group_presence_events` | 그룹 입퇴장 이벤트 로그 | `GroupPresenceEvent` |

## `group_rooms`

### 역할

- 그룹명, 고정 초대 코드, 방장, 방 상태를 저장합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 방 ID |
| `name` | varchar(100) | N |  |  | 그룹명 |
| `invite_code` | varchar(32) | N |  | unique | 그룹 고정 초대 코드 |
| `host_member_id` | bigint | N |  | FK | 방장 회원 ID |
| `status` | varchar(20) | N |  | enum | 그룹 방 상태 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 그룹 방 식별자 |
| FK | `fk_group_rooms_host_member` | `host_member_id -> members.id` | 방장 회원 |
| unique | `uk_group_rooms_invite_code` | `invite_code` | 초대 코드 중복 방지 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `status` | `ACTIVE` | 활성 방 |
| `status` | `CLOSED` | 닫힌 방 |
| `status` | `DELETED` | 삭제 처리 방 |

## `group_room_members`

### 역할

- 그룹 방과 회원의 멤버십, 역할, 참여 상태를 저장합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 방 멤버 ID |
| `room_id` | bigint | N |  | FK, unique 조합 | 그룹 방 ID |
| `member_id` | bigint | N |  | FK, unique 조합 | 회원 ID |
| `role` | varchar(20) | N |  | enum | 그룹 멤버 역할 |
| `status` | varchar(20) | N |  | enum | 그룹 멤버 상태 |
| `joined_at` | datetime | N |  |  | 참여 시각 |
| `left_at` | datetime | Y |  |  | 퇴장/강퇴 시각 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 멤버십 식별자 |
| FK | `fk_group_room_members_room` | `room_id -> group_rooms.id` | 그룹 방 |
| FK | `fk_group_room_members_member` | `member_id -> members.id` | 회원 |
| unique | `uk_group_room_member` | `room_id`, `member_id` | 같은 방에 같은 회원 중복 가입 방지 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `role` | `OWNER` | 방장 |
| `role` | `MEMBER` | 일반 멤버 |
| `status` | `ACTIVE` | 참여 중 |
| `status` | `LEFT` | 자발적 퇴장 |
| `status` | `KICKED` | 강퇴 |

## `group_locations`

### 역할

- 그룹 추천 기준 위치를 저장합니다.
- 위치는 위도, 경도, 반경 거리, 주소 문자열로 구성합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 위치 ID |
| `group_room_id` | bigint | N |  | FK by JPA | 그룹 방 ID |
| `latitude` | decimal(10,7) | Y |  |  | 위도 |
| `longitude` | decimal(10,7) | Y |  |  | 경도 |
| `radius_meters` | int | Y |  |  | 반경 거리 |
| `address` | varchar(255) | Y |  |  | 주소 문자열 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 위치 식별자 |
| FK | JPA 자동 생성 | `group_room_id -> group_rooms.id` | 필수 관계 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

## `group_invites`

### 역할

- 특정 회원이 다른 회원에게 보낸 그룹 직접 초대 요청을 저장합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 초대 ID |
| `room_id` | bigint | N |  | FK | 그룹 방 ID |
| `request_member_id` | bigint | N |  | FK | 초대 생성 회원 ID |
| `target_member_id` | bigint | N |  | FK | 초대 대상 회원 ID |
| `status` | varchar(20) | N |  | enum | 초대 상태 |
| `expires_at` | datetime | Y |  |  | 만료 시각 |
| `responded_at` | datetime | Y |  |  | 응답 시각 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 초대 식별자 |
| FK | `fk_group_invites_room` | `room_id -> group_rooms.id` | 초대 방 |
| FK | `fk_group_invites_request_member` | `request_member_id -> members.id` | 요청 회원 |
| FK | `fk_group_invites_target_member` | `target_member_id -> members.id` | 대상 회원 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `status` | `PENDING` | 응답 대기 |
| `status` | `ACCEPTED` | 수락 |
| `status` | `DECLINED` | 거절 |
| `status` | `EXPIRED` | 만료 |
| `status` | `REVOKED` | 철회 |

## `group_invite_links`

### 역할

- 방장이 발급한 UUID 기반 그룹 초대 링크 토큰과 만료 시각을 저장합니다.
- 별도 상태 컬럼 없이 `expires_at > 현재 시각`이면 활성 링크로 판단합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 그룹 링크 초대 ID |
| `room_id` | bigint | N |  | FK | 그룹 방 ID |
| `token` | varchar(36) | N |  | unique | URL 끝에 붙이는 UUID 기반 토큰 |
| `expires_at` | datetime | N |  |  | 만료 시각 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 링크 초대 식별자 |
| FK | JPA 자동 생성 | `room_id -> group_rooms.id` | 초대 대상 그룹 |
| unique | `uk_group_invite_links_token` | `token` | 토큰 중복 방지 |

### 인덱스

- 토큰 unique 제약 인덱스를 사용합니다.
- 그룹별 현재 링크 조회용 보조 인덱스는 실제 실행 계획을 확인한 뒤 도입합니다.

## `group_presence_events`

### 역할

- 그룹 방 입장/퇴장 이벤트를 로그로 저장합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | presence 이벤트 ID |
| `room_id` | bigint | N |  | FK | 그룹 방 ID |
| `member_id` | bigint | N |  | FK | 회원 ID |
| `event_type` | varchar(20) | N |  | enum | 이벤트 유형 |
| `websocket_session_id` | varchar(100) | Y |  |  | 웹소켓 세션 ID |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |

`group_presence_events`는 `CreatedAtEntity`를 사용하므로 `updated_at`이 없습니다.

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 이벤트 식별자 |
| FK | `fk_group_presence_events_room` | `room_id -> group_rooms.id` | 그룹 방 |
| FK | `fk_group_presence_events_member` | `member_id -> members.id` | 회원 |

### 인덱스

- 현재 명시 보조 인덱스는 없습니다. 실제 조회 성능과 실행 계획을 비교한 뒤 도입합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `event_type` | `JOIN` | 입장 |
| `event_type` | `LEAVE` | 퇴장 |

## 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 | 주의점 |
| --- | --- | --- | --- |
| 그룹 생성 | `host_member_id`, `invite_code` | 그룹 방과 방장 멤버 row 생성 | 초대 코드 unique |
| 멤버 참여 | `room_id`, `member_id` | 멤버 row 생성 또는 재참여 처리 | 중복 멤버십 unique |
| 멤버 퇴장/강퇴 | `room_id`, `member_id` | 상태와 `left_at` 갱신 | 방장 권한 확인 |
| 위치 저장 | `group_room_id` | 최신 위치 row 갱신 또는 생성 | JPA 필수 관계 유지 |
| 초대 응답 | `id`, `target_member_id` | 상태와 `responded_at` 갱신 | 만료/이미 응답 처리 |
| 링크 신규 발급 | `room_id`, `expires_at` | 활성 링크가 없을 때 UUID 토큰과 1일 만료 시각 저장 | 그룹 행 잠금으로 동시 발급 직렬화 |
| 링크 재발급 | `room_id`, `expires_at` | 기존 활성 링크 즉시 만료 후 새 링크 저장 | 이전 토큰 즉시 무효화 |
| 링크 참여 | `token`, `expires_at` | 유효한 토큰의 그룹 멤버십 생성 또는 재활성화 | 인증 회원만 허용 |

## 운영 기준

- 그룹 방 삭제는 물리 삭제보다 `status=DELETED` 전환을 우선합니다.
- 그룹 멤버 퇴장/강퇴도 멤버십 row를 보존하고 상태를 전환합니다.
- 고정 초대 코드는 `group_rooms.invite_code` 기준입니다.
- 링크 초대는 이력을 보존하며 활성 여부를 `group_invite_links.expires_at`으로 판단합니다.

## 현재 제외 범위

- 그룹별 권한 상세 테이블
- 위치 이력 조회 API 전제 구조
- presence 현재 상태 materialized table

## 코드 변경 시 확인할 것

- 그룹 상태값이나 멤버 상태값 추가 시 권한 체크, 목록 조회 필터, API 문서를 함께 확인합니다.
- 관계와 제약을 바꾸면 JPA Entity 및 빈 DB 기동 검증을 함께 갱신해야 합니다.
- presence 이벤트가 현재 상태 판단에 쓰이기 시작하면 별도 상태 저장 구조를 검토합니다.

## 함께 볼 문서

- [회원 테이블 정의서](./members-schema.md)
- [그룹 추천 테이블 정의서](./group-recommendations-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-08-14
