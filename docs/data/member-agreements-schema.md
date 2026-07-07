# 회원 약관 동의 테이블 정의서

## 문서 상태

- 상태: 현재 구현 기준
- 기준일: 2026-07-02
- 담당 영역: member
- 기준 소스:
  - JPA Entity: `MemberAgreement`, `AgreementType`
  - DDL / init SQL: `backend/init/sql/01-schema.sql`
  - 관련 API 문서: `docs/api/member-required-agreements.md`

## 기준 소스 우선순위

1. JPA Entity와 enum
2. `backend/init/sql/01-schema.sql`
3. 약관 동의 service write path와 repository query
4. 관련 API 문서
5. 기존 `docs/data/`

| 충돌 항목 | 코드 기준 | 문서/DDL 기준 | 판단 | 후속 작업 |
| --- | --- | --- | --- | --- |
| 없음 |  |  |  |  |

## 문서 목적

- `member_agreements` 테이블의 현재 컬럼, 제약, 완료 여부 계산 기준을 정의합니다.
- 구현 전 초안인 `member-required-agreements-schema.md`와 구분되는 현재판 역할을 합니다.

## 현재 확정 전제

- 현재 약관 이력은 `member_agreements` 단일 테이블에 저장합니다.
- 필수 약관 타입은 `TERMS_OF_SERVICE`, `PRIVACY_POLICY`입니다.
- 최신 필수 버전은 DB가 아니라 서버 상수 `RequiredAgreementVersions`로 관리합니다.
- 필수 약관 완료 여부는 별도 boolean 컬럼으로 저장하지 않습니다.

가정(Assumption):

- MVP에서는 약관 철회, 선택 약관, 약관 마스터 테이블을 구현하지 않습니다.

## 테이블 목록

| 테이블 | 역할 | 기준 소스 |
| --- | --- | --- |
| `member_agreements` | 회원별 약관 타입/버전 동의 이력 | `MemberAgreement`, `01-schema.sql` |

## `member_agreements`

### 역할

- 회원이 어떤 약관 타입의 어떤 버전에 동의했는지 기록합니다.
- 필수 약관 완료 여부 계산의 근거가 됩니다.
- 약관 개정 시 재동의 대상 판별에 사용합니다.

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 제약/기타 | 설명 |
| --- | --- | --- | --- | --- | --- |
| `id` | bigint | N |  | PK, auto increment | 회원 약관 동의 ID |
| `member_id` | bigint | N |  | FK, unique 조합 | 동의 회원 ID |
| `agreement_type` | varchar(50) | N |  | enum, unique 조합 | 약관 종류 |
| `agreement_version` | varchar(50) | N |  | unique 조합 | 동의한 약관 버전 |
| `agreed_at` | datetime | N |  |  | 동의 시각 |
| `created_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 생성 일시 |
| `updated_at` | datetime | N | CURRENT_TIMESTAMP(6) | auditing | 수정 일시 |

### 제약조건

| 구분 | 이름 | 컬럼 | 설명 |
| --- | --- | --- | --- |
| PK |  | `id` | 약관 동의 식별자 |
| FK | `fk_member_agreements_member` | `member_id -> members.id` | 동의 회원 |
| unique | `uk_member_agreements_member_type_version` | `member_id`, `agreement_type`, `agreement_version` | 같은 회원의 같은 약관/버전 중복 동의 방지 |

### 인덱스

- 현재 명시 보조 인덱스 없음
- `(member_id, agreement_type, agreement_version)` unique 제약으로 상태 조회와 멱등 저장을 보조합니다.

### enum / 상태값

| 컬럼 | 값 | 설명 |
| --- | --- | --- |
| `agreement_type` | `TERMS_OF_SERVICE` | 서비스 이용약관 |
| `agreement_type` | `PRIVACY_POLICY` | 개인정보 처리방침 |

### 관계

| 기준 | 대상 | 관계 | 설명 |
| --- | --- | --- | --- |
| `member_agreements.member_id` | `members.id` | N : 1 | 약관 동의 주체 |

### 주요 쿼리 / 쓰기 패턴

| 상황 | 기준 컬럼 | 동작 | 주의점 |
| --- | --- | --- | --- |
| 완료 여부 조회 | `member_id`, `agreement_type`, `agreement_version` | 최신 필수 버전 동의 존재 여부 확인 | 최신 버전은 서버 상수 기준 |
| 동의 저장 | `member_id`, `agreement_type`, `agreement_version` | 없으면 insert, 있으면 기존 row 유지 | 중복 제출은 멱등 성공 처리 |

### 운영 기준

- 필수 약관 완료는 `TERMS_OF_SERVICE`와 `PRIVACY_POLICY`의 최신 필수 버전에 모두 동의했을 때 true입니다.
- 약관 완료 여부는 `members.status`와 분리된 파생 판단값입니다.
- 버전 문자열은 사용자가 실제 동의한 버전을 보존합니다.

### 현재 제외 범위

- `agreements` 마스터 테이블
- 약관 전문 HTML/Markdown DB 저장
- 약관 철회 이력 컬럼
- 선택 약관
- 관리자 약관 버전 관리 UI

## 영역 공통 판단

- 계정 생성과 서비스 이용 조건 충족을 분리합니다.
- 동의 기록은 감사성 데이터이므로 물리 삭제보다 이력 보존을 우선합니다.

## 코드 변경 시 확인할 것

- `AgreementType` 추가 시 필수/선택 여부, 완료 여부 계산, API 응답을 함께 확인합니다.
- `RequiredAgreementVersions` 변경 시 재동의 대상 판별과 문서 버전 예시를 확인합니다.
- unique 제약 변경 시 중복 제출 멱등성이 깨지지 않는지 확인합니다.

## 함께 볼 문서

- [회원 테이블 정의서](./members-schema.md)
- [회원 필수 약관 동의 데이터 상세 설계 초안](./member-required-agreements-schema.md)
- [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md)

## 마지막 갱신

- 2026-07-02
