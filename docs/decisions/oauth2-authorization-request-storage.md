# OAuth2 Authorization Request 저장 구조 결정

이 문서는 OAuth2 authorization request 저장 방식의 현재 구현 기준만 남깁니다.
사람이 읽는 장애 배경과 설계 이야기는 GitHub Wiki에서 관리합니다.

## 결정

- OAuth2 시작부터 callback 사이의 임시 상태는 서버 세션에 저장합니다.
- 브라우저에는 큰 커스텀 authorization request 쿠키를 저장하지 않습니다.
- 서비스 인증 구조는 여전히 `access token + refresh token cookie` 기반입니다.
- OAuth2 handshake 구간만 선택적으로 stateful하게 운영합니다.

## 배경 요약

과거에는 `OAuth2AuthorizationRequest` 전체를 Base64 직렬화해 커스텀 쿠키에 저장했습니다.
운영 환경에서 이 쿠키와 redirect 헤더가 커지면서 Nginx가 upstream response header를 읽지 못했고, Google OAuth2 시작 요청이 `502 Bad Gateway`로 실패했습니다.

## 현재 구조

- `GET /api/v1/auth/oauth2/google`로 OAuth2 흐름을 시작합니다.
- Spring Security OAuth2 Client가 authorization request를 생성합니다.
- 생성된 request는 서버 세션에 저장합니다.
- callback에서 세션의 request를 조회해 검증합니다.
- 성공/실패 처리 후 임시 상태를 정리합니다.

## 장점

- 큰 `Set-Cookie` 헤더를 제거합니다.
- OAuth2 callback 검증용 내부 상태를 브라우저가 통째로 운반하지 않습니다.
- 단일 서버 운영 기준에서 구현과 운영 복잡도가 낮습니다.

## 주의점

- 다중 인스턴스 운영 시 sticky session 또는 shared session store가 필요할 수 있습니다.
- 서버 재시작 중 OAuth2 중간 상태가 유실될 수 있습니다.
- 이 결정은 OAuth2 handshake에 한정되며, API 인증 전체를 세션 기반으로 바꾸는 결정이 아닙니다.
