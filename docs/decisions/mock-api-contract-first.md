# Mock API 계약 우선 개발 가이드

이 문서는 아직 비즈니스 로직이 구현되지 않은 API를 먼저 노출해 프론트엔드 개발과 Swagger/OpenAPI 계약 검토를 병렬로 진행하기 위한 기준입니다.

Mock API의 목적은 실제 도메인 처리를 대신하는 것이 아니라, 요청/응답 계약을 먼저 고정하고 화면 개발과 API 명세 검토를 가능하게 만드는 것입니다.

## 목표

- 요청값에 대한 기본적인 validation을 수행합니다.
- 프론트엔드가 화면 흐름을 붙일 수 있을 만큼 그럴듯한 mock 응답을 반환합니다.
- Swagger UI에는 실제 API와 같은 수준으로 상세 명세를 작성하되, 해당 API가 mock 응답 단계임을 명시합니다.
- 실제 비즈니스 로직 구현 시 URL, request DTO, response DTO, Swagger 계약을 크게 바꾸지 않도록 합니다.

## 비목표

- 실제 추천, 투표, 권한, 상태 전이 로직을 구현하지 않습니다.
- DB 영속성이나 도메인 무결성을 보장하지 않습니다.
- Mock 응답을 운영 환경에서 장기 사용하지 않습니다.
- 프론트엔드 전용 임시 API 경로를 만들지 않습니다. 실제 API 경로를 기준으로 작성합니다.

## 기본 방식

Mock API는 Controller에서 service를 호출하지 않고 response DTO의 mock factory를 사용해 응답을 반환합니다.

```java
@RestController
@RequestMapping("/api/v1/groups")
public class GroupController implements GroupApi {

    @PostMapping
    public ApiResponse<CreateGroupResponse> createGroup(
            @Valid @RequestBody CreateGroupRequest request
    ) {
        return ApiResponse.success(CreateGroupResponse.mockActive());
    }
}
```

응답 DTO에는 mock 전용 static factory method를 둡니다.

```java
public record CreateGroupResponse(
        Long groupId,
        String status
) {
    public static CreateGroupResponse mockActive() {
        return new CreateGroupResponse(3001L, "ACTIVE");
    }
}
```

`mock constructor`보다 static factory를 사용합니다.

- `mockActive`, `mockOpen`, `mockFinalized`처럼 화면 상태가 드러나는 이름을 사용합니다.
- 생성자는 실제 DTO 생성 규칙을 유지하고, mock 의도는 factory 이름으로 표현합니다.
- mock 데이터가 길어지면 Controller 본문이 아니라 response DTO 또는 별도 mock fixture helper로 분리합니다.

## 패키지 기준

API 패키지 구조는 실제 구현과 동일하게 둡니다.

```text
api/<domain>
├─ <Domain>Api.java
├─ <Domain>Controller.java
├─ dto
│  ├─ request
│  ├─ response
│  └─ docs
└─ mapper
```

- `XXXApi.java`: Swagger/OpenAPI 명세 인터페이스입니다.
- `XXXController.java`: 실제 URL과 HTTP method를 노출합니다. Mock 단계에서는 service 호출 없이 response DTO mock factory를 반환할 수 있습니다.
- `dto/request`: 실제 요청 DTO입니다. Mock 단계에서도 `@Valid` 검증 기준을 넣습니다.
- `dto/response`: 실제 런타임 응답 payload DTO입니다. 필요한 경우 mock factory를 포함합니다.
- `dto/docs`: Swagger envelope, 문서 전용 schema 표현에 사용합니다.
- `mapper`: 실제 service 연동 전에는 만들지 않아도 됩니다. 실제 구현으로 전환할 때 필요하면 추가합니다.

## Validation 기준

Mock API도 기본 요청 검증은 수행합니다.

- request body는 `@Valid @RequestBody`를 사용합니다.
- 필수값, 문자열 길이, enum, 숫자 범위는 request DTO validation으로 표현합니다.
- path variable과 query parameter의 단순 형식 검증은 Controller에서 처리할 수 있습니다.
- DB 조회가 필요한 검증은 mock 단계에서 생략할 수 있습니다.

예시:

```java
public record CreateGroupRequest(
        @NotBlank
        @Size(max = 100)
        String name,

        @DecimalMin("-90.0")
        @DecimalMax("90.0")
        BigDecimal latitude,

        @DecimalMin("-180.0")
        @DecimalMax("180.0")
        BigDecimal longitude
) {
}
```

Mock 단계에서 생략 가능한 검증:

- 존재하지 않는 `groupId` 조회
- 이미 종료된 그룹 상태 확인
- 현재 회원의 그룹 참여 여부 확인
- 중복 투표 여부 확인
- 추천 후보 생성 알고리즘 검증

다만 Swagger 명세에는 위 실패 케이스를 실제 API 기준으로 작성할 수 있습니다.

## Mock 응답 기준

Mock 응답은 프론트엔드 화면 흐름을 검증할 수 있을 만큼 실제처럼 작성합니다.

- 공통 envelope는 항상 `ApiResponse.success(...)`를 사용합니다.
- 목록이나 페이지 응답은 기존 `PageResponse.mock(...)`을 사용할 수 있습니다.
- 그룹 의사결정 흐름은 후보 3개, 참여자, 투표 상태, 최종 결과처럼 화면에 필요한 상태를 포함합니다.
- 추천 사유는 제품 방향에 맞게 설명 가능한 문장으로 둡니다.
- `LocalDateTime.now()`는 반복 테스트에서 응답이 계속 바뀌므로, 가능하면 고정값을 사용합니다.

예시:

```java
public static GroupRecommendationSessionResponse mockOpen() {
    return new GroupRecommendationSessionResponse(
            5001L,
            "OPEN",
            List.of(
                    GroupRecommendationCandidateResponse.mockBibimbap(),
                    GroupRecommendationCandidateResponse.mockPorkCutlet(),
                    GroupRecommendationCandidateResponse.mockRiceNoodle()
            )
    );
}
```

## Swagger 작성 기준

`XXXApi.java`에는 실제 API 명세 수준으로 상세히 작성합니다.
Mock 단계임을 숨기지 않고 description에 명시합니다.

```java
@Operation(
        summary = "그룹 생성",
        description = """
                그룹 방을 생성합니다.

                Mock API 상태:
                - 현재 응답은 비즈니스 로직과 DB 저장을 거치지 않는 더미 응답입니다.
                - request body validation은 수행합니다.
                - 실제 구현 시 동일한 URL, request DTO, response DTO를 유지하는 것을 목표로 합니다.

                실제 API 기준:
                - 인증된 회원만 호출할 수 있습니다.
                - 생성자는 자동으로 그룹 멤버에 포함됩니다.
                - 성공 시 생성된 그룹 ID와 상태를 반환합니다.
                """
)
```

Swagger에는 아래 내용을 포함합니다.

- summary
- 상세 description
- 인증 필요 여부
- request body 필드 의미와 제약
- path/query parameter 의미와 제약
- 성공 응답 schema와 example
- 대표 실패 응답 example
- Mock API 상태 표시

문서 전용 envelope schema가 필요하면 `dto/docs`에 둡니다.
실제 런타임 response DTO와 Swagger envelope DTO를 섞지 않습니다.

## 실제 구현 전환 기준

Mock API를 실제 API로 전환할 때는 Controller 메서드 단위로 진행합니다.

Mock 단계:

```java
return ApiResponse.success(CreateGroupResponse.mockActive());
```

실제 구현 단계:

```java
var command = groupMapper.toCreateGroupCommand(request);
var result = groupService.createGroup(command);
var response = groupMapper.toCreateGroupResponse(result);

return ApiResponse.success(response);
```

전환 시 확인할 항목:

- request DTO가 실제 service command로 변환되는가
- response DTO가 result에서 생성되는가
- mock factory 호출이 Controller에서 제거되었는가
- Swagger의 "Mock API 상태" 문구를 실제 구현 상태에 맞게 갱신했는가
- 대표 성공/실패 테스트를 추가했는가
- `docs/api/api-status.md`의 mock/real 상태표를 갱신했는가
- 진행 중 실행 계획이 있다면 해당 실행 계획의 상태표도 갱신했는가

## 진행 상태 관리

Mock API가 많아지면 어떤 API가 mock인지 코드만 보고 추적하기 어렵습니다.
전체 API 상태는 `docs/api/api-status.md`에서 관리합니다.
진행 중인 기능의 세부 작업 이력은 필요할 때 내부 실행 계획 기록에 별도 상태표로 둡니다.

예시:

```md
| API | Mock 응답 | Validation | Swagger | 실제 구현 | 상태 |
| --- | --- | --- | --- | --- | --- |
| POST /api/v1/groups | 완료 | 완료 | 완료 | 미완료 | mock |
| GET /api/v1/groups/{groupId} | 완료 | 완료 | 완료 | 완료 | real |
| POST /api/v1/groups/{groupId}/recommendations | 완료 | 완료 | 완료 | 미완료 | mock |
```

상태 기준:

- `mock`: Controller가 response DTO mock factory를 반환합니다.
- `real`: Controller가 service를 호출하고 실제 비즈니스 로직을 수행합니다.
- `blocked`: API 계약이나 도메인 판단이 아직 확정되지 않았습니다.

## 코드 작성 규칙

- Mock API도 실제 API 경로를 사용합니다.
- Response DTO mock factory 이름은 화면 상태나 시나리오가 드러나게 작성합니다.
- Controller 본문에 긴 fixture를 직접 작성하지 않습니다.
- `Result` 객체를 mock으로 직접 생성하지 않습니다. Mock 단계에서는 response DTO를 바로 반환합니다.
- 실제 구현 후에도 Swagger 문서용 DTO는 `dto/docs`에 유지합니다.
- mock factory가 실제 구현에서 계속 필요하지 않으면 전환 완료 후 제거할 수 있습니다.

## 예외

아래 경우에는 별도 helper를 둘 수 있습니다.

- 여러 response DTO가 같은 후보 메뉴 fixture를 공유하는 경우
- 그룹 추천처럼 후보, 투표, 멤버 상태 fixture가 길어지는 경우
- Swagger example과 runtime mock 응답을 같은 값으로 맞추고 싶은 경우

이때 helper는 `api/<domain>/dto/response` 안의 DTO 책임을 넘어 너무 커지지 않게 유지합니다.
도메인 규칙이나 실제 알고리즘은 helper에 넣지 않습니다.

## 검증 방법

Mock API 추가 후 기본 검증은 아래를 따릅니다.

- `./gradlew test`
- Swagger UI에서 해당 API가 보이는지 확인
- 성공 example과 실제 mock 응답의 필드가 크게 어긋나지 않는지 확인
- request DTO validation이 대표 잘못된 입력을 거절하는지 확인
- 프론트엔드가 mock 응답으로 화면 흐름을 진행할 수 있는지 확인

문서만 작성한 경우에는 관련 API 문서, Swagger description, 실행 계획 상태표가 서로 어긋나지 않는지 직접 점검합니다.
