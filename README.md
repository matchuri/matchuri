# MATCHURI

Matchuri는 함께 먹을 점심 메뉴를 빠르게 정하기 위한 메뉴 의사결정 서비스입니다.

맛집 검색보다 `후보 3개 안팎 + 투표 + 최종 메뉴 확정` 흐름에 집중해, 팀이 메뉴를 고르는 데 쓰는 시간을 줄이는 것을 목표로 합니다.

## 팀원 소개

<div align="center">

| Member | Member |
| ------ | ------ |
|   <img src="https://github.com/yourjinKR.png" width="150" />     |    <img src="https://github.com/Leejaelim.png" width="150" />     |
| 유어진 <br/>백엔드, 인프라    | 이재림 <br/> 프론트엔드, 기획, 디자인   |

</div>

## 목차

1. [프로젝트 소개](#프로젝트-소개)  
2. [기술 스택](#기술-스택)  
3. [서비스 아키텍처](#서비스-아키텍처)  
4. [프로젝트 구조](#프로젝트-구조)
5. [문서 구조](#문서-구조)

## 프로젝트 소개

Matchuri는 개인 취향과 그룹 상황을 바탕으로 점심 후보를 좁히고, 투표를 통해 최종 메뉴를 확정하는 서비스입니다.

- 핵심 문제: 점심 메뉴를 정하는 데 반복적으로 드는 대화 비용
- 핵심 흐름: 후보 추천, 그룹 투표, 최종 메뉴 확정
- 사람용 문서: [matchuri.wiki/Home.md](matchuri.wiki/Home.md)

## 기술 스택

## 서비스 아키텍처

## 프로젝트 구조

```text
backend/        Spring Boot 백엔드
frontend/       프론트엔드 애플리케이션
docs/           개발 기준 문서
matchuri.wiki/  사람용 위키와 포트폴리오 문서
secrets/        내부 운영 문서와 실행 계획
```

## 문서 구조

- [matchuri.wiki/Home.md](matchuri.wiki/Home.md): 프로젝트 소개, 포트폴리오, 협업 안내
- [docs/README.md](docs/README.md): 개발 기준 문서 홈
- [docs/api/index.md](docs/api/index.md): API 계약과 상태
- [docs/data/index.md](docs/data/index.md): 데이터 모델
- [docs/decisions/index.md](docs/decisions/index.md): 설계 결정
- [matchuri.wiki/버전관리.md](matchuri.wiki/%EB%B2%84%EC%A0%84%EA%B4%80%EB%A6%AC.md): Git 협업 규칙
