# 프론트엔드 가이드

## 목적

UI 구조, 라우팅 규칙, 스타일링 기준, 프론트엔드 구현 원칙을 정리합니다.

## 현재 상태

- 프레임워크: Next.js 16
- 언어: TypeScript
- 애플리케이션 위치: `frontend/`

## 로컬 로그인 CAPTCHA

- `app/login/layout.tsx`는 공급자 중립적인 `CaptchaProvider`만 로그인 라우트에 적용합니다.
- `features/auth/infrastructure/captcha/CaptchaContext.tsx`가 준비 상태, 오류 코드, 목적별 토큰 발급이라는 공통 어댑터 계약을 제공합니다.
- `features/auth/infrastructure/captcha/useCaptchaChallenge.ts`는 공급자 오류를 공통 사용자 메시지로 변환합니다.
- 현재 구현체인 Google reCAPTCHA v3는 `features/auth/infrastructure/captcha/google/GoogleRecaptchaProvider.tsx`에 격리합니다. `next-recaptcha-v3`를 다른 로그인 코드에서 직접 import하지 않습니다.
- `CaptchaProvider.tsx`는 실제 구현체를 선택하는 composition root입니다. 공급자를 바꿀 때 페이지와 `useLogin` 대신 이 경계와 공급자 어댑터를 교체합니다.
- `features/auth/application/hooks/useLogin.ts`는 `CaptchaPurpose.LOGIN`으로 공통 훅을 호출하고 로그인 입력, CAPTCHA 결과, API 요청과 오류 우선순위를 하나의 흐름으로 조정합니다.
- 로그인 페이지는 `useLogin`이 반환한 단일 상태와 `submit()`만 사용합니다.
- 발급 토큰은 기존 `login usecase -> authApi` 흐름을 통해 공급자 중립 필드인 `captchaToken`으로 전달합니다.
- 현재 Google 공개 site key는 `NEXT_PUBLIC_RECAPTCHA_SITE_KEY`로 주입합니다. backend secret key를 frontend 환경에 두지 않습니다.
- OAuth2 로그인은 이 검증 흐름의 대상이 아닙니다.

## 다음에 채울 내용

- 라우트 맵
- 상태 관리 방식
- API 연동 패턴
- 디자인 시스템 규칙
- 접근성 체크리스트
