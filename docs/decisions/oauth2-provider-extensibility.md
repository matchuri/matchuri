# OAuth2 Provider 확장 구조 결정

이 문서는 OAuth2 provider 확장 시 유지해야 하는 구현 기준만 남깁니다.
사람이 읽는 설계 배경은 GitHub Wiki에서 관리합니다.

## 결정

- OAuth2 로그인 오케스트레이션은 공통화합니다.
- provider별 차이는 사용자 정보 매핑 어댑터로 제한합니다.
- 성공/실패 핸들러, 로그인 결과 객체, 토큰 발급 오케스트레이션 서비스, 리다이렉트 서비스는 provider별로 복제하지 않습니다.
- provider별 클래스로 남겨도 되는 것은 user info resolver 정도입니다.

## 권장 구조

공통 객체:

- `OAuth2LoginService`
- `OAuth2LoginResult`
- `OAuth2MemberService`
- `OAuth2ProviderUserInfo`
- `OAuth2UserInfoResolver`
- `OAuth2AuthenticationSuccessHandler`
- `OAuth2AuthenticationFailureHandler`
- `OAuth2RedirectService`

provider별 객체:

- `GoogleOAuth2UserInfoResolver`
- `KakaoOAuth2UserInfoResolver`
- `NaverOAuth2UserInfoResolver`

## 책임 기준

- `OAuth2LoginService`: provider별 resolver 선택, 회원 조회/생성, 토큰/교환 코드 발급
- `OAuth2UserInfoResolver`: provider attribute를 공통 사용자 정보로 정규화
- `OAuth2MemberService`: 소셜 회원 조회/생성 규칙 관리
- `OAuth2RedirectService`: 성공/실패 프론트 복귀 URL 생성

## 제한

지금 단계에서는 아래 수준의 과한 추상화를 피합니다.

- provider별 전략 객체가 로그인, 리다이렉트, 회원 생성, 토큰 정책까지 전부 소유하는 구조
- 별도 팩토리, 레지스트리, 디렉터리 계층을 여러 겹 두는 구조
- 외부 provider 연동을 플러그인 시스템처럼 만드는 구조

## 테스트 기준

- provider별 registration id 처리
- Google/Kakao/Naver attribute 정규화
- 기존 회원 조회, 신규 생성, 비활성 회원 차단
- provider별 성공/실패 redirect URL 생성
