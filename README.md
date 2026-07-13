# Matchuri 개발 워크스페이스

이 저장소는 Matchuri 팀원이 로컬 개발 환경을 처음 구성할 때 사용하는 워크스페이스 루트입니다. 제품 소개, 포트폴리오, 팀 소개는 [GitHub Wiki](https://github.com/matchuri/matchuri/wiki)에서 관리합니다.

## 저장소 구성

Matchuri는 세 개의 독립 Git 저장소를 한 워크스페이스에서 사용합니다.

| 경로 | 저장소 | 역할 |
| --- | --- | --- |
| `/` | [matchuri/matchuri](https://github.com/matchuri/matchuri) | 공통 개발 문서, 에이전트 규칙과 워크스페이스 진입점 |
| `backend/` | [matchuri/backend](https://github.com/matchuri/backend) | Spring Boot API 서버 |
| `frontend/` | [matchuri/frontend](https://github.com/matchuri/frontend) | Next.js 웹 애플리케이션 |

`backend/`와 `frontend/`는 루트 저장소에서 추적하지 않습니다. 브랜치, 커밋, 원격 저장소 작업도 각 디렉터리에서 따로 수행합니다.

## 준비 사항

- Git과 Matchuri GitHub 조직 저장소 접근 권한
- JDK 21
- Docker Desktop 또는 Docker Engine
- Node.js 22 이상, npm 10 이상
- Infisical CLI와 Matchuri `dev` 환경 접근 권한

## 최초 설정

### 1. 워크스페이스와 애플리케이션 저장소 받기

```bash
git clone https://github.com/matchuri/matchuri.git
cd matchuri
git clone https://github.com/matchuri/backend.git backend
git clone https://github.com/matchuri/frontend.git frontend
```

### 2. Infisical 연결하기

루트 디렉터리에서 로그인하고 Matchuri 프로젝트를 선택합니다. 생성되는 루트 `.infisical.json`은 로컬 설정이며 Git에서 추적하지 않습니다.

```bash
infisical login
infisical init
```

조직 또는 프로젝트가 보이지 않으면 진행하기 전에 팀 관리자에게 Infisical 접근 권한을 요청합니다.

### 3. 백엔드 실행하기

먼저 [백엔드 README](https://github.com/matchuri/backend#3-실행환경)의 로컬 예시대로 `backend/.env`를 준비합니다.

```powershell
cd backend
docker compose up -d db
.\gradlew.bat bootRun
```

macOS/Linux에서는 `./gradlew bootRun`을 사용합니다. 서버가 기동되면 다음 주소를 확인합니다.

- Health: <http://localhost:8080/api/v1/health>
- Swagger UI: <http://localhost:8080/docs/swagger-ui.html>

### 4. 프론트엔드 실행하기

새 터미널에서 실행합니다. `npm run dev`는 Infisical의 `dev` 환경을 `frontend/.env.local`로 내보낸 뒤 개발 서버를 시작합니다.

```bash
cd frontend
npm ci
npm run dev
```

브라우저에서 <http://localhost:3000>을 엽니다.

## 기본 검증

```powershell
cd backend
.\gradlew.bat test

cd ..\frontend
npm run lint
npm run build
```

macOS/Linux에서는 백엔드 테스트 명령으로 `./gradlew test`를 사용합니다.

## 작업 시작 전

- 공통 개발 문서 진입점: [docs/README.md](docs/README.md)
- 백엔드 작업 규칙: 로컬 `backend/AGENTS.md`
- 프론트엔드 작업 규칙: 로컬 `frontend/AGENTS.md`
- 제품 소개와 협업 맥락: [GitHub Wiki](https://github.com/matchuri/matchuri/wiki)

작업하려는 저장소에서 브랜치를 만들고, 동작이나 API 계약·데이터 구조·도메인 용어가 바뀌면 루트 `docs/`의 관련 문서도 함께 갱신합니다.
