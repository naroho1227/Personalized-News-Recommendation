# 📰 개인 맞춤형 뉴스 추천 플랫폼

> 단국대학교 오픈소스SW기초  
> 사용자의 클릭 행동을 학습해 점점 정확해지는 실시간 뉴스 추천 시스템

---

## 🌟 서비스 소개

> **"읽을수록, 나에게 맞춰지는 뉴스"**

포털 사이트의 뉴스 탭을 열면 정치·사회·연예·스포츠 기사가 뒤섞여 쏟아집니다.  
정작 내가 관심 있는 분야의 기사를 찾으려면 수십 개의 기사를 훑어야 하고,  
포털이 중요하다고 판단한 기사가 상단에 노출될 뿐 — 내가 어떤 기사를 클릭하는지는 다음 추천에 전혀 반영되지 않습니다.

**이 플랫폼은 그 문제를 해결합니다.**

- 회원가입 시 관심 카테고리를 하나 선택하면 즉시 맞춤 뉴스가 추천됩니다
- 기사를 클릭할수록 해당 카테고리의 가중치가 높아지고, 추천 결과가 점점 나의 취향에 맞춰집니다
- 특정 카테고리에 편중되지 않도록 다양성도 자동으로 유지됩니다
- SBS, 한겨레, 동아일보, 전자신문의 RSS 피드에서 **실시간으로** 최신 기사를 수집해 항상 오늘의 뉴스를 보여드립니다

모든 기술 스택은 오픈소스로만 구성했으며, Docker 한 번으로 누구나 로컬에서 바로 실행할 수 있습니다.

---

## 🚀 빠른 시작 (Quick Start)

### 사전 요구사항

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치
- Python 3.9 이상

### 1단계 — 저장소 클론

```bash
git clone https://github.com/naroho1227/Personalized-News-Recommendation.git
cd Personalized-News-Recommendation
```

### 2단계 — PostgreSQL DB 실행 (Docker)

```bash
cd docker
docker-compose up -d
```

> ⚠️ 처음 실행 시 PostgreSQL 이미지를 다운로드하므로 수십 초 정도 소요될 수 있습니다.

### 3단계 — 백엔드 서버 실행

```bash
cd ../backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4단계 — 브라우저에서 접속

```
http://localhost:8000
```

접속하면 로그인/회원가입 화면이 나타납니다. 계정을 만들고 바로 사용해 보세요!

---

## 📖 사용 방법

### 1. 회원가입

- 이메일, 비밀번호, 닉네임을 입력하고 **관심 카테고리 1개**를 선택해 주세요
- 선택 가능한 카테고리: 일반 / 기술 / 경제 / 스포츠 / 과학 / 건강 / 엔터테인먼트
- 가입 즉시 선택한 카테고리에 가중치가 높게 설정되어 첫 추천부터 반영됩니다

### 2. 뉴스 추천받기

- 로그인 후 **"뉴스 새로 추천받기"** 버튼을 누르면 20건의 기사가 카드 형태로 표시됩니다
- 각 카드에는 기사 제목, 언론사, 링크가 포함되어 있습니다

### 3. 기사 클릭 → 추천 개선

- 기사 카드를 클릭하면 해당 언론사 기사 페이지로 이동하고, **동시에 클릭 기록이 서버에 저장**됩니다
- 클릭한 기사의 카테고리 점수가 올라가고, 다음 추천 요청부터 해당 카테고리 기사 비율이 높아집니다
- 같은 기사는 두 번 추천되지 않습니다 (이미 클릭한 URL은 자동으로 제외됩니다)

### 4. 관심도 차트 확인

- 화면 하단의 막대 차트에서 카테고리별 관심도 비율을 실시간으로 확인하실 수 있습니다
- 기사를 클릭할 때마다 차트가 즉시 갱신되어 추천 시스템이 어떻게 변화하는지 눈으로 확인하실 수 있습니다

---

## 📌 프로젝트 개요

### 핵심 특징

- 🎯 **실시간 개인화** — 클릭한 기사의 카테고리 점수가 즉시 반영되어 다음 추천부터 변화합니다
- 📡 **RSS 실시간 수집** — SBS, 한겨레, 동아일보, 전자신문의 RSS 피드에서 최신 기사를 매 요청마다 수집합니다
- 🧮 **Softmax 기반 추천 알고리즘** — 특정 카테고리 편중을 방지하고 최소 3% 다양성을 보장합니다
- 🔐 **JWT 인증** — 회원가입/로그인부터 모든 API 요청에 토큰 기반 인증이 적용됩니다
- 🐳 **Docker 기반 배포** — PostgreSQL DB를 컨테이너로 운영하고, 볼륨으로 데이터 영속성을 보장합니다

---

## 👥 팀원 및 담당 분야

| 이름 | 학번 | 담당 분야 |
|------|------|-----------|
| 김준환 | 32251072 | 추천 알고리즘 |
| 김건희 | 32247063 | 백엔드 (FastAPI, 인증) |
| 윤채원 | 32247579 | DB 구축 (PostgreSQL, SQLAlchemy) |
| 임수종 | 32213775 | 프론트엔드 (Vanilla JS, UI) |

---

## 🗂 디렉토리 구조

```
Personalized-News-Recommendation/
├── backend/              # FastAPI 서버 (API 엔드포인트, 인증, 추천 로직)
│   ├── main.py           # FastAPI 앱 진입점, 라우터 등록
│   ├── auth.py           # 회원가입/로그인, JWT 발급
│   ├── recommend.py      # Softmax 기반 추천 알고리즘
│   ├── rss_collector.py  # RSS 피드 실시간 수집 모듈
│   ├── models.py         # SQLAlchemy ORM 모델 (User, UserLog)
│   └── database.py       # DB 연결 및 세션 관리
├── crawler/              # (구) NewsAPI 기반 수집기 (RSS 전환 전 버전)
├── docker/               # Docker Compose 설정
│   └── docker-compose.yml
├── frountend/            # 프론트엔드 (Vanilla JS 단일 파일)
│   ├── index.html        # 전체 UI (로그인, 뉴스카드, 관심도 차트)
│   └── script.js         # Fetch API 기반 백엔드 연동 로직
├── .gitignore
├── USER_GUIDE.md
└── ngrok.exe             # 외부 노출용 터널링 도구
```

---

## 🏗 시스템 아키텍처

```
[사용자 브라우저]
      │  Fetch API (HTTP)
      ▼
[FastAPI 서버 (백엔드)]
  ├── /auth/register  ── bcrypt 해시 → PostgreSQL 저장
  ├── /auth/login     ── 해시 비교 → JWT 24h 토큰 발급
  ├── /recommend      ── 사용자 점수 조회 → Softmax 계산 → RSS 수집 → 20건 반환
  ├── /log            ── 클릭 로그 저장 + 카테고리 점수 업데이트
  └── /stats          ── 카테고리별 관심도 비율 반환
      │
      ├── SQLAlchemy ORM
      │        │
      │        ▼
      │   [PostgreSQL (Docker)]
      │    ├── users 테이블 (점수 7개 포함)
      │    └── user_logs 테이블
      │
      └── feedparser
               │
               ▼
    [언론사 RSS 피드]
     SBS / 한겨레 / 동아일보 / 전자신문
```

---

## 📋 API 명세

| Method | Endpoint | 인증 | 설명 |
|--------|----------|------|------|
| GET | `/` | 없음 | 서버 상태 확인 |
| POST | `/auth/register` | 없음 | 회원가입 (email, password, nickname, interest) |
| POST | `/auth/login` | 없음 | 로그인 → JWT 토큰 발급 |
| GET | `/recommend` | JWT | 개인화 뉴스 20건 실시간 반환 |
| POST | `/log` | JWT | 클릭 로그 저장 및 관심도 점수 업데이트 |
| GET | `/stats` | JWT | 카테고리별 관심도 비율 반환 |

---

## 🗄 데이터베이스 구조

### `users` 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | Integer (PK) | 사용자 고유 ID |
| email | String (Unique) | 이메일 (로그인 ID) |
| password | String | bcrypt 해시 비밀번호 |
| nickname | String | 닉네임 |
| score_general | Float | 일반 카테고리 관심도 점수 |
| score_technology | Float | 기술 카테고리 관심도 점수 |
| score_business | Float | 경제 카테고리 관심도 점수 |
| score_sports | Float | 스포츠 카테고리 관심도 점수 |
| score_science | Float | 과학 카테고리 관심도 점수 |
| score_health | Float | 건강 카테고리 관심도 점수 |
| score_entertainment | Float | 엔터테인먼트 카테고리 관심도 점수 |

### `user_logs` 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | Integer (PK) | 로그 고유 ID |
| user_id | Integer (FK) | 사용자 ID |
| news_url | String | 기사 URL (중복 제외 기준) |
| news_category | String | 기사 카테고리 |
| action | String | 행동 유형 (click) |
| timestamp | DateTime | 로그 발생 시각 |

---

## ⚙️ 구현 상세

---

### 🧮 추천 알고리즘 (Softmax 기반 개인화)

**담당: 김준환**

단순히 점수가 높은 카테고리 기사를 많이 보여주는 방식이 아니라, **"특정 카테고리가 독점되지 않으면서도 클릭 행동이 반영되는"** 자기조절형 알고리즘을 설계했습니다.

**동작 원리:**

1. **초기 점수 부여** — 회원가입 시 선택한 관심 카테고리에 1.5점, 나머지 6개에 1.0점을 부여합니다
2. **Softmax 변환** — 7개 카테고리 점수를 Softmax 함수에 통과시켜 확률 분포로 변환합니다. 어떤 카테고리도 추천 확률이 0이 되지 않도록 보장합니다
3. **최소 3% 노출 보장** — 모든 카테고리에 최소 3%의 추천 비율을 강제 적용하여 뉴스 편식을 방지합니다
4. **20건 배분** — 계산된 비율에 따라 총 20건의 뉴스를 카테고리별로 나누어 RSS에서 수집합니다
5. **감쇠 계수 적용** — 클릭 시 점수를 단순히 +1 하는 대신, 해당 카테고리의 비율이 포화 임계값(50%)에 가까워질수록 증가폭이 줄어드는 감쇠 함수를 적용합니다. 한 카테고리가 전체 추천의 절반 이상을 차지하지 못하도록 자동 조절됩니다

```
점수 증가량 = 기본 증가량 × (1 - 현재 비율 / 포화 임계값)
```

**시행착오:**
- 초기에는 단순 정렬 방식(높은 점수 → 많은 기사)을 사용했는데, 특정 카테고리를 몇 번만 클릭해도 나머지 카테고리 기사가 아예 사라지는 문제가 발생했습니다. Softmax와 최솟값 보정을 추가하면서 해결했습니다.
- 감쇠 계수의 포화 임계값을 처음에는 70%로 설정했는데, 너무 빨리 감쇠가 시작되어 사용자가 변화를 느끼기 어려웠습니다. 반복 테스트 후 50%로 조정했습니다.
- 최소 비율 보장 로직 추가 후 총합이 100%를 초과하는 수치 오류가 발생했고, 최솟값 보정 후 나머지 비율을 비례적으로 재조정하는 정규화 과정을 별도로 추가하여 해결했습니다.

---

### 🔧 백엔드 (FastAPI + 인증)

**담당: 김건희**

FastAPI로 총 5개의 엔드포인트를 구현했습니다. 각 엔드포인트는 `APIRouter`를 통해 모듈별로 분리하여 `main.py`에서 일괄 등록하는 구조를 채택했습니다.

**인증 흐름:**
- 회원가입 시 비밀번호를 `bcrypt`로 단방향 해시하여 DB에 저장합니다
- 로그인 시 입력값을 해시 후 DB의 해시값과 비교하고, 일치하면 24시간 유효한 JWT 토큰을 발급합니다
- 인증이 필요한 엔드포인트(`/recommend`, `/log`, `/stats`)는 `Depends(get_current_user)`를 통해 토큰 검증이 자동으로 연결됩니다. 각 함수마다 별도로 인증 코드를 작성할 필요 없이 FastAPI의 의존성 주입 시스템이 처리합니다

```python
# 인증이 필요한 엔드포인트에 Depends 적용 예시
@router.get("/recommend")
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ...
```

**시행착오:**
- 초기 설계에서는 URL에 `user_id`를 직접 포함하는 `GET /recommend/{user_id}` 방식으로 구현했으나, 사용자가 다른 user_id로 요청을 위조할 수 있는 보안 문제가 있었습니다. JWT 토큰 도입 이후 `get_current_user()`로 토큰에서 사용자 ID를 추출하는 `GET /recommend` 방식으로 전면 교체했습니다.
- 로그인 후 프론트엔드에서 빈 화면만 나오는 문제가 발생했는데, 정적 파일 서빙 설정이 잘못되어 FastAPI가 `index.html`을 제대로 반환하지 못한 것이 원인이었습니다. `StaticFiles` 마운트 경로를 수정하여 해결했습니다.

---

### 🗄 DB 구축 (PostgreSQL + SQLAlchemy + Docker)

**담당: 윤채원**

프로젝트의 모든 데이터를 영속적으로 저장하는 계층을 담당했습니다. PostgreSQL을 Docker 컨테이너로 운영하고, Python 코드와 DB 사이의 연결은 SQLAlchemy ORM을 통해 처리했습니다.

**구현 내용:**

- **`models.py`** — `User`와 `UserLog` 두 개의 테이블을 SQLAlchemy 클래스로 정의했습니다. 카테고리별 점수 7개는 `User` 테이블의 Float 컬럼으로 직접 관리합니다
- **`database.py`** — `create_engine()`으로 DB 연결 URL을 설정하고 `SessionLocal` 팩토리를 생성합니다. 각 API 요청마다 `get_db()` 제너레이터를 통해 독립적인 세션을 열고 요청 종료 시 자동으로 닫습니다
- **Docker 볼륨 설정** — `docker-compose.yml`에 named volume을 설정하여 컨테이너가 재시작되어도 DB 데이터가 사라지지 않도록 영속성을 보장합니다
- **클릭 시 점수 업데이트** — `/log` API 요청이 들어오면 로그를 저장함과 동시에 해당 카테고리의 `score_*` 컬럼을 감쇠 계수가 적용된 값으로 갱신합니다

```python
# models.py 핵심 구조
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)          # bcrypt 해시
    nickname = Column(String)
    score_general = Column(Float, default=1.0)
    score_technology = Column(Float, default=1.0)
    score_business = Column(Float, default=1.0)
    score_sports = Column(Float, default=1.0)
    score_science = Column(Float, default=1.0)
    score_health = Column(Float, default=1.0)
    score_entertainment = Column(Float, default=1.0)
```

**시행착오:**
- 가장 먼저 만난 문제는 **포트 5432 충돌**이었습니다. 로컬 머신에 설치된 PostgreSQL이 이미 5432 포트를 점유하고 있어 Docker 컨테이너 바인딩에 실패했습니다. `docker-compose.yml`에서 호스트 포트를 5433으로 변경하고 연결 URL도 함께 수정하여 해결했습니다.
- `bcrypt` 라이브러리 버전 충돌로 해시 검증 시 오류가 발생했습니다. `passlib`과 `bcrypt` 버전 간 호환성 문제였으며, 특정 버전 조합으로 고정(`bcrypt==4.0.1`)하여 해결했습니다.
- SQLAlchemy 세션 문제로 점수 업데이트가 DB에 반영되지 않는 경우가 있었습니다. `db.commit()`과 `db.refresh(user)` 순서를 명확히 하여 해결했습니다.

---

### 🎨 프론트엔드 (Vanilla JS)

**담당: 임수종**

초기에는 React 프레임워크 기반으로 계획했으나, 빌드 환경 구성 없이 바로 실행 가능한 **Vanilla JS 단일 파일 구조**로 변경했습니다. `index.html` 하나에 HTML 구조, CSS 스타일, JavaScript 로직이 모두 들어있으며, 별도의 빌드나 패키지 설치 없이 브라우저에서 즉시 실행됩니다.

**주요 구현 내용:**

- **뉴스 카드 UI** — 각 기사를 카드 형태로 렌더링합니다. 제목, 언론사, 링크를 포함하며, 클릭 시 `/log` API를 자동 호출해 클릭 이벤트를 서버에 전송합니다
- **Fetch API 비동기 통신** — 모든 백엔드 API 요청은 `fetch()`로 처리합니다. JWT 토큰은 `localStorage`에 저장하고 매 요청 헤더에 `Authorization: Bearer <token>` 형식으로 첨부합니다
- **관심도 막대 차트** — `/stats` 응답값을 기반으로 각 카테고리별 비율을 CSS 너비 애니메이션으로 시각화합니다. 뉴스를 클릭할 때마다 차트가 실시간으로 갱신됩니다

**시행착오:**
- React로 시작했지만 Node.js 환경 세팅, `npm install`, Webpack 빌드 과정이 팀 전체 개발 환경과 맞지 않는 문제가 반복되었습니다. 배포와 협업 편의성을 위해 Vanilla JS로 전환했고, 오히려 의존성 충돌 없이 빠르게 개발할 수 있었습니다.
- 로그인 성공 후 토큰을 받아도 화면 전환이 되지 않는 버그가 있었습니다. `fetch` 응답 처리에서 `.json()` 파싱 타이밍과 조건부 렌더링 로직의 순서가 잘못된 것이 원인이었으며, 순서를 수정하여 해결했습니다.

---

### 📡 RSS 수집 모듈

RSS(Really Simple Syndication)는 언론사 서버가 항상 제공하는 XML 파일로, 최신 기사 제목, 요약, 링크, 날짜가 정형화된 구조로 담겨 있습니다. `feedparser` 라이브러리로 이를 파싱하여 뉴스 리스트를 생성합니다.

수집 언론사 및 RSS URL:
- **SBS 뉴스** — https://news.sbs.co.kr
- **한겨레** — https://www.hani.co.kr
- **동아일보** — https://rss.donga.com
- **전자신문** — https://rss.etnews.com

`/recommend` 요청이 들어올 때마다 실시간으로 RSS를 수집하며, 이미 클릭한 기사 URL(`user_logs`에 존재하는 URL)과 중복 기사는 자동으로 제외됩니다.

**초기 계획 → 변경 이유 (NewsAPI → RSS 전환):**

초기에는 NewsAPI(newsapi.org)를 사용했으나 세 가지 문제가 발견되었습니다:

1. 무료 플랜 기준 하루 100건 호출 제한 → 하루에 제공 가능한 뉴스 수에 한계가 있었습니다
2. 기사를 DB에 미리 저장해두는 구조 → 실시간 최신 뉴스 제공이 불가능하고 저장 비용이 발생했습니다
3. 한국 뉴스가 거의 없음 → 사실상 영어 기사만 제공할 수 있었습니다

RSS로 전환하면서 이 세 가지를 모두 해결했습니다: 호출 제한 없음, 요청마다 실시간 수집, 국내 언론사 안정적 지원.

---

## ✅ 테스트 결과 요약

| 테스트 항목 | 결과 |
|------------|------|
| 중복 이메일 회원가입 차단 | ✅ 정상 (400 에러 반환) |
| 잘못된 비밀번호 로그인 거부 | ✅ 정상 (401 에러 반환) |
| 뉴스 20건 실시간 추천 | ✅ 정상 (GET /recommend 200 OK) |
| 기사 클릭 시 점수 업데이트 | ✅ 정상 (POST /log 200 OK) |
| 관심도 차트 실시간 갱신 | ✅ 정상 (GET /stats 200 OK) |
| 감쇠 함수 (클릭 반복 시 증가폭 감소) | ✅ 정상 작동 확인 |
| 최소 3% 추천 비율 보장 | ✅ 정상 (모든 카테고리 노출 확인) |

---

## 🛠 기술 스택

| 분류 | 기술 |
|------|------|
| 백엔드 | FastAPI, Python, Uvicorn |
| 인증 | JWT (python-jose), bcrypt (passlib) |
| ORM | SQLAlchemy |
| DB | PostgreSQL |
| 컨테이너 | Docker, Docker Compose |
| 뉴스 수집 | feedparser (RSS) |
| 프론트엔드 | Vanilla JS, HTML, CSS (단일 파일) |

---

## 📚 용어 설명

| 용어 | 설명 |
|------|------|
| FastAPI | Python 기반 고성능 RESTful API 프레임워크 |
| SQLAlchemy | Python용 ORM 라이브러리. SQL 없이 Python 객체로 DB를 조작할 수 있습니다 |
| PostgreSQL | 오픈소스 관계형 데이터베이스. Docker 컨테이너로 운영합니다 |
| Softmax | 카테고리 점수를 확률 분포로 변환하는 함수. 어떤 카테고리도 추천 확률이 0이 되지 않도록 보장합니다 |
| JWT | JSON Web Token. 로그인 인증 정보를 암호화하며 토큰만으로 사용자를 식별할 수 있습니다 |
| bcrypt | 비밀번호 단방향 해시 암호화 알고리즘 |
| feedparser | RSS/Atom 문서 파싱 Python 라이브러리 |
| RSS | Really Simple Syndication. 언론사가 제공하는 표준 XML 형식의 기사 피드 |
