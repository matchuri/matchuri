# 데이터 모델

데이터 구조의 단일 기준은 `backend/src/main/java/matchuri/backend/domain/**/entity`의 JPA 매핑입니다. 테이블·컬럼·인덱스·연관관계를 Markdown에 다시 복사하지 않습니다.

## 기준과 검증

| 대상 | 기준 |
| --- | --- |
| 테이블과 컬럼 | JPA Entity, `@Table`, `@Column` |
| FK와 연관관계 | JPA association, `@JoinColumn` |
| unique와 index | `@Table`의 constraint/index 선언 |
| 실제 매핑 가능 여부 | H2 `ddl-auto: create-drop`를 사용하는 backend 테스트 |
| 명명·enum·연관관계 규칙 | `backend/scripts/audit_jpa_schema.py` |
| 구조만으로 알 수 없는 판단 | [데이터 정책](./policies.md) |

검증 명령은 backend 저장소에서 실행합니다.

```powershell
python scripts/audit_jpa_schema.py --root . --strict
./gradlew test --quiet
```

CI는 두 검증을 모두 실행합니다. 별도의 generated schema 파일은 저장하지 않습니다.

## 변경 규칙

- 구조가 바뀌면 엔티티와 테스트만 수정합니다.
- 보존 기간, 만료, 삭제, 이력, 개인정보처럼 코드만으로 의도를 알기 어려운 판단이 바뀌면 [데이터 정책](./policies.md)도 수정합니다.
- 정확한 운영 DB 구조를 확인해야 하면 배포 대상 DB의 schema 또는 migration 결과를 확인합니다.
- 문서가 엔티티의 필드 목록을 다시 나열하기 시작하면 중복으로 보고 제거합니다.
