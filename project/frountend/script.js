// 백엔드 서버 주소 (FastAPI)
const API = "http://127.0.0.1:8000";

async function loadNews() {

  // 입력한 사용자 ID 가져오기
  const userId = document.getElementById("userId").value;

  // 추천 API 요청
  const res = await fetch(`${API}/recommend/${userId}`);

  // JSON 데이터로 변환
  const data = await res.json();

  // 뉴스 리스트 영역 가져오기
  const list = document.getElementById("newsList");

  // 기존 내용 초기화
  list.innerHTML = "";

  // 뉴스 데이터 하나씩 화면에 출력
  data.forEach(n => {

    // div 생성
    const div = document.createElement("div");
    div.className = "news";

    // 뉴스 정보 출력
    div.innerHTML = `
        <h3>${n.title}</h3>
        <p>카테고리: ${n.category}</p>

        <!-- 조회 로그 버튼 -->
        <button onclick="viewLog(${userId}, ${n.id})">조회</button>

        <!-- 클릭 로그 + 기사 이동 -->
        <button onclick="clickLog(${userId}, ${n.id}, '${n.url}')">기사보기</button>
    `;

    // 화면에 추가
    list.appendChild(div);
  });
}

/*
 * 조회(view) 로그 저장 함수
 * POST /log 호출
 */
async function viewLog(userId, newsId) {

  await fetch(`${API}/log`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },

    // 서버로 보낼 데이터
    body: JSON.stringify({
      user_id: userId,
      news_id: newsId,
      action: "view"
    })
  });

  alert("조회 로그 저장됨");
}

/*
 * 클릭(click) 로그 저장 + 기사 이동
 */
async function clickLog(userId, newsId, url) {

  await fetch(`${API}/log`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({
      user_id: userId,
      news_id: newsId,
      action: "click"
    })
  });

  // 새 탭으로 기사 열기
  window.open(url, "_blank");
}