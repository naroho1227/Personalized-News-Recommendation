# 개인 맞춤형 뉴스 추천 플랫폼 — Developer Guide

단국대학교 오픈소스SW기초 9조

이 가이드는 개인 맞춤형 뉴스 추천 플랫폼을 수정하거나 확장하려는 개발자를 위해 작성되었습니다. 프로젝트 구조, 핵심 모듈 설명, 알고리즘 동작 원리, 기능 확장 방법을 다룹니다.

---

## 목차

1. [개발 환경](#1-개발-환경)
2. [프로젝트 구조](#2-프로젝트-구조)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [모듈별 상세 설명](#4-모듈별-상세-설명)
5. [추천 알고리즘 상세](#5-추천-알고리즘-상세)
6. [API 명세](#6-api-명세)
7. [데이터베이스 구조](#7-데이터베이스-구조)
8. [기능 확장 가이드](#8-기능-확장-가이드)
9. [코딩 스타일](#9-코딩-스타일)
10. [알려진 이슈 및 개선 사항](#10-알려진-이슈-및-개선-사항)

---

## 1. 개발 환경

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.9+, JavaScript (ES6), HTML5, CSS3 |
| 백엔드 프레임워크 | FastAPI 0.115.0 |
| ORM | SQLAlchemy 2.0.35 |
| 데이터베이스 | PostgreSQL 16 (Docker) |
| 뉴스 수집 | feedparser 6.0.11 (RSS) |
| 인증 | JWT (python-jose), bcrypt (passlib) |
| 컨테이너 | Docker, Docker Compose |
| 프론트엔드 | Vanilla JS 단일 파일 (빌드 과정 없음) |

### 로컬 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/naroho1227/Personalized-News-Recommendation.git
cd Personalized-News-Recommendation

# 2. PostgreSQL 컨테이너 실행
cd docker
docker-compose up -d

# 3. 패키지 설치 및 서버 실행
cd ../backend
pip install -r requirements.txt
uvicorn main:app --reload
```

접속 주소: `http://localhost:8000`

> **참고**: `database.py`에 설정된 기본 DB 접속 정보는 `postgresql://postgres:1234@localhost:5433/news_db`입니다. Docker Compose로 실행 시 포트가 5433으로 매핑되므로 로컬에 PostgreSQL이 이미 설치된 경우에도 충돌 없이 동작합니다.

---

## 2. 프로젝트 구조

```
Personalized-News-Recommendation/
├── backend/
│   ├── __init__.py
│   ├── main.py           # FastAPI 앱 진입점, 라우터 및 미들웨어 설정
│   ├── models.py         # SQLAlchemy ORM 모델 (User, UserLog)
│   ├── database.py       # DB 연결 및 세션 관리
│   ├── recommend.py      # Softmax 기반 추천 알고리즘
│   ├── rss_collector.py  # RSS 피드 실시간 수집 모듈
│   └── requirements.txt
├── docker/
│   └── docker-compose.yml    # PostgreSQL 컨테이너 설정
├── frountend/
│   ├── index.html            # 전체 UI (로그인, 뉴스카드, 관심도 차트 포함)
│   └── script.js             # Fetch API 기반 백엔드 연동 로직
├── .gitignore
├── README.md
└── USER_GUIDE.md
```

---

## 3. 시스템 아키텍처

```
[사용자 브라우저]
      │  Fetch API (HTTP)
      ▼
[FastAPI 서버 (backend/main.py)]
  ├── POST /auth/register  ── bcrypt 해시 → PostgreSQL 저장
  ├── POST /auth/login     ── 해시 비교 → JWT 24h 토큰 발급
  ├── GET  /recommend      ── 사용자 점수 조회 → Softmax 계산 → RSS 수집 → 20건 반환
  ├── POST /log            ── 클릭 로그 저장 + 카테고리 점수 업데이트
  └── GET  /stats          ── 카테고리별 관심도 비율 반환
      │
      ├── SQLAlchemy ORM
      │        │
      │        ▼
      │   [PostgreSQL (Docker, port 5433)]
      │    ├── users 테이블 (사용자 정보 + 카테고리 점수 7개)
      │    └── user_logs 테이블 (클릭 이력)
      │
      └── feedparser
               │
               ▼
    [언론사 RSS 피드]
     SBS / 한겨레 / 동아일보 / 전자신문
```

---

## 4. 모듈별 상세 설명

### 4.1 `main.py` — FastAPI 앱 진입점

FastAPI 앱을 초기화하고 5개의 핵심 엔드포인트를 등록합니다. 인증이 필요한 엔드포인트(`/recommend`, `/log`, `/stats`)는 `Depends(get_current_user)`를 통해 JWT 검증이 자동으로 처리됩니다.

**주요 함수:**

- `get_current_user(token, db)` — Authorization 헤더의 JWT를 디코딩하여 사용자 객체를 반환합니다. 토큰이 유효하지 않으면 401을 반환합니다.
- `register(body, db)` — 이메일 중복 확인 후 bcrypt로 비밀번호를 해시하여 사용자를 저장합니다. 관심 카테고리는 초기 점수(1.5점)로 반영됩니다.
- `login(form, db)` — 이메일과 비밀번호를 검증하고 24시간 유효한 JWT 토큰을 발급합니다. 응답에는 `access_token`, `token_type`, `user_id`, `nickname`이 포함됩니다.
- `recommend_news(current_user, db)` — 현재 사용자의 관심도 점수를 기반으로 뉴스 20건을 반환합니다.
- `save_log(log, current_user, db)` — 클릭 이벤트를 기록하고 해당 카테고리 점수를 업데이트합니다.
- `get_stats(current_user, db)` — 카테고리별 추천 비율(%)을 반환합니다.

**정적 파일 서빙:**

FastAPI가 프론트엔드 파일을 직접 서빙합니다. `frountend/` 디렉토리를 루트(`/`)에 마운트하여 별도 웹 서버 없이 동작합니다.

```python
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frountend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
```

> **주의**: `frountend`는 오타가 포함된 폴더명이지만 실제 디렉토리명과 일치해야 합니다. 폴더명을 변경할 경우 이 경로도 함께 수정해야 합니다.

---

### 4.2 `recommend.py` — 추천 알고리즘

추천 알고리즘의 핵심 로직이 구현된 모듈입니다. Softmax 변환과 감쇠 계수를 결합하여 개인화와 다양성을 동시에 확보합니다. 자세한 알고리즘 설명은 [5절](#5-추천-알고리즘-상세)을 참조하세요.

**주요 함수:**

- `get_scores(user)` — User 객체에서 7개 카테고리 점수를 딕셔너리로 추출합니다.
- `softmax(scores)` — 점수 딕셔너리를 확률 분포로 변환합니다. 수치 안정성을 위해 최댓값을 차감한 후 지수 변환을 적용합니다.
- `get_ratios(user)` — Softmax 결과에 최소 3% 하한선을 적용한 추천 비율을 반환합니다.
- `update_score(db, user, category)` — 클릭 이벤트 발생 시 감쇠 계수를 적용하여 해당 카테고리 점수를 증가시키고 `db.commit()`으로 즉시 DB에 반영합니다.
- `get_recommendations(db, user_id, total)` — 추천 비율에 따라 카테고리별 기사 수를 결정하고 RSS에서 수집한 뒤 반환합니다.

---

### 4.3 `rss_collector.py` — RSS 수집 모듈

언론사 RSS 피드를 실시간으로 파싱하는 모듈입니다. `/recommend` 요청이 들어올 때마다 호출됩니다.

> **import 경로 주의**: `recommend.py`는 `rss_collector`를 `../../crawler` 경로를 `sys.path`에 추가하여 import합니다. 실제 `rss_collector.py` 파일은 `backend/` 폴더 안에 있으므로, 디렉토리 구조를 변경할 경우 `recommend.py` 상단의 `sys.path.append(...)` 경로도 함께 수정해야 합니다.

**RSS 피드 목록 (`RSS_FEEDS`):**

| 카테고리 | 언론사 |
|----------|--------|
| general | SBS (정치, 사회), 한겨레 |
| technology | 한겨레 (과학), 전자신문 |
| business | SBS (경제) |
| sports | SBS (스포츠), 한겨레, 동아일보 |
| science | 한겨레 (과학), 전자신문 |
| health | 동아일보 |
| entertainment | SBS (연예), 동아일보 |

> **설계 특이사항**: 카테고리 분류는 키워드 기반이 아닌 피드 URL 기반입니다. 언론사가 사전에 분류한 섹션별 RSS URL을 카테고리에 매핑하여 사용합니다.

**`fetch_rss(category, count, exclude_urls)`:**

- `category`에 해당하는 모든 피드 URL을 순회하며 기사를 수집합니다.
- `exclude_urls`에 포함된 URL은 건너뜁니다 (이미 클릭한 기사 제외).
- 기사 수가 `count * 3`에 도달하면 조기 종료합니다 (충분한 후보 확보 목적).
- `summary` 필드가 없는 경우 빈 문자열로 처리하고, 200자를 초과하면 잘라냅니다.

피드 URL을 추가하거나 변경하려면 `RSS_FEEDS` 딕셔너리만 수정하면 됩니다.

---

### 4.4 `models.py` — ORM 모델

SQLAlchemy 모델 두 개로 구성됩니다.

**`User`** — 사용자 정보와 7개 카테고리 관심도 점수를 저장합니다. 점수는 Float 컬럼으로 직접 관리하며 초기값은 1.0입니다.

**`UserLog`** — 사용자의 기사 클릭 이력을 저장합니다. `news_url`을 기준으로 중복 추천을 방지합니다.

---

### 4.5 `database.py` — DB 연결

```python
DATABASE_URL = "postgresql://postgres:1234@localhost:5433/news_db"
```

`get_db()` 제너레이터를 FastAPI의 `Depends`에 주입하면 요청 단위로 세션이 열리고, 요청 종료 시 자동으로 닫힙니다.

DB 접속 정보를 변경하려면 `DATABASE_URL`을 수정하고, `docker-compose.yml`의 환경변수(`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`)와 일치시켜야 합니다.

---

### 4.6 `script.js` — 프론트엔드 로직

Vanilla JS로 구현된 클라이언트 로직입니다. 모든 백엔드 통신은 `fetch()`를 사용합니다.

**주요 함수:**

- `doLogin()` — `FormData`로 OAuth2 형식의 로그인 요청을 전송하고 JWT 토큰과 사용자 정보를 `localStorage`에 저장합니다.
- `doRegister()` — JSON 형식으로 회원가입 요청을 전송합니다. 비밀번호 6자 이상 등 기본 유효성 검사를 포함합니다.
- `loadNews()` — `/recommend` 엔드포인트를 호출하여 뉴스 카드를 렌더링합니다. 로딩 중에는 스켈레톤 UI를 표시합니다.
- `doClick(encodedUrl, encodedCat)` — 기사 클릭 시 `/log`에 click 이벤트를 전송한 뒤 새 탭으로 원문을 엽니다. 700ms 후 관심도 차트를 갱신합니다. `action == "click"`으로 기록된 URL만 이후 추천에서 제외되며, `"view"` 이벤트로만 기록된 기사는 다시 추천될 수 있습니다.
- `renderInterestBars(items)` — `/stats` 응답값을 바탕으로 카테고리별 관심도 비율을 CSS 막대 그래프로 시각화합니다.

**JWT 처리:**

토큰은 `localStorage`에 `np_token` 키로 저장되며, 인증이 필요한 모든 요청의 헤더에 `Authorization: Bearer <token>` 형식으로 첨부됩니다. 401 응답이 오면 자동으로 로그아웃 처리됩니다.

---

## 5. 추천 알고리즘 상세

### 5.1 초기 점수 부여

회원가입 시 선택한 관심 카테고리에는 **1.5점**, 나머지 6개 카테고리에는 **1.0점**이 부여됩니다.

### 5.2 Softmax 변환

카테고리 점수를 확률 분포(추천 비율)로 변환합니다.

$$\text{softmax}(s_i) = \frac{e^{s_i - \max(s)}}{\sum_j e^{s_j - \max(s)}}$$

최댓값을 차감하는 것은 수치 오버플로를 방지하기 위한 처리입니다.

### 5.3 최소 3% 보장

Softmax 결과에 최소 비율(`min_ratio = 0.03`)을 적용합니다.

```python
def get_ratios(user: User) -> dict:
    scores = get_scores(user)
    raw = softmax(scores)
    min_ratio = 0.03
    adjusted = {k: max(v, min_ratio) for k, v in raw.items()}
    total = sum(adjusted.values())
    return {k: v / total for k, v in adjusted.items()}
```

> **알려진 동작**: 최소값 보정 후 재정규화(`/ total`)를 수행하므로 실제 최솟값은 정확히 3%가 아닌 약 2.54%로 수렴합니다. 정확히 3%를 보장하려면 `adjusted` 딕셔너리를 재정규화 없이 반환하는 방식으로 수정해야 합니다.

### 5.4 기사 수 배분

비율에 따라 총 20건을 카테고리별로 배분합니다. 비율 순으로 정렬 후 순서대로 `round(total * ratio)`를 계산하고, 마지막 카테고리에 나머지를 모두 배정하여 합계가 정확히 20건이 되도록 합니다.

### 5.5 감쇠 계수

클릭 시 단순히 +1 대신 감쇠 계수를 곱하여 점수를 증가시킵니다.

$$\text{decay} = \max(0.1,\ 1.0 - \frac{\text{현재 비율}}{\text{포화 비율}})$$

포화 비율(`SATURATION = 0.5`)에 가까워질수록 증가폭이 줄어들어 한 카테고리가 전체 추천의 50% 이상을 차지하기 어려워집니다. 감쇠 계수는 최소 0.1로 고정되어 점수 증가가 완전히 멈추지 않습니다.

---

## 6. API 명세

| Method | Endpoint | 인증 | 설명 |
|--------|----------|------|------|
| GET | `/` | 없음 | 서버 상태 확인 |
| POST | `/auth/register` | 없음 | 회원가입 |
| POST | `/auth/login` | 없음 | 로그인 → JWT 토큰 발급 |
| GET | `/recommend` | JWT | 개인화 뉴스 20건 반환 |
| POST | `/log` | JWT | 클릭 로그 저장 및 점수 업데이트 |
| GET | `/stats` | JWT | 카테고리별 관심도 비율 반환 |

**`POST /auth/register` 요청 바디:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "nickname": "닉네임",
  "interest": "technology"
}
```

**`POST /log` 요청 바디:**
```json
{
  "news_url": "https://...",
  "news_category": "technology",
  "action": "click"
}
```
`action`은 `"view"` 또는 `"click"`만 허용됩니다. 점수 업데이트는 `"click"`일 때만 발생합니다.

**`GET /recommend` 응답 형식:**
```json
[
  {
    "title": "기사 제목",
    "description": "기사 요약 (최대 200자)",
    "url": "https://...",
    "category": "technology"
  }
]
```

API 문서는 서버 실행 후 `http://localhost:8000/docs`(Swagger UI)에서 직접 확인하고 테스트할 수 있습니다.

**`GET /stats` 응답 형식:**
```json
[
  {"name": "technology", "ratio": 24.5},
  {"name": "general", "ratio": 18.3}
]
```
`ratio`는 0~100 사이의 퍼센트 값입니다 (`round(ratio * 100, 2)` 적용).

---

## 7. 데이터베이스 구조

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
| user_id | Integer | 사용자 ID |
| news_url | String | 기사 URL (중복 제외 기준) |
| news_category | String | 기사 카테고리 |
| action | String | 행동 유형 (`click` / `view`) |
| timestamp | DateTime | 로그 발생 시각 (UTC) |

테이블은 서버 최초 실행 시 `Base.metadata.create_all(bind=engine)`으로 자동 생성됩니다. 별도의 마이그레이션 도구는 사용하지 않습니다.

---

## 8. 기능 확장 가이드

### 8.1 RSS 피드 추가

`rss_collector.py`의 `RSS_FEEDS` 딕셔너리에 항목을 추가합니다.

```python
RSS_FEEDS = {
    "technology": [
        "https://www.hani.co.kr/rss/science/",
        "https://rss.etnews.com/Section901.xml",
        "https://새로추가할피드.com/rss.xml",  # 추가
    ],
    ...
}
```

피드 URL이 유효한 RSS/Atom 형식인지 확인하세요. `feedparser`는 대부분의 표준 피드를 지원합니다.

### 8.2 카테고리 추가

카테고리를 추가하려면 다음 네 곳을 함께 수정해야 합니다.

1. **`recommend.py`** — `CATEGORIES` 리스트에 새 카테고리 이름 추가
2. **`models.py`** — `User` 클래스에 `score_새카테고리 = Column(Float, default=1.0)` 추가
3. **`rss_collector.py`** — `RSS_FEEDS`에 새 카테고리 키와 피드 URL 추가
4. **`script.js`** — `CAT_COLORS`와 `CAT_KR`에 색상 코드와 한글 이름 추가

모델 변경 후에는 기존 DB에 새 컬럼이 없으므로, 컨테이너를 재시작하거나 DB를 초기화해야 합니다.

### 8.3 추천 알고리즘 수정

감쇠 계수의 포화 임계값을 조정하려면 `recommend.py`의 상수를 변경합니다.

```python
SATURATION = 0.5  # 높일수록 편중이 더 심해지기 전까지 감쇠가 늦게 시작됨
```

최소 노출 비율을 변경하려면 `get_ratios()` 함수의 `min_ratio`를 수정합니다.

```python
min_ratio = 0.03  # 0.05로 높이면 각 카테고리 최소 ~5% 보장
```

### 8.4 추천 기사 수 변경

`/recommend` 엔드포인트에서 `get_recommendations()`의 `total` 파라미터를 변경합니다.

```python
@app.get("/recommend")
def recommend_news(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    articles = get_recommendations(db, current_user.id, total=30)  # 20 → 30으로 변경
    ...
```

### 8.5 JWT 만료 시간 변경

`main.py`의 상수를 변경합니다.

```python
ACCESS_TOKEN_EXPIRE_HOURS = 24  # 시간 단위
```

---

## 9. 코딩 스타일

Python 코드는 PEP 8을 따릅니다.

- **변수/함수명**: `snake_case` 사용 (`get_ratios`, `update_score`)
- **클래스명**: `PascalCase` 사용 (`User`, `UserLog`)
- **상수**: 대문자 `SNAKE_CASE` 사용 (`SATURATION`, `CATEGORIES`)
- **타입 힌트**: 함수 인자와 반환값에 가능한 한 타입 힌트를 명시합니다.

```python
# 좋은 예
def softmax(scores: dict) -> dict:
    values = list(scores.values())
    ...

# FastAPI 의존성 주입 패턴
@app.get("/recommend")
def recommend_news(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ...
```

JavaScript 코드는 ES6 문법을 사용합니다.

- **변수 선언**: `const` 우선, 재할당이 필요한 경우 `let` 사용
- **비동기 처리**: `async/await` 패턴 사용
- **DOM 조작**: `document.getElementById()` 사용

---

## 10. 알려진 이슈 및 개선 사항

| 이슈 | 설명 | 해결 방법 |
|------|------|-----------|
| 최소 비율 수렴 문제 | `get_ratios()`에서 재정규화로 인해 실제 최솟값이 3%가 아닌 약 2.54%로 수렴 | `adjusted` 딕셔너리를 재정규화 없이 직접 반환 |
| 프론트엔드 폴더명 오타 | `frountend/`는 `frontend/`의 오타이나 실제 폴더명으로 고정됨 | 폴더명 변경 시 `main.py`의 경로도 함께 수정 필요 |
| RSS 수집 지연 | 추천 요청마다 여러 RSS 피드를 실시간 호출하여 응답이 느려질 수 있음 | 캐싱 레이어 추가 또는 백그라운드 주기적 수집 방식으로 전환 |
| DB 마이그레이션 도구 없음 | 모델 변경 시 Alembic 등의 마이그레이션 도구가 없어 수동 처리 필요 | Alembic 도입 권장 |
| SECRET_KEY 하드코딩 | JWT 서명 키가 `main.py`에 평문으로 노출됨 | 환경 변수 또는 `.env` 파일로 분리 |
| HTML description 포함 가능 | 일부 언론사 RSS의 `<description>` 필드에 HTML 태그가 포함될 수 있음 | `rss_collector.py`에서 정규식 기반 HTML 제거 함수 적용 필요 |

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 공식 문서](https://docs.sqlalchemy.org/en/20/)
- [feedparser 공식 문서](https://feedparser.readthedocs.io/)
- [python-jose JWT 라이브러리](https://github.com/mpdavis/python-jose)
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
