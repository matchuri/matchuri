# 회원 필수 약관 동의 테스트 시나리오

이 문서는 Matchuri의 필수 약관 동의 기능을 구현할 때 확인해야 하는 테스트 시나리오 초안입니다.
목적은 서비스 로직, API 계약, 접근 제어가 설계 문서와 같은 동작을 하는지 검증 포인트를 미리 고정하는 것입니다.

## 문서 목적

- 서비스 단위 테스트와 API 통합 테스트의 핵심 시나리오를 정리합니다.
- 약관 상태 조회, 동의 제출, 핵심 API 차단 흐름을 빠짐없이 검증하도록 돕습니다.
- 자체 로그인과 소셜 로그인 이후 동일한 약관 흐름을 검증하는 기준을 만듭니다.

## 범위

- 필수 약관 상태 조회
- 필수 약관 동의 제출
- 중복 제출 멱등 처리
- 버전 불일치 처리
- 미동의 회원 핵심 API 차단

## 비범위

- 프론트 UI 렌더링 테스트
- 약관 전문 콘텐츠 표시 테스트
- 관리자 약관 버전 관리 테스트

## 테스트 레벨 권장안

### 서비스 단위 테스트

- 필수 약관 완료 여부 계산
- 필수 약관 누락 검증
- 버전 불일치 검증
- 멱등 처리 검증

### API 통합 테스트

- 인증 후 상태 조회 응답 검증
- 동의 제출 요청/응답 검증
- 에러 코드와 HTTP status 검증

### 접근 제어 테스트

- 미동의 회원의 허용 API 접근
- 미동의 회원의 핵심 API 차단
- 동의 완료 후 핵심 API 허용

## 공통 전제 데이터

권장 전제:

- 회원 A: 로그인 가능, 약관 미동의
- 회원 B: `TERMS_OF_SERVICE`만 동의
- 회원 C: `PRIVACY_POLICY`만 동의
- 회원 D: 두 필수 약관 모두 최신 필수 버전에 동의
- 회원 E: 이전 버전에만 동의

가정(Assumption):

- 최신 필수 버전 예시는 `2026-04-10` 문자열을 사용합니다.

## 상태 조회 시나리오

### 1. 두 약관 모두 미동의

- Given:
  - 로그인한 회원에게 `member_agreements` 레코드가 없다.
- When:
  - `GET /api/v1/member-agreements/required-status`
- Then:
  - `200`
  - `requiredAgreementsCompleted=false`
  - `missingAgreementTypes`에 `TERMS_OF_SERVICE`, `PRIVACY_POLICY` 포함

### 2. 한 종류만 동의

- Given:
  - 로그인한 회원이 `TERMS_OF_SERVICE` 최신 버전에만 동의했다.
- When:
  - 상태 조회 호출
- Then:
  - `requiredAgreementsCompleted=false`
  - `missingAgreementTypes`에 `PRIVACY_POLICY`만 포함

### 3. 두 종류 모두 최신 버전 동의

- Given:
  - 로그인한 회원이 두 필수 약관 모두 최신 버전에 동의했다.
- When:
  - 상태 조회 호출
- Then:
  - `requiredAgreementsCompleted=true`
  - `missingAgreementTypes=[]`

### 4. 이전 버전에만 동의

- Given:
  - 로그인한 회원이 두 약관 모두 존재하지만 현재 최신 버전보다 이전 버전에만 동의했다.
- When:
  - 상태 조회 호출
- Then:
  - `requiredAgreementsCompleted=false`
  - 필요한 타입이 누락 상태로 계산된다.

### 5. 과거 버전과 최신 버전이 함께 있어도 완료 상태 유지

- Given:
  - 로그인한 회원이 같은 약관 타입에 대해 이전 버전과 최신 버전 이력을 모두 가지고 있다.
- When:
  - 상태 조회 호출
- Then:
  - `requiredAgreementsCompleted=true`
  - 과거 버전 레코드 때문에 최신 동의 상태가 무효화되지 않는다.

### 6. 인증 없이 상태 조회

- Given:
  - Access Token이 없다.
- When:
  - 상태 조회 호출
- Then:
  - `401`
  - 인증 관련 공통 에러 코드 반환

## 동의 제출 시나리오

### 7. 두 필수 약관 최신 버전 정상 제출

- Given:
  - 로그인한 회원이 미동의 상태다.
- When:
  - `POST /api/v1/member-agreements/consents`
  - `TERMS_OF_SERVICE`, `PRIVACY_POLICY` 최신 버전 함께 제출
- Then:
  - `200`
  - `requiredAgreementsCompleted=true`
  - 새 `accessToken`이 응답에 포함된다.
  - `member_agreements`에 두 레코드 저장

### 8. 한 종류만 제출

- Given:
  - 로그인한 회원
- When:
  - 한 종류만 포함해 동의 제출
- Then:
  - `400`
  - `MEMBER_AGREEMENT_REQUIRED_TYPES_MISSING`

### 9. 잘못된 약관 타입 제출

- Given:
  - 로그인한 회원
- When:
  - 지원하지 않는 `agreementType` 제출
- Then:
  - `400`
  - `MEMBER_AGREEMENT_INVALID_TYPE`

### 10. 최신 버전과 다른 버전 제출

- Given:
  - 서버 최신 필수 버전은 `2026-04-10`
- When:
  - `2026-03-01` 같은 이전 버전 제출
- Then:
  - `409`
  - `MEMBER_AGREEMENT_VERSION_MISMATCH`

### 11. 동일 타입/버전 중복 제출

- Given:
  - 로그인한 회원이 이미 같은 타입/버전에 동의했다.
- When:
  - 같은 요청을 다시 제출한다.
- Then:
  - 성공 응답
  - 중복 레코드가 추가 생성되지 않는다.

### 12. 인증 없이 동의 제출

- Given:
  - Access Token이 없다.
- When:
  - 동의 제출 호출
- Then:
  - `401`
  - 인증 관련 공통 에러 코드 반환

## 접근 제어 시나리오

### 13. 미동의 회원은 약관 상태 조회 가능

- Given:
  - 로그인한 회원이 필수 약관 미완료 상태
- When:
  - 상태 조회 API 호출
- Then:
  - `200`

### 14. 미동의 회원은 동의 제출 가능

- Given:
  - 로그인한 회원이 필수 약관 미완료 상태
- When:
  - 동의 제출 API 호출
- Then:
  - `200` 또는 검증 실패 시 정의된 오류 반환

### 15. 미동의 회원은 로그아웃 가능

- Given:
  - 로그인한 회원이 필수 약관 미완료 상태
- When:
  - 로그아웃 호출
- Then:
  - 로그아웃 정책에 맞는 정상 응답

### 16. 미동의 회원은 핵심 API 차단

- Given:
  - 로그인한 회원이 필수 약관 미완료 상태
- When:
  - 개인 추천 또는 그룹 API 호출
- Then:
  - `403`
  - `MEMBER_AGREEMENT_REQUIRED`

### 17. 약관 동의 완료 후 닉네임 미완료면 핵심 API 차단

- Given:
  - 로그인한 회원이 두 필수 약관 최신 버전에 모두 동의했다.
  - `nicknameCompleted=false`
- When:
  - 약관 동의 응답의 새 Access Token으로 핵심 보호 API 호출
- Then:
  - `403`
  - `MEMBER_NICKNAME_REQUIRED`

### 18. 닉네임 미완료 회원은 닉네임 설정 API를 호출할 수 있다.

- Given:
  - 로그인한 회원이 두 필수 약관 최신 버전에 모두 동의했다.
  - `nicknameCompleted=false`
- When:
  - `PATCH /api/v1/members/me`로 닉네임 수정
- Then:
  - 성공 응답
  - 응답의 `data.onboarding.nextStep=READY`

### 19. 약관과 닉네임 완료 후 핵심 API 허용

- Given:
  - 로그인한 회원이 두 필수 약관 최신 버전에 모두 동의했다.
  - `nicknameCompleted=true`
- When:
  - 핵심 보호 API 호출
- Then:
  - 온보딩 미완료 차단이 발생하지 않는다.

### 20. 약관 동의 완료 후 기존 Access Token은 계속 차단

- Given:
  - 로그인 직후 발급된 Access Token으로는 필수 약관 미완료 상태다.
- When:
  - 약관 동의 제출은 성공했지만, 기존 Access Token으로 핵심 보호 API를 호출한다.
- Then:
  - `403`
  - `MEMBER_AGREEMENT_REQUIRED`

## 자체 로그인/소셜 로그인 연결 시나리오

### 21. 자체 로그인 후 약관 미완료 상태

- Given:
  - 자체 로그인 회원 생성 후 아직 약관 미동의
- When:
  - 로그인 성공 후 상태 조회
- Then:
  - 필수 약관 미완료 상태가 반환된다.

### 22. 소셜 신규 가입 후 약관 미완료 상태

- Given:
  - 신규 소셜 회원이 최초 로그인 성공
- When:
  - 후속 토큰 교환 후 상태 조회
- Then:
  - 필수 약관 미완료 상태가 반환된다.

### 23. 자체 로그인과 소셜 로그인 모두 동일한 완료 기준 사용

- Given:
  - 자체 로그인 회원과 소셜 회원이 같은 약관 동의 이력을 가진다.
- When:
  - 상태 조회 호출
- Then:
  - 동일한 완료 여부 판단 결과가 나온다.

## 저장소/무결성 시나리오

### 24. 유니크 제약 보장

- Given:
  - 동일 회원, 동일 타입, 동일 버전 조합
- When:
  - 저장이 중복 시도된다.
- Then:
  - DB 제약 또는 서비스 멱등 처리로 중복 데이터가 남지 않는다.

### 25. 서로 다른 버전은 별도 기록 가능

- Given:
  - 회원이 이전 버전과 최신 버전에 각각 동의한 상황
- When:
  - 두 버전 레코드를 조회한다.
- Then:
  - 각 버전 이력이 구분되어 저장될 수 있다.

## 문서/계약 검증 포인트

- `requiredAgreementsCompleted` 필드명이 실제 구현과 일치하는가
- `missingAgreementTypes` 값이 enum 문자열과 일치하는가
- 동의 제출 성공 응답의 `accessToken`, `expiresIn` 필드가 실제 구현과 일치하는가
- 에러 코드 문자열이 문서와 구현에서 동일한가
- `403` 차단 응답이 인증 실패와 혼동되지 않는가

## 최소 회귀 세트 권장안

구현 후 최소한 아래 시나리오는 회귀 세트에 포함하는 것이 좋습니다.

1. 상태 조회: 미동의
2. 상태 조회: 완료
3. 동의 제출: 정상
4. 동의 제출: 버전 불일치
5. 동의 제출: 중복 제출
6. 미동의 회원 핵심 API 차단
7. 닉네임 미완료 회원 핵심 API 차단
8. 닉네임 설정 API 온보딩 예외
9. 온보딩 완료 후 핵심 API 허용

## 후속 문서화 항목

- 실제 테스트 클래스 위치와 이름 반영
- REST Docs 스니펫 대상 시나리오 확정
- OAuth2 통합 테스트 범위 확정
