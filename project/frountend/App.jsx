import { useState } from "react";

const API = "http://127.0.0.1:8000";

function App() {
    const [userId, setUserId] = useState("");
    const [newsList, setNewsList] = useState([]);

    const getRecommendations = async () => {
        const res = await fetch(`${API}/recommend/${userId}`);
        const data = await res.json();
        setNewsList(data);
    };

    const handleClick = async (newsId) => {
        await fetch(`${API}/log`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: parseInt(userId),
                news_id: newsId,
                action: "click",
            }),
        });
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