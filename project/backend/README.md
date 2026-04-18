# 뉴스 추천 시스템

## 프로젝트 구조

```
project-root/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── recommend.py
│   ├── check_db.py
│   └── requirements.txt
├── crawler/
│   └── news_collector.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── App.jsx
├── docker/
│   └── docker-compose.yml
└── README.md
```

## 실행 순서

### 1. PostgreSQL 실행
```bash
cd docker
docker-compose up -d
```

### 2. 패키지 설치
```bash
cd backend
pip install -r requirements.txt
```

### 3. 백엔드 실행 (project-root에서)
```bash
uvicorn backend.app.main:app --reload
```

### 4. 뉴스 수집
```bash
python crawler/news_collector.py
```

### 5. 유저 생성
App.jsx의 유저 생성 UI 사용 또는 직접 API 호출:
```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"interest": "technology"}'
```

유효한 interest 값:
general, technology, business, sports, science, health, entertainment

### 6. 프론트엔드 실행

**HTML 버전**: frontend/index.html을 VS Code Live Server로 열기

**React 버전**:
```bash
cd frontend
npm create vite@latest . -- --template react
# 생성된 src/App.jsx를 frontend/App.jsx로 교체
npm install
npm run dev
```

## DB 확인
```bash
python backend/check_db.py
```

## API 문서
서버 실행 후 http://127.0.0.1:8000/docs 접속
