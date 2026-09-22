# 회원 탈퇴 및 물리 삭제 정책

## 설명

- 사용자가 회원탈퇴를 요청하면 계정을 즉시 물리 삭제하지 않고 `DELETED` 상태로 전환한다.
- 탈퇴 요청 시각부터 3일은 복구 가능 기간이 아니라 물리 삭제 대기 기간이다.
- 현재 탈퇴 철회 기능은 제공하지 않으며, 복구 정책은 팀 합의 후 별도 API 요구사항으로 정의한다.
- 사용자가 방장인 그룹도 함께 `DELETED` 처리한다.
- 삭제 예정 시각이 지나면 스케줄러가 회원 행을 한 번 삭제하고 DB FK의 `ON DELETE CASCADE`로 소유 그룹 및 회원을 참조하는 데이터를 연쇄 물리 삭제한다.
- 별도의 삭제 요청 테이블이나 탈퇴 철회 토큰은 사용하지 않는다.

## 수용 기준

- 로그인한 사용자는 `DELETE /api/v1/members/me`로 회원탈퇴를 요청할 수 있다.
- 탈퇴 응답에는 회원 `id`와 `DELETED` 상태만 포함된다.
- `deletedAt`, `purgeAt`은 서버 내부의 삭제 처리 및 스케줄링 정보이며 API 응답에 노출하지 않는다.
- 탈퇴 즉시 해당 회원의 refresh token과 미사용 OAuth2 교환 코드는 폐기된다.
- 탈퇴 회원의 기존 access token은 보호 API에서 `MEMBER_INACTIVE_MEMBER`로 거절된다.
- 탈퇴 회원이 올바른 로컬 자격 증명으로 로그인해도 `MEMBER_INACTIVE_MEMBER` (`403`)가 반환된다.
- 비밀번호가 틀리면 계정 상태와 관계없이 `AUTH_LOGIN_FAILED`가 반환된다.
- 탈퇴 회원이 OAuth2 인증에 성공해도 서비스 로그인은 `MEMBER_INACTIVE_MEMBER`로 거절된다.
- 로그인 body나 OAuth2 로그인 query에는 탈퇴 철회 의도를 나타내는 필드가 없다.
- 탈퇴 회원과 방장 그룹은 물리 삭제 전까지 `DELETED` 상태를 유지하며 복구되지 않는다.
- 스케줄러는 `status=DELETED`이고 `purgeAt`이 지난 회원을 최대 100명씩 처리한다.
- 스케줄러의 애플리케이션 삭제 명령은 회원 행에 대한 단일 `DELETE`이며, 자식 엔티티를 조회하거나 테이블별 native SQL을 실행하지 않는다.
- 물리 삭제 후 같은 로그인 ID 또는 소셜 provider 식별자는 신규 회원 생성에 다시 사용할 수 있다.

## 엣지케이스

- 탈퇴 회원이 올바르지 않은 비밀번호로 로그인한다.
- 탈퇴 직전 여러 기기에서 발급된 access token과 refresh token이 존재한다.
- `purgeAt`은 지났지만 스케줄러가 아직 회원을 물리 삭제하지 않았다.
- 방장 그룹이 탈퇴 전에 `CLOSED` 상태였다.
- 탈퇴 회원이 다른 사용자의 그룹에 일반 멤버로 참여하고 있다.
- OAuth2 provider 인증 도중 사용자가 동의를 취소한다.
- 회원 연관 데이터의 cascade FK 제약이 잘못 구성되어 물리 삭제 트랜잭션이 롤백된다.
- 복구 정책이 확정되기 전에 클라이언트가 임의로 복구 요청 필드를 전송한다.

## 참고

- 관련 API: `DELETE /api/v1/members/me`, `POST /api/v1/auth/login`, `GET /api/v1/auth/oauth2/{provider}`
- 관련 데이터: `members`, `group_rooms`, 인증 세션·이메일 인증, 회원 취향/위치/약관, 개인 추천, 그룹 멤버십/추천/투표/초대
- 삭제 구현: Hibernate `@OnDelete(CASCADE)`로 FK 삭제 정책을 선언하고, 선택 후보의 순환 nullable FK는 `@OnDelete(SET_NULL)`로 해소한다.
- 삭제 대기 기간: 탈퇴 요청 시각부터 3일
- 물리 삭제 실행 주기: 기본 매시간 정각, `MATCHURI_MEMBER_DELETION_PURGE_CRON`으로 조정 가능
- 프론트 처리: 복구 UI나 복구 재요청을 제공하지 않고 `MEMBER_INACTIVE_MEMBER`를 탈퇴 계정의 종료 상태로 처리한다.
- 미정 사항: 탈퇴 철회 제공 여부와 인증 방식, 물리 삭제 완료 후 동일 식별자 재가입 안내 문구, 방장 그룹 참가자에 대한 사전 알림 UI
