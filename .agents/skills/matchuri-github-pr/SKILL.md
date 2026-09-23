---
name: matchuri-github-pr
description: Matchuri의 root, backend, frontend 저장소에서 사용자가 명시적으로 요청한 GitHub PR을 저장소별 템플릿에 맞춰 빠르게 생성하거나 수정한다.
---

# Matchuri GitHub PR

PR 생성은 구현이나 검증을 다시 수행하는 단계가 아니다.
마지막 코드 변경 이후 확보한 검증 결과를 재사용한다.

## 저장소

root, app/backend/, app/frontend/는 각각 독립된 Git 저장소다.
항상 PR 대상 코드가 속한 저장소에서 Git 명령을 수행한다.

## PR 작성

1. 대상 저장소의 status와 diff를 확인한다.
2. 해당 저장소의 PR template을 사용한다.
3. 현재 작업에서 확보한 검증 결과를 작성한다.
4. 검증하지 않은 checkbox는 체크하지 않는다.
5. branch를 push한 뒤 PR을 생성한다.

## 금지

- PR 생성을 위해 이미 통과한 테스트를 다시 실행하지 않는다.
- 명시적인 요청 없이 CI 완료를 기다리지 않는다.
- PR 생성 과정에서 코드를 수정하지 않는다.
- PR 생성 성공 후 불필요하게 PR을 반복 조회하지 않는다.

## 실패

실패 원인을 확인하고 해당 단계만 다시 실행한다.
같은 명령을 이유 없이 반복하지 않는다.
