# OAuth2 Provider 확장 구조

## 문서 목적

- 현재 `Google` 중심으로 구현된 OAuth2 로그인 구조가 `Kakao`, `Naver` 추가 시 어떻게 확장되어야 하는지 기준을 정한다.
- provider별 클래스가 무분별하게 늘어나는 구조를 피하고, 2인 팀이 유지 가능한 단순한 구조를 선택한다.
- 구현 전에 어떤 책임을 공통화하고 어떤 부분만 provider별로 남길지 합의한다.

## 현재 문제 인식

현재 구현은 `GoogleOAuth2...` 이름의 클래스가 여러 계층에 퍼져 있다.

- `GoogleOAuth2AuthenticationSuccessHandler`
- `GoogleOAuth2AuthenticationFailureHandler`
- `GoogleOAuth2RedirectService`
- `GoogleOAuth2LoginService`
- `GoogleOAuth2Service`
- `GoogleOAuth2LoginResult`

이 구조는 `Google`만 있을 때는 빠르게 구현하기 쉽지만, 이후 `Kakao`, `Naver`가 추가되면 아래 문제가 생길 가능성이 높다.

- 성공 핸들러, 실패 핸들러, 결과 객체, 서비스가 provider마다 반복 생성된다.
- 실제로는 같은 흐름인데 클래스 이름만 provider별로 달라진다.
- 공통 정책 변경 시 여러 provider 클래스를 함께 수정해야 한다.
- provider 고유 책임과 OAuth2 공통 책임의 경계가 흐려진다.

## 판단 원칙

- provider 추가는 자주 일어나지 않지만, 한 번 추가될 때마다 구조 비용이 급격히 늘어나면 안 된다.
- Matchuri는 2인 팀 운영이므로 "프레임워크처럼 거대한 추상화"보다 "확장 포인트가 분명한 얇은 추상화"를 우선한다.
- 공통 흐름은 공통 객체로 묶고, provider별 차이는 "사용자 정보 해석"과 "등록 정보" 근처에만 남긴다.
- provider별 클래스를 완전히 없애는 것이 목표는 아니다.
  다만 provider마다 성공/실패 핸들러와 전체 로그인 서비스가 복제되는 구조는 피한다.

## 권장 방향

### 한 줄 요약

- `OAuth2 로그인 오케스트레이션은 공통화`
- `provider별 차이는 사용자 정보 매핑 어댑터로 제한`

## 목표 구조

### 1. 공통 흐름은 하나의 서비스로 모은다

현재 `GoogleOAuth2LoginService`가 하는 일은 사실상 provider 공통 흐름이다.

공통 흐름:

1. provider 식별
2. provider 사용자 정보 정규화
3. 기존 회원 조회 또는 신규 회원 생성
4. Refresh Token 발급
5. 교환 코드 발급
6. 성공 로그 기록

이 흐름은 provider가 바뀌어도 거의 동일하므로, 아래처럼 공통 서비스로 승격하는 방향이 적절하다.

- `OAuth2LoginService`
- `OAuth2LoginResult`

예시 역할:

```text
OAuth2LoginService
  - login(provider, oAuth2User, clientIp)
```

### 2. provider별 차이는 정규화 객체로 흡수한다

Google, Kakao, Naver는 사용자 식별 정보의 필드 모양이 다르다.
차이는 대부분 `OAuth2User attributes`를 어떻게 읽느냐에 있다.

따라서 provider별 차이는 "정규화 단계"에 가두는 것이 자연스럽다.

권장 구조:

```text
OAuth2UserInfoResolver
  - supports(provider)
  - resolve(attributes) -> OAuth2ProviderUserInfo
```

예시 구현:

- `GoogleOAuth2UserInfoResolver`
- `KakaoOAuth2UserInfoResolver`
- `NaverOAuth2UserInfoResolver`

공통 정규화 결과:

```text
OAuth2ProviderUserInfo
  - provider
  - providerUserId
  - email
  - nickname
```

이 구조의 장점:

- provider별 복잡도는 attribute 파싱 클래스 안에만 모인다.
- 공통 서비스는 provider별 JSON 구조를 몰라도 된다.
- 테스트가 쉬워진다.

### 3. 회원 조회/생성도 provider 중립적으로 바꾼다

현재 `GoogleOAuth2Service`는 이름상 Google 전용처럼 보이지만, 실제 책임은 "소셜 회원 조회 또는 생성"이다.
이 책임은 provider 공통 유스케이스에 가깝다.

권장 이름:

- `SocialLoginMemberService`
- 또는 `OAuth2MemberService`

예시 역할:

```text
OAuth2MemberService
  - findOrCreateMember(OAuth2ProviderUserInfo userInfo)
```

이 서비스는 아래 규칙을 공통으로 관리한다.

- `providerUserId` 필수 여부 확인
- `provider + providerUserId` 기준 기존 회원 조회
- 없으면 신규 소셜 회원 생성
- 비활성 회원 차단

이렇게 하면 `GoogleOAuth2Service`, `KakaoOAuth2Service`, `NaverOAuth2Service`처럼 서비스가 복제되지 않는다.

### 4. 성공/실패 핸들러도 공통화한다

현재 성공/실패 핸들러는 이름상 `Google` 전용이지만, 대부분 동작은 공통이다.

공통 동작:

- authorization request 쿠키 정리
- refresh token 쿠키 설정 또는 제거
- 성공/실패 redirect URL 생성
- 실패 코드 해석

권장 구조:

- `OAuth2AuthenticationSuccessHandler`
- `OAuth2AuthenticationFailureHandler`
- `OAuth2RedirectService`

핸들러는 provider를 직접 하드코딩하지 않고, Spring Security 인증 객체에서 registration id를 읽어 `SocialProviderType`으로 변환해 사용한다.

예시:

```text
OAuth2AuthenticationToken.getAuthorizedClientRegistrationId()
```

이렇게 하면 `provider=google` 하드코딩이 제거되고, redirect URL에도 실제 provider 값을 실을 수 있다.

### 5. provider별 클래스를 완전히 없애지는 않는다

아래 클래스는 provider별로 남아도 괜찮다.

- `GoogleOAuth2UserInfoResolver`
- `KakaoOAuth2UserInfoResolver`
- `NaverOAuth2UserInfoResolver`

이 클래스들은 provider별 속성 구조 차이를 흡수하는 "작은 어댑터"이기 때문이다.
반면 아래 클래스는 provider별로 복제하지 않는 것을 권장한다.

- 성공 핸들러
- 실패 핸들러
- 로그인 결과 객체
- 토큰 발급 오케스트레이션 서비스
- 리다이렉트 서비스

## 제안 패키지 방향

현재 구조를 크게 흔들지 않으면서 아래 정도로 정리할 수 있다.

```text
domain/auth/service
  - AuthService
  - OAuth2LoginService
  - OAuth2LoginResult
  - OAuth2MemberService
  - OAuth2ProviderUserInfo
  - OAuth2UserInfoResolver
  - GoogleOAuth2UserInfoResolver
  - KakaoOAuth2UserInfoResolver
  - NaverOAuth2UserInfoResolver
  - SessionTokenService
  - JwtTokenProvider

global/security
  - OAuth2AuthenticationSuccessHandler
  - OAuth2AuthenticationFailureHandler
  - OAuth2RedirectService
  - MatchuriOAuth2AuthorizationRequestRepository
```

현재 구현 기준:

- authorization request 저장소는 `MatchuriOAuth2AuthorizationRequestRepository`를 사용합니다.
- 내부 저장은 서버 세션 기반이며, 과거 cookie-backed 구현은 제거되었습니다.

## 권장 객체 책임

### `OAuth2AuthenticationSuccessHandler`

- 인증 객체에서 provider 식별
- `OAuth2LoginService` 호출
- refresh token cookie 처리
- authorization request 상태 정리
- 성공/실패 리다이렉트

### `OAuth2LoginService`

- provider별 user info resolver 선택
- 정규화된 사용자 정보 생성
- 회원 조회/생성
- 토큰/교환 코드 발급

### `OAuth2UserInfoResolver`

- provider별 attribute 구조를 `OAuth2ProviderUserInfo`로 변환

### `OAuth2MemberService`

- 소셜 회원 조회/생성 규칙 관리

### `OAuth2RedirectService`

- provider, errorCode, exchangeCode를 기반으로 프론트 리다이렉트 URL 생성

## 왜 이 구조가 더 객체지향적인가

이 구조는 "provider 이름을 클래스 이름에 반복하는 것"보다 "변하는 이유" 기준으로 객체를 나눈다.

- `OAuth2LoginService`가 바뀌는 이유:
  OAuth2 로그인 공통 흐름이 바뀔 때
- `OAuth2UserInfoResolver` 구현체가 바뀌는 이유:
  특정 provider의 사용자 정보 구조가 바뀔 때
- `OAuth2RedirectService`가 바뀌는 이유:
  프론트 복귀 계약이 바뀔 때

즉, 클래스가 "provider 이름"이 아니라 "책임"을 중심으로 분리된다.
이 점에서 현재 구조보다 변경 이유가 더 명확하다.

## 과한 추상화를 피하기 위한 제한

아래 수준까지만 추상화하는 것을 권장한다.

- resolver 인터페이스 1개
- 공통 로그인 서비스 1개
- 공통 핸들러 2개
- 공통 결과 객체 1개

아래 수준까지는 지금 단계에서 과하다고 본다.

- provider별 전략 객체가 로그인, 리다이렉트, 회원 생성, 토큰 정책까지 전부 소유하는 구조
- 별도 팩토리, 레지스트리, 디렉터리 계층을 여러 겹 두는 구조
- 외부 provider 연동을 플러그인 시스템처럼 만드는 구조

현재 provider 수는 3개 정도가 예상되므로, "작은 전략 + 공통 오케스트레이션"이면 충분하다.

## 단계별 리팩토링 전략

### 1단계. 이름과 책임 일반화

- `GoogleOAuth2LoginResult` -> `OAuth2LoginResult`
- `GoogleOAuth2LoginService` -> `OAuth2LoginService`
- `GoogleOAuth2Service` -> `OAuth2MemberService`
- `GoogleOAuth2RedirectService` -> `OAuth2RedirectService`
- 성공/실패 핸들러 이름 일반화

목표:

- provider별 복제 구조를 멈춘다.

### 2단계. provider 식별을 인증 객체에서 읽도록 변경

- `google` 하드코딩 제거
- registration id -> `SocialProviderType` 매핑 추가

목표:

- 성공/실패 리다이렉트와 로그에서 실제 provider를 공통적으로 다룬다.

### 3단계. 사용자 정보 정규화 도입

- `OAuth2ProviderUserInfo`
- `OAuth2UserInfoResolver`
- `Google/Kakao/Naver` resolver 구현

목표:

- provider 추가 시 변경 범위를 attribute 파싱 계층으로 제한한다.

### 4단계. Kakao/Naver 등록

- Spring Security registration 추가
- resolver 구현 추가
- 통합 테스트 추가

목표:

- provider 추가가 기존 공통 흐름 변경 없이 가능함을 확인한다.

## 테스트 전략

- 공통 성공 핸들러 테스트:
  provider별 registration id가 올바르게 처리되는지 검증
- resolver 테스트:
  Google/Kakao/Naver attribute 샘플을 정규화 객체로 변환하는지 검증
- 회원 서비스 테스트:
  기존 회원 조회, 신규 생성, 비활성 회원 차단 검증
- redirect 서비스 테스트:
  provider별 성공/실패 URL 파라미터가 일관되게 생성되는지 검증

## 현재 권장 결론

- 현재 구조는 `Google` 하나만 있을 때는 빠르게 동작하지만, `Kakao`, `Naver`까지 확장하기에는 provider 이름이 너무 넓은 범위에 퍼져 있다.
- provider별 클래스를 일부 두는 것은 괜찮지만, 그것은 "user info resolver" 정도로 제한하는 것이 적절하다.
- 성공/실패 핸들러, 로그인 서비스, 결과 객체, 리다이렉트 서비스는 provider 공통 구조로 일반화하는 방향을 권장한다.
- 즉, 다음 단계 리팩토링은 "provider별 서비스 복제"가 아니라 "공통 오케스트레이션 + provider별 정규화 어댑터"를 목표로 한다.
