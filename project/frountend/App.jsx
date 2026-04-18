import { useState } from "react";

const API = "http://127.0.0.1:8000";

const CATEGORIES = [
    "general", "technology", "business",
    "sports", "science", "health", "entertainment"
];

function App() {
    const [userId, setUserId] = useState("");
    const [newsList, setNewsList] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const [newInterest, setNewInterest] = useState("technology");
    const [createdUser, setCreatedUser] = useState(null);

    const createUser = async () => {
        setError("");
        try {
            const res = await fetch(`${API}/users`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ interest: newInterest }),
            });
            const data = await res.json();
            if (!res.ok) { setError(data.detail); return; }
            setCreatedUser(data);
            setUserId(String(data.id));
        } catch {
            setError("서버에 연결할 수 없습니다.");
        }
    };

    const getRecommendations = async () => {
        if (!userId) { setError("User ID를 입력해주세요."); return; }
        setLoading(true);
        setError("");
        setNewsList([]);
        try {
            const res = await fetch(`${API}/recommend/${userId}`);
            const data = await res.json();
            if (!res.ok) { setError(data.detail); return; }
            if (data.length === 0) { setError("추천 뉴스가 없습니다."); return; }
            setNewsList(data);
        } catch {
            setError("서버에 연결할 수 없습니다.");
        } finally {
            setLoading(false);
        }
    };

    const handleClick = async (newsId, url) => {
        await fetch(`${API}/log`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: parseInt(userId), news_id: newsId, action: "click" }),
        });
        window.open(url, "_blank");
    };

    return (
        <div style={{ padding: "20px", fontFamily: "Arial" }}>
            <h1>뉴스 추천 시스템</h1>

            <div style={{ marginBottom: "20px", padding: "12px", border: "1px solid #ddd" }}>
                <h3 style={{ margin: "0 0 8px" }}>신규 유저 생성</h3>
                <select
                    value={newInterest}
                    onChange={(e) => setNewInterest(e.target.value)}
                    style={{ padding: "6px", marginRight: "8px" }}
                >
                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <button onClick={createUser} style={{ padding: "6px 12px" }}>유저 생성</button>
                {createdUser && (
                    <span style={{ marginLeft: "10px", color: "green" }}>
                        생성됨 — ID: {createdUser.id} / 관심사: {createdUser.interest}
                    </span>
                )}
            </div>

            <div style={{ marginBottom: "20px" }}>
                <input
                    type="number"
                    placeholder="User ID 입력"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    style={{ padding: "8px", marginRight: "10px" }}
                />
                <button onClick={getRecommendations} disabled={loading} style={{ padding: "8px" }}>
                    {loading ? "불러오는 중..." : "추천 받기"}
                </button>
            </div>

            {error && <p style={{ color: "red" }}>{error}</p>}

            <ul style={{ marginTop: "20px", padding: 0, listStyle: "none" }}>
                {newsList.map((news) => (
                    <li
                        key={news.id}
                        style={{ padding: "10px", borderBottom: "1px solid #ccc" }}
                    >
                        <strong>{news.title}</strong> ({news.category})
                        <br />
                        <small>{news.description}</small>
                        <br />
                        <button
                            onClick={() => handleClick(news.id, news.url)}
                            style={{ marginTop: "6px", padding: "4px 10px" }}
                        >
                            기사 보기
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;
