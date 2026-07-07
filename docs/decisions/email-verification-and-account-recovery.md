# 이메일 인증과 계정 복구 설계

이 문서는 Matchuri의 이메일 인증, 로그인 ID 찾기, 비밀번호 재설정 흐름을 같은 기준으로 설계하기 위한 문서입니다.
현재 직접 구현된 이메일 발송 코드를 출발점으로 삼되, 계정 복구까지 이어질 수 있는 운영 가능한 구조를 목표로 합니다.

## 배경

개발 중 자체 로그인 계정에서 로그인 ID와 비밀번호를 찾을 수 없는 문제가 확인됐습니다.
이를 해결하려면 사용자가 계정 소유자임을 증명할 수 있는 수단이 필요하고, 현재 단계에서는 이메일 인증이 가장 단순한 선택입니다.

이 기능은 맛추리의 핵심 추천 기능은 아니지만, 회원 가입과 재방문 경험의 신뢰성을 받치는 기반 기능입니다.
특히 취향 프로필, 추천 이력, 그룹 참여 이력이 회원 계정에 묶이기 때문에 계정 복구가 되지 않으면 사용자가 쌓아둔 의사결정 맥락을 잃을 수 있습니다.

## 리팩토링 전 코드 초안

현재 구현된 핵심 파일은 아래와 같습니다.

- `backend/src/main/java/matchuri/backend/api/auth/EmailApi.java`
- `backend/src/main/java/matchuri/backend/api/auth/EmailController.java`
- `backend/src/main/java/matchuri/backend/domain/auth/entity/EmailVerification.java`
- `backend/src/main/java/matchuri/backend/domain/auth/service/EmailVerificationServiceImpl.java`

첫 번째 API 리팩토링 전 코드가 이미 제공하던 것:

- Gmail SMTP 기반 텍스트 메일 발송
- 6자리 인증 코드 생성
- 이메일, 코드, 인증 타입 저장
- `POST /api/v1/auth/email` 공개 API 초안

첫 번째 API 리팩토링 전 코드에서 후속 정리가 필요했던 것:

- 요청 DTO와 응답 DTO가 domain service까지 직접 전달됩니다.
- 인증 코드 검증 API가 없습니다.
- 만료 시간, 검증 시도 횟수, 재발송 제한, 사용 완료 상태가 없습니다.
- 인증 코드가 평문으로 저장됩니다.
- 발송 실패 시 저장된 인증 레코드 정합성 기준이 불명확합니다.
- `support/vertification` 패키지명 오타가 있습니다. 목표 패키지명은 `support/verification`입니다.
- `EmailVerificationType.LOGIN`, `PASSWORD`는 목적이 모호합니다.
- 현재 테이블명 `email_verification`은 기존 인증 테이블명인 `auth_refresh_tokens`, `auth_exchange_codes`와 명명 규칙이 다릅니다.
- `spring.mail.username`에 실제 계정 문자열이 직접 들어가 있어 운영 시크릿 관리 기준과 어긋납니다.

2026-04-26 첫 번째 API 구현 반영:

- `POST /api/v1/auth/email`은 목표 계약의 `email`, `purpose`, `loginId` 요청과 `accepted`, `resendAvailableAfterSeconds` 응답으로 정리했습니다.
- domain service의 API DTO 직접 의존을 `SendEmailVerificationCommand`, `SendEmailVerificationResult`로 분리했습니다.
- 인증 코드는 평문 대신 `codeHash`로 저장합니다.
- `EmailVerificationPurpose`, `EmailVerificationStatus`, `auth_email_verifications` 테이블명 기준으로 엔티티를 정리했습니다.
- `support/vertification` 오타는 `support/verification`으로 정리했습니다.
- SMTP username/password는 환경 변수 기반 설정으로 정리했습니다.
- `POST /api/v1/auth/email/confirm` 인증 확인 API를 추가하고, 성공 시 DB 저장형 랜덤 `emailVerificationToken`을 발급합니다.
- 자체 회원가입 통합 API에서 `SIGNUP` 목적 `emailVerificationToken` 검증, 이메일 중복 검사, 회원 email 저장, token 사용 완료 처리를 연결했습니다.
- 로그인 ID 찾기 API에서 `FIND_LOGIN_ID` 목적 token 검증, 단일 loginId 반환, token 사용 완료 처리를 연결했습니다.
- 비밀번호 재설정 API에서 `RESET_PASSWORD` 목적 token 검증, 비밀번호 해시 교체, refresh token 전체 폐기, token 사용 완료 처리를 연결했습니다.

## 목표

- 이메일 인증을 회원가입, 로그인 ID 찾기, 비밀번호 재설정의 공통 기반으로 둡니다.
- MVP 프로토타입에서는 회원가입 중복 이메일을 명시해 사용자 흐름을 단순화하되, 계정 복구 목적에서는 계정 존재 여부를 과도하게 노출하지 않는 API 응답을 유지합니다.
- Redis 없이 MySQL과 Spring Boot만으로 MVP 수준의 재시도, 만료, 검증 흐름을 처리합니다.
- 인증 코드는 평문 저장하지 않습니다.
- 프론트가 구현하기 쉬운 단계형 API 계약을 제공합니다.
- 기존 auth 도메인의 `service`, `command`, `result`, `support`, `exception` 구조를 따릅니다.

## 범위

- 이메일 인증 코드 발송
- 이메일 인증 코드 확인
- 로그인 ID 찾기
- 비밀번호 재설정
- 자체 로그인 회원가입의 이메일 인증 연계 설계
- 현재 이메일 발송 코드 리팩토링 방향

## 범위 제외

- 이메일 HTML 템플릿 고도화
- 대량 메일 발송 시스템
- Redis 기반 rate limit
- 계정 병합
- 소셜 계정과 자체 계정 자동 연결
- 관리자용 계정 복구

## 제품 결정

### 자체 로그인 계정과 이메일

로그인 ID 찾기와 비밀번호 재설정을 제공하려면 계정 소유 확인 수단이 필요합니다.
따라서 신규 자체 회원가입부터 이메일 인증을 필수로 둡니다.

확정 기준:

- 신규 자체 로그인 회원가입은 `loginId`, `password`, `nickname`, `email`, 필수 약관 동의를 함께 받습니다.
- 회원 생성 전에 이메일 인증이 완료되어야 합니다.
- 기존 자체 로그인 계정 중 이메일이 없는 계정은 로그인 ID 찾기와 비밀번호 재설정을 사용할 수 없습니다.
- 기존 계정 이메일 보강은 별도 마이그레이션 또는 프로필 이메일 인증 기능으로 후속 처리합니다.

### 이메일 유니크 여부

자체 로그인 계정은 같은 이메일을 중복 사용할 수 없습니다.

확정 기준:

- 신규 자체 회원가입에서는 검증된 이메일이 기존 자체 로그인 계정에 이미 사용 중이면 가입을 거절합니다.
- 로그인 ID 찾기는 인증된 이메일에 연결된 자체 로그인 ID 1개를 반환합니다.
- 기존 자체 로그인 계정 중 같은 이메일을 가진 데이터가 발견되면 데이터 보정 대상으로 봅니다.

소셜 계정과 자체 계정의 같은 이메일 처리 방식은 자동 병합하지 않는 기존 정책을 유지합니다.
따라서 초기 구현은 자체 로그인 계정 범위의 이메일 중복을 애플리케이션 규칙으로 먼저 막고, DB 제약 강화는 실제 스키마 전환 부담을 보고 후속 검토합니다.

## 인증 목적

이메일 인증 목적은 enum으로 명확히 분리합니다.

| 목적 | 설명 | 추가 입력 |
| --- | --- | --- |
| `SIGNUP` | 자체 회원가입 이메일 소유 확인 | 없음 |
| `FIND_LOGIN_ID` | 이메일 기준 로그인 ID 조회 | 없음 |
| `RESET_PASSWORD` | 비밀번호 재설정 전 소유 확인 | `loginId` |

현재 코드의 `LOGIN`, `PASSWORD`는 후속 리팩토링에서 각각 `FIND_LOGIN_ID`, `RESET_PASSWORD`로 바꿉니다.

## 사용자 흐름

### 회원가입 이메일 인증

1. 사용자가 회원가입 화면에서 이메일을 입력합니다.
2. 프론트는 `purpose=SIGNUP`으로 인증 코드 발송 API를 호출합니다.
3. 이미 가입된 자체 로그인 이메일이면 서버는 `MEMBER_DUPLICATE_EMAIL`을 반환합니다.
4. 사용 가능한 이메일이면 서버는 인증 코드를 생성하고 이메일로 전송합니다.
5. 사용자는 이메일로 받은 코드를 입력합니다.
6. 프론트는 인증 코드 확인 API를 호출합니다.
7. 서버는 짧게 유효한 `emailVerificationToken`을 발급합니다.
8. 프론트는 회원가입 API에 `email`과 `emailVerificationToken`을 함께 전달합니다.
9. 서버는 토큰이 `SIGNUP` 목적이고 해당 이메일에 대해 유효한지 확인한 뒤 회원을 생성합니다.

### 로그인 ID 찾기

1. 사용자가 이메일을 입력합니다.
2. 프론트는 `purpose=FIND_LOGIN_ID`로 인증 코드 발송 API를 호출합니다.
3. 서버는 계정 존재 여부와 무관하게 동일한 성공 응답을 반환합니다.
4. 이메일이 복구 가능한 계정과 연결되어 있으면 인증 코드가 발송됩니다.
5. 사용자가 인증 코드를 확인합니다.
6. 서버는 인증 성공 시 `emailVerificationToken`을 발급합니다.
7. 프론트는 로그인 ID 찾기 API에 토큰을 전달합니다.
8. 서버는 해당 이메일의 자체 로그인 ID를 반환합니다.

주의:

- 이메일이 등록되지 않았더라도 발송 요청 응답은 동일하게 유지합니다.
- 실제 코드 발송 여부를 응답으로 드러내지 않습니다.
- 인증 코드 확인 단계에서 유효한 인증 레코드가 없으면 일반적인 인증 실패로 처리합니다.

### 비밀번호 재설정

1. 사용자가 `loginId`와 이메일을 입력합니다.
2. 프론트는 `purpose=RESET_PASSWORD`, `loginId`로 인증 코드 발송 API를 호출합니다.
3. 서버는 계정 일치 여부와 무관하게 동일한 성공 응답을 반환합니다.
4. 일치하는 활성 자체 로그인 계정이면 인증 코드가 발송됩니다.
5. 사용자가 인증 코드를 확인합니다.
6. 서버는 인증 성공 시 `emailVerificationToken`을 발급합니다.
7. 프론트는 새 비밀번호와 토큰을 비밀번호 재설정 API에 전달합니다.
8. 서버는 토큰 목적과 회원 매칭을 확인하고 비밀번호 해시를 교체합니다.
9. 서버는 해당 회원의 기존 refresh token을 모두 폐기합니다.
10. 서버는 현재 응답의 refresh token cookie를 만료시켜 같은 브라우저의 남은 cookie 상태도 즉시 정리합니다.

## API 설계 원칙

- `SIGNUP` 목적의 이메일 인증 발송 API는 이미 가입된 자체 로그인 이메일이면 중복 이메일 오류를 반환합니다.
- `FIND_LOGIN_ID`, `RESET_PASSWORD` 목적의 이메일 인증 발송 API 응답은 계정 존재 여부를 알려주지 않습니다.
- 인증 코드 원문은 응답에 포함하지 않습니다.
- 인증 레코드 ID도 프론트에 노출하지 않습니다.
- 인증 성공 후에는 인증 코드 자체가 아니라 짧게 유효한 verification token으로 다음 단계를 진행합니다.
- verification token은 Access Token이나 Refresh Token과 다른 계정 복구 전용 토큰입니다.
- verification token은 JWT가 아니라 DB 저장형 랜덤 토큰으로 발급합니다.
- verification token 원문은 응답 시 한 번만 노출하고, 서버에는 해시와 만료/사용 상태만 저장합니다.
- 비밀번호 재설정 성공 후 자동 로그인하지 않습니다.
- 비밀번호 재설정 성공 후 해당 회원의 기존 refresh token은 모두 폐기합니다.
- 비밀번호 재설정 성공 후 현재 응답의 refresh token cookie도 만료시킵니다.

## 도메인 구조

목표 패키지 구조:

```text
domain/auth
├─ command
│  ├─ SendEmailVerificationCommand.java
│  ├─ ConfirmEmailVerificationCommand.java
│  ├─ FindLoginIdsCommand.java
│  └─ ResetPasswordCommand.java
├─ result
│  ├─ SendEmailVerificationResult.java
│  ├─ ConfirmEmailVerificationResult.java
│  ├─ FindLoginIdsResult.java
│  └─ ResetPasswordResult.java
├─ service
│  ├─ EmailVerificationService.java
│  └─ AccountRecoveryService.java
├─ support
│  ├─ mail
│  │  └─ AuthMailSender.java
│  └─ verification
│     ├─ VerificationCodeGenerator.java
│     ├─ VerificationCodeHasher.java
│     ├─ EmailVerificationPolicy.java
│     └─ EmailVerificationTokenGenerator.java
├─ entity
│  ├─ EmailVerification.java
│  ├─ EmailVerificationPurpose.java
│  └─ EmailVerificationStatus.java
└─ repository
   └─ EmailVerificationRepository.java
```

구조 판단:

- `EmailVerificationService`는 코드 발송과 확인 유스케이스 진입점입니다.
- `AccountRecoveryService`는 로그인 ID 찾기와 비밀번호 재설정 유스케이스 진입점입니다.
- SMTP 발송은 도메인 규칙이 아니므로 `AuthMailSender` 같은 경계로 감쌉니다.
- 인증 코드 생성, 해시, 만료 정책, 랜덤 token 발급은 `support/verification`에 둡니다.
- Controller는 request DTO를 command로 변환하고 result를 response DTO로 변환합니다.

## 데이터 모델

목표 테이블명은 `auth_email_verifications`입니다.

핵심 컬럼:

- `id`
- `email`
- `login_id`
- `purpose`
- `code_hash`
- `status`
- `expires_at`
- `verified_at`
- `verification_token_hash`
- `verification_token_expires_at`
- `verification_token_used_at`
- `attempt_count`
- `last_sent_at`
- `created_at`
- `updated_at`

핵심 정책:

- 인증 코드는 해시로 저장합니다.
- 같은 `email + purpose + loginId` 조합에서 새 코드를 발급하면 이전 미완료 코드는 만료 또는 폐기합니다.
- 만료된 코드는 검증할 수 없습니다.
- 검증 시도 횟수가 임계값을 넘으면 실패 처리합니다.
- 인증 완료된 레코드는 재사용하지 않습니다.

## 보안 기준

- 인증 코드는 6자리 숫자로 시작합니다.
- 인증 코드 유효 시간은 5분을 기본값으로 둡니다.
- 인증 성공 후 발급하는 verification token 유효 시간은 10분을 기본값으로 둡니다.
- verification token은 충분한 엔트로피를 가진 랜덤 문자열로 발급합니다.
- 재발송 쿨다운은 60초를 기본값으로 둡니다.
- 검증 실패 허용 횟수는 5회를 기본값으로 둡니다.
- 비밀번호, 인증 코드, verification token 원문은 로그에 남기지 않습니다.
- 메일 발송 로그에는 목적, 결과, 이메일 마스킹 값, 요청 IP 정도만 남깁니다.

가정(Assumption): 초기 rate limit은 Redis 없이 DB의 최근 발송 기록과 시각 기준으로 처리합니다.

## 설정 기준

메일 설정은 `application.yaml`에서 환경 변수로 읽습니다.

권장 환경 변수:

- `MATCHURI_MAIL_HOST`
- `MATCHURI_MAIL_PORT`
- `MATCHURI_MAIL_USERNAME`
- `MATCHURI_MAIL_PASSWORD`
- `MATCHURI_MAIL_FROM`
- `MATCHURI_EMAIL_VERIFICATION_CODE_TTL_SECONDS`
- `MATCHURI_EMAIL_VERIFICATION_TOKEN_TTL_SECONDS`
- `MATCHURI_EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS`
- `MATCHURI_EMAIL_VERIFICATION_MAX_ATTEMPTS`

저장소에는 실제 Gmail 계정이나 앱 비밀번호를 직접 남기지 않습니다.

## 리팩토링 기준

현재 구현은 후속 코드 작업에서 아래 순서로 정리합니다.

1. `SendEmailRequest`, `SendEmailResponse`를 domain service에서 제거하고 command/result로 분리합니다.
2. `sendTxtEmail` 이름을 `sendVerificationEmail`에 가까운 유스케이스 이름으로 바꿉니다.
3. `EmailVerificationType`을 `EmailVerificationPurpose`로 바꾸고 목적 값을 재정의합니다.
4. `support/vertification`을 `support/verification`으로 이동합니다.
5. 인증 코드 평문 저장을 `codeHash` 저장으로 바꿉니다.
6. 만료, 검증 시도 횟수, 상태 컬럼을 추가합니다.
7. 인증 코드 확인 API를 추가합니다.
8. 로그인 ID 찾기와 비밀번호 재설정 API를 추가합니다.
9. Swagger 문서와 `docs/api/` 문서를 함께 갱신합니다.
10. 대표 정상/실패 테스트를 추가합니다.

## 검증 기준

- `SIGNUP` 인증 코드 발송 요청은 이미 가입된 자체 로그인 이메일이면 중복 이메일 오류를 반환합니다.
- 계정 복구 목적의 인증 코드 발송 요청은 계정 존재 여부를 응답으로 드러내지 않습니다.
- 유효한 코드 확인 시 verification token이 발급됩니다.
- 만료된 코드, 틀린 코드, 시도 횟수 초과 코드는 실패합니다.
- 회원가입은 `SIGNUP` 목적의 유효한 verification token 없이는 실패합니다.
- 로그인 ID 찾기는 인증된 이메일의 자체 로그인 ID 1개만 반환합니다.
- 비밀번호 재설정은 `RESET_PASSWORD` 목적의 유효한 token과 `loginId` 매칭이 필요합니다.
- 비밀번호 재설정 후 기존 비밀번호로 로그인할 수 없습니다.
- 새 비밀번호로 로그인할 수 있습니다.
- 비밀번호 재설정 후 기존 refresh token으로 access token을 재발급할 수 없습니다.

## 확정된 계정 복구 결정

- 신규 자체 회원가입부터 이메일 인증을 필수로 둡니다.
- 한 이메일에 여러 자체 로그인 ID를 허용하지 않습니다.
- 비밀번호 재설정 성공 시 해당 회원의 기존 refresh token을 모두 폐기합니다.
- 기존 `POST /api/v1/auth/email`은 별도 호환 경로를 두지 않고 목표 계약에 맞게 직접 수정합니다.
- emailVerificationToken은 JWT가 아니라 DB 저장형 랜덤 토큰으로 발급합니다.

## 관련 문서

- [인증 이메일 검증과 계정 복구 API](../api/auth-email-verification.md)
- [인증 이메일 검증 데이터 상세 설계](../data/auth-email-verifications-schema.md)
- [보안](../backend/security.md)
- [백엔드 가이드](../backend/guide.md)
