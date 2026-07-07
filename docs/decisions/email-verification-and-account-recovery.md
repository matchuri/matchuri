# 이메일 인증과 계정 복구 결정

이 문서는 이메일 인증과 계정 복구 구현 기준만 남깁니다.
사람이 읽는 배경 설명과 제품 맥락은 GitHub Wiki에서 관리합니다.

## 결정

- 신규 자체 회원가입부터 이메일 인증을 필수로 둡니다.
- 자체 로그인 계정은 같은 이메일을 중복 사용할 수 없습니다.
- 이메일 인증 목적은 `SIGNUP`, `FIND_LOGIN_ID`, `RESET_PASSWORD`로 분리합니다.
- 인증 성공 후 다음 단계에는 인증 코드가 아니라 짧게 유효한 `emailVerificationToken`을 사용합니다.
- `emailVerificationToken`은 JWT가 아니라 DB 저장형 랜덤 토큰입니다.
- 인증 코드와 verification token 원문은 저장하지 않고 해시로 저장합니다.
- 비밀번호 재설정 성공 시 해당 회원의 기존 refresh token을 모두 폐기합니다.
- 기존 자체 로그인 계정 중 이메일이 없는 계정은 별도 이메일 보강 흐름 전까지 계정 복구 대상에서 제외합니다.

## API 원칙

- `SIGNUP` 목적의 이메일 인증 발송은 이미 가입된 자체 로그인 이메일이면 중복 이메일 오류를 반환합니다.
- `FIND_LOGIN_ID`, `RESET_PASSWORD` 목적의 발송 요청은 계정 존재 여부를 응답으로 드러내지 않습니다.
- 인증 코드 원문, 인증 레코드 ID, token hash는 응답에 포함하지 않습니다.
- 비밀번호 재설정 성공 후 자동 로그인하지 않습니다.

## 데이터 기준

목표 테이블명은 `auth_email_verifications`입니다.

핵심 컬럼:

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

## 보안 기준

- 인증 코드는 6자리 숫자로 시작합니다.
- 인증 코드 유효 시간은 5분을 기본값으로 둡니다.
- verification token 유효 시간은 10분을 기본값으로 둡니다.
- 재발송 쿨다운은 60초를 기본값으로 둡니다.
- 검증 실패 허용 횟수는 5회를 기본값으로 둡니다.
- 비밀번호, 인증 코드, verification token 원문은 로그에 남기지 않습니다.

## 검증 기준

- 유효한 코드 확인 시 verification token이 발급됩니다.
- 만료된 코드, 틀린 코드, 시도 횟수 초과 코드는 실패합니다.
- 회원가입은 `SIGNUP` 목적의 유효한 verification token 없이는 실패합니다.
- 로그인 ID 찾기는 인증된 이메일의 자체 로그인 ID 1개만 반환합니다.
- 비밀번호 재설정은 `RESET_PASSWORD` 목적의 유효한 token과 `loginId` 매칭이 필요합니다.
- 비밀번호 재설정 후 기존 비밀번호와 기존 refresh token은 사용할 수 없습니다.
