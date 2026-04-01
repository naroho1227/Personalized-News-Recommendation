import { useState } from "react";

function App() {
    const [userId, setUserId] = useState("");
    const [newsList, setNewsList] = useState([]);

    // mock 데이터(api 연동 전에 확인차 mock 데이터를 AI한테 추천받아 구성하였습니다.
    const mockNews = [
        { id: 1, title: "AI 기술 급성장", category: "IT" },
        { id: 2, title: "금리 인상 소식", category: "경제" },
        { id: 3, title: "챔피언스리그 결과", category: "스포츠" },
        { id: 4, title: "신작 영화 개봉", category: "연예" },
        { id: 5, title: "기후 변화 이슈", category: "사회" }
    ];

    // 추천 가져오기 (mock)
    const getRecommendations = () => {
        // 나중에 API로 교체 가능
        // fetch(`/recommend/${userId}`)
        setNewsList(mockNews);
    };

    // 클릭 로그 (mock)
    const handleClick = (newsId) => {
        const logData = {
            user_id: userId,
            news_id: newsId
        };

        // 나중에 API로 교체 가능!
        // fetch("/log", { method: "POST", body: JSON.stringify(logData) })

        console.log("로그 전송:", logData);
    };

    return (
        <div style={{ padding: "20px", fontFamily: "Arial" }}>
            <h1>뉴스 추천 시스템</h1>

            <input
                type="text"
                placeholder="User ID 입력"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                style={{ padding: "8px", marginRight: "10px" }}
            />

            <button onClick={getRecommendations} style={{ padding: "8px" }}>
                추천 받기
            </button>

            <ul style={{ marginTop: "20px" }}>
                {newsList.map((news) => (
                    <li
                        key={news.id}
                        onClick={() => handleClick(news.id)}
                        style={{
                            padding: "10px",
                            borderBottom: "1px solid #ccc",
                            cursor: "pointer"
                        }}
                    >
                        <strong>{news.title}</strong> ({news.category})
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;