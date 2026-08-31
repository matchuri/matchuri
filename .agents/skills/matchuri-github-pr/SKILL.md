---
name: matchuri-github-pr
description: Matchuri의 root, backend, frontend 저장소에서 사용자가 명시적으로 요청한 GitHub PR을 템플릿에 맞게 생성하거나 수정한다. Markdown 본문 손상 방지와 저장소별 변경 분리가 필요할 때 사용한다.
---

# Matchuri GitHub PR

## 범위

- 사용자가 PR 생성 또는 수정을 명시적으로 요청한 경우에만 GitHub 상태를 변경한다.
- root, `backend/`, `frontend/`를 독립 Git 저장소로 취급한다.
- 현재 작업의 파일만 stage·commit하고 기존 사용자 변경을 포함하지 않는다.

## 절차

1. 대상 저장소의 PR 템플릿과 base branch를 확인한다.
2. PR 본문을 템플릿 구조에 맞는 Markdown으로 작성한다.
3. 본문 UTF-8 bytes를 Base64로 인코딩한다.
4. `scripts/write_pr_body.py --body-base64 <encoded>`로 임시 Markdown 파일을 만든다.
5. `gh pr create` 또는 `gh pr edit`에는 inline `--body`를 사용하지 않고 `--body-file <path>`만 사용한다.
6. `gh pr view --json body,url,state,baseRefName,headRefName`으로 저장된 본문과 PR 상태를 확인한다.
7. 생성된 임시 파일의 정확한 절대 경로를 확인한 뒤 삭제한다.

## 안전 기준

- PR 생성·수정 전에 외부 변경 권한이 현재 요청에 포함되는지 확인한다.
- PR 템플릿 checkbox는 실제 검증 결과만 표시한다.
- API나 DB 영향이 있으면 관련 PR과 후속 consumer 작업을 명시한다.
- 검증 실패나 본문 불일치가 있으면 자동으로 재시도하지 말고 원인을 확인한다.

## 본문 파일 생성

스크립트는 Markdown을 shell 인자로 직접 전달할 때 생기는 개행·backtick·특수문자 손상을 방지한다. 출력된 파일 경로만 `gh --body-file`에 전달한다.
