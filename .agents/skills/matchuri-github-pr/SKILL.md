---
name: matchuri-github-pr
description: Matchuri의 root, backend, frontend 저장소에서 사용자가 명시적으로 요청한 GitHub PR을 저장소별 템플릿에 맞춰 빠르게 생성하거나 수정한다.
---

# Matchuri GitHub PR

PR 제출은 구현·리뷰를 다시 수행하는 단계가 아니다. 마지막 코드 변경 이후 확보된 검증 결과를 재사용하고, 알려진 차단 문제가 없으면 바로 제출한다.

## 원칙

- 사용자가 PR 생성 또는 수정을 명시적으로 요청한 경우에만 GitHub 상태를 변경한다.
- root, `backend/`, `frontend/`를 독립 Git 저장소로 취급한다.
- 요청한 PR에 속하는 변경만 포함한다. 작성자가 사용자인지 agent인지는 포함 기준이 아니다.
- 검증하지 않은 template checkbox는 비워 두고 제한 사항에 적는다.
- 코드가 바뀌지 않았다면 테스트와 audit를 반복하지 않는다.
- 원격 CI는 현재 상태만 보고한다. 완료 확인 요청이 없으면 기다리거나 polling하지 않는다.
- 알려진 compile 오류나 충돌을 해결하거나 PR 단계에서 코드를 바꾼 경우에만 해당 영역 규칙에 따라 필요한 검증을 실행한다.

## 흐름

1. 대상 저장소에서 status, diff, PR template, base branch를 확인한다.
2. 요청 범위 파일만 stage·commit하고 branch를 push한다.
3. template에 검증 결과와 API·DB·consumer 영향을 적는다.
4. 본문을 UTF-8 Base64로 인코딩해 `scripts/write_pr_body.py --body-base64 <encoded>`로 임시 파일을 만든다.
5. inline `--body` 대신 `--body-file`로 PR을 생성하거나 수정한다.
6. `gh pr view --json body,url,state,baseRefName,headRefName`으로 한 번 확인한 뒤 임시 파일을 삭제한다.

실패하면 원인을 확인하고 필요한 부분만 고친다. 같은 명령을 무작정 반복하지 않는다.
