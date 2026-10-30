# 메뉴 시드 추천 커버리지

`MenuSeedCoverageAudit`는 `seed/reference-data.json`을 읽고 실제 회원 개인 추천 알고리즘 `v1.3`으로 후보 부족을 검사합니다. 점수 계산을 별도로 복제하지 않으며, 운영 DB가 아닌 저장소의 시드를 검사합니다. 추천 점수의 의미는 [추천 점수 계약](./recommendation-scoring.md)을 봅니다.

## 실행

`JAVA_HOME`이 Java 21을 가리키는 환경에서 `app/backend`를 작업 디렉터리로 실행합니다.

```powershell
.\gradlew.bat auditMenuSeedCoverage --quiet
.\gradlew.bat auditMenuSeedCoverage --args="--strict" --quiet
.\gradlew.bat auditMenuSeedCoverage --args="--output build/reports/custom.json" --quiet
```

- 기본 JSON 보고서는 `app/backend/build/reports/menu-seed-coverage.json`입니다. `--output` 상대 경로는 `app/backend`를 기준으로 해석합니다.
- `--seed <path>`와 `--fixtures <path>`로 입력 파일을 교체해 시드·fixture 변경안을 검사할 수 있습니다.
- 일반 실행은 부족한 조합을 보고하고 성공합니다. `--strict`는 지원 대상 프로필이 아래 기준을 충족하지 못하면 실패합니다.
- 시드 보강 전에는 엄격 검사의 실패가 예상됩니다. 현재 `check`·`test`에 연결하지 않으며, 시드 보강과 실제 API 통합 검증을 맞춘 뒤 CI 필수 검사로 적용합니다.

## 프로필과 판정 기준

- 기본 프로필은 시드에 정의된 모든 `FLAVOR` × `COOKING_METHOD`의 단일 선택 조합을 자동으로 생성합니다. 추가 취향 조합은 `src/test/resources/seed/recommendation-coverage-fixtures.json`의 `profiles`, 제약별 진단은 `constraintScenarios`, 미지원 프로필과 필수 사유는 `unsupportedProfiles`에서 관리합니다.
- 지원 대상의 기준은 선택 이력과 제외 제약이 없을 때 100점 메뉴가 6개 이상이고, 첫 추천 3개를 `SKIP`한 뒤에도 100점 메뉴가 3개 이상 남는 것입니다.
- 제한 재료·비선호 메뉴가 있는 추가 프로필은 진단만 수행하며 엄격 검사 통과 여부에 포함하지 않습니다. 후보 부족을 해결하기 위해 제한 재료나 비선호 제외를 완화하지 않습니다.
- 지원하지 않는 프로필은 사유를 보고합니다. 모든 취향·제약 조합에서 충분한 후보가 나온다고 보장하지 않습니다.

## 보고서와 변경 시 확인

보고서는 프로필별 후보 수와 메뉴 코드, 기준 미달 수량, `SKIP` 이후 후보, 미태깅 메뉴, 희소 태그, 미지원 사유를 제공합니다. 실행 결과의 수량은 보고서를 기준으로 확인합니다.

`backend-app/src/main/resources/seed/reference-data.json`의 메뉴 코드·태그·재료를 변경하면 이 검사를 다시 실행합니다. 검사기는 시드 순서에 따라 임시 ID를 부여하고 코드·태그·재료 관계를 복원해 실제 알고리즘에 전달합니다. 동점의 ID 정렬은 임시 ID를 따르므로 운영 DB의 메뉴 순서와 동일하다고 보장하지 않습니다.

기계적인 검사 기준은 `src/test/java/matchuri/backend/application/seed/coverage/MenuSeedCoverageAudit.java`와 fixture를 기준으로 유지합니다. 이 검사는 실제 API에서의 카테고리 조회·후보 저장을 검증하는 통합 테스트와 함께 사용합니다.
