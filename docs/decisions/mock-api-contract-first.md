# Mock API 계약 우선 개발 기준

이 문서는 Mock API를 사용할 때 지켜야 하는 구현 기준만 남깁니다.
사람이 읽는 개발 방식 설명은 GitHub Wiki에서 관리합니다.

## 목적

아직 비즈니스 로직이 구현되지 않은 API를 먼저 노출해 프론트엔드 화면 흐름과 Swagger/OpenAPI 계약 검토를 병렬로 진행합니다.

Mock API는 실제 도메인 처리를 대신하지 않습니다.

## 원칙

- Mock API도 실제 API 경로를 사용합니다.
- request DTO와 response DTO는 실제 구현 전환을 전제로 작성합니다.
- 기본 validation은 수행합니다.
- Swagger에는 Mock API 상태를 명시합니다.
- 운영 환경에서 장기 사용하지 않습니다.

## 구현 기준

- Controller에서 service를 호출하지 않고 response DTO의 mock factory를 반환할 수 있습니다.
- mock factory는 `mockActive`, `mockOpen`, `mockFinalized`처럼 화면 상태가 드러나는 이름을 사용합니다.
- 긴 fixture는 Controller 본문에 직접 쓰지 않습니다.
- Swagger 문서 전용 DTO는 `dto/docs`에 둡니다.

## 실제 구현 전환 기준

전환 시 확인할 항목:

- request DTO가 service command로 변환됩니다.
- response DTO가 service result에서 생성됩니다.
- Controller에서 mock factory 호출이 제거됩니다.
- Swagger의 Mock API 문구가 실제 구현 상태에 맞게 갱신됩니다.
- 대표 성공/실패 테스트가 추가됩니다.
- API 상태표의 `mock`/`real` 상태가 갱신됩니다.

## 상태 기준

- `mock`: Controller가 response DTO mock factory를 반환합니다.
- `real`: Controller가 service를 호출하고 실제 비즈니스 로직을 수행합니다.
- `blocked`: API 계약이나 도메인 판단이 아직 확정되지 않았습니다.
