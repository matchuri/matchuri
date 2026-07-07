# 회원 필수 약관 동의 데이터 상세 설계 초안

## 문서 상태

- 상태: 폐기 예정 참고 문서
- 기준일: 2026-07-02
- 담당 영역: member
- 기준 소스:
  - 과거 구현 전 설계 초안
  - 현재 구현 기준 문서: [회원 약관 동의 테이블 정의서](./member-agreements-schema.md)

## 문서 목적

- 이 문서는 `member_agreements` 구현 전에 작성했던 설계 초안의 위치를 보존합니다.
- 현재 운영 테이블 정의서로 사용하지 않습니다.
- 필수 약관 동의의 현재 컬럼, 제약, 운영 기준은 [회원 약관 동의 테이블 정의서](./member-agreements-schema.md)를 우선합니다.

## 현재 기준

| 항목 | 현재 기준 문서 |
| --- | --- |
| `member_agreements` 컬럼 정의 | [회원 약관 동의 테이블 정의서](./member-agreements-schema.md) |
| `AgreementType` enum | [회원 약관 동의 테이블 정의서](./member-agreements-schema.md) |
| 필수 약관 완료 여부 계산 | [회원 약관 동의 테이블 정의서](./member-agreements-schema.md) |
| 전체 운영 테이블 목록 | [현재 구현 테이블 정의서 인덱스](./implemented-jpa-data-model.md) |


- 필수 약관 동의는 `member_agreements` 테이블에 저장합니다.
- 완료 여부는 `members`의 boolean 컬럼으로 저장하지 않고 약관 동의 이력과 서버 상수 버전을 비교해 계산합니다.
- 같은 회원의 같은 약관 타입/버전 중복 동의는 unique 제약과 서비스 멱등 처리로 막습니다.
- 약관 마스터 테이블, 선택 약관, 약관 철회 이력은 MVP 범위에서 제외했습니다.

## 주의

- 이 문서의 내용을 기준으로 새 구현을 진행하지 않습니다.
- 현재 구현과 이 문서가 다르면 [회원 약관 동의 테이블 정의서](./member-agreements-schema.md)를 따릅니다.
- 과거 논의 맥락이 필요할 때만 참고합니다.

## 함께 볼 문서

- [회원 약관 동의 테이블 정의서](./member-agreements-schema.md)
- [회원 테이블 정의서](./members-schema.md)
- [데이터 문서 인덱스](./index.md)

## 마지막 갱신

- 2026-07-02
