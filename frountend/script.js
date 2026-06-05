const API = "http://127.0.0.1:8000";

const CAT_COLORS = {
  general:       "#2c3e50",
  technology:    "#1a6b8a",
  business:      "#7d5a00",
  sports:        "#1a7a3e",
  science:       "#5b2d8e",
  health:        "#a0302e",
  entertainment: "#b5450b",
};

const CAT_KR = {
  general:       "일반",
  technology:    "기술",
  business:      "경제",
  sports:        "스포츠",
  science:       "과학",
  health:        "건강",
  entertainment: "엔터테인먼트",
};

let token = localStorage.getItem("np_token") || null;
let currentUser = JSON.parse(localStorage.getItem("np_user") || "null");

window.addEventListener("DOMContentLoaded", () => {
  if (token && currentUser) {
    showApp();
    loadStats();
  }
});

function switchTab(tab) {
  document.getElementById("loginForm").style.display    = tab === "login"    ? "" : "none";
  document.getElementById("registerForm").style.display = tab === "register" ? "" : "none";
  document.getElementById("tabLogin").classList.toggle("active",    tab === "login");
  document.getElementById("tabRegister").classList.toggle("active", tab === "register");
  document.getElementById("authError").textContent = "";
}

async function doLogin() {
  const email    = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;
  if (!email || !password) { setAuthError("이메일과 비밀번호를 입력하세요."); return; }

  try {
    const form = new FormData();
    form.append("username", email);
    form.append("password", password);

    const res  = await fetch(`${API}/auth/login`, { method: "POST", body: form });
    const data = await res.json();

    if (!res.ok) { setAuthError(data.detail || "로그인에 실패했습니다."); return; }

    token       = data.access_token;
    currentUser = { id: data.user_id, nickname: data.nickname };
    localStorage.setItem("np_token", token);
    localStorage.setItem("np_user", JSON.stringify(currentUser));

    showApp();
    loadStats();
    showToast(`${currentUser.nickname}님, 환영합니다.`);
  } catch {
    setAuthError("서버에 연결할 수 없습니다.");
  }
}

async function doRegister() {
  const email    = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const nickname = document.getElementById("regNickname").value.trim();
  const interest = document.getElementById("regInterest").value;

  if (!email || !password || !nickname) { setAuthError("모든 항목을 입력하세요."); return; }
  if (password.length < 6) { setAuthError("비밀번호는 6자 이상이어야 합니다."); return; }

  try {
    const res  = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, nickname, interest }),
    });
    const data = await res.json();

    if (!res.ok) { setAuthError(data.detail || "회원가입에 실패했습니다."); return; }

    showToast("가입이 완료되었습니다. 로그인하세요.");
    switchTab("login");
    document.getElementById("loginEmail").value = email;
  } catch {
    setAuthError("서버에 연결할 수 없습니다.");
  }
}

function logout() {
  token       = null;
  currentUser = null;
  localStorage.removeItem("np_token");
  localStorage.removeItem("np_user");

  document.getElementById("authOverlay").style.display   = "flex";
  document.getElementById("mastheadRight").style.display = "none";
  document.getElementById("newsFeed").innerHTML = `
    <div class="empty-state">
      <div class="big-icon">📋</div>
      <h3>뉴스를 불러와보세요</h3>
      <p>위의 '새로 추천받기' 버튼을 눌러<br>맞춤 뉴스를 확인하세요.</p>
    </div>`;
  document.getElementById("errorMsg").innerHTML = "";
  document.getElementById("interestBars").innerHTML =
    `<p style="color:var(--muted);font-size:13px;">로그인 후 확인할 수 있습니다.</p>`;
}

function showApp() {
  document.getElementById("authOverlay").style.display   = "none";
  document.getElementById("mastheadRight").style.display = "flex";
  document.getElementById("mastheadNickname").textContent = currentUser.nickname + "님";
  document.getElementById("avatarInitial").textContent    = currentUser.nickname.charAt(0).toUpperCase();
}

async function loadStats() {
  if (!token) return;
  try {
    const res = await fetch(`${API}/stats`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) return;
    const data = await res.json();
    renderInterestBars(data);
  } catch {}
}

function renderInterestBars(items) {
  const container = document.getElementById("interestBars");
  if (!items || items.length === 0) {
    container.innerHTML = `<p style="color:var(--muted);font-size:13px;">데이터가 없습니다.</p>`;
    return;
  }
  const sorted = [...items].sort((a, b) => b.ratio - a.ratio);
  container.innerHTML = sorted.map(item => {
    const color = CAT_COLORS[item.name] || "#888";
    const kr    = CAT_KR[item.name]    || item.name;
    const ratio = Math.round(item.ratio * 10) / 10;
    return `
      <div class="interest-bar-item">
        <div class="interest-bar-label">
          <span>${kr}</span>
          <span class="pct">${ratio.toFixed(1)}%</span>
        </div>
        <div class="interest-bar-track">
          <div class="interest-bar-fill" style="width:${ratio}%;background:${color}"></div>
        </div>
      </div>`;
  }).join("");
}

async function loadNews() {
  if (!token) return;

  const feed    = document.getElementById("newsFeed");
  const errorEl = document.getElementById("errorMsg");
  const btn     = document.getElementById("recommendBtn");

  errorEl.innerHTML = "";
  btn.disabled      = true;
  btn.textContent   = "불러오는 중...";

  feed.innerHTML = Array(5).fill(`
    <div class="skeleton-card">
      <div class="skeleton-line short"></div>
      <div class="skeleton-line wide"></div>
      <div class="skeleton-line medium"></div>
    </div>`).join("");

  try {
    const res = await fetch(`${API}/recommend`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!res.ok) {
      const d = await res.json();
      if (res.status === 401) { logout(); return; }
      showError(d.detail || "기사를 불러오지 못했습니다.");
      feed.innerHTML = "";
      return;
    }

    const articles = await res.json();

    if (!articles || articles.length === 0) {
      showError("추천 기사가 없습니다.");
      feed.innerHTML = "";
      return;
    }

    renderNews(articles);
    loadStats();
    showToast(`${articles.length}개의 기사를 불러왔습니다.`);

  } catch {
    showError("서버에 연결할 수 없습니다.");
    feed.innerHTML = "";
  } finally {
    btn.disabled    = false;
    btn.textContent = "새로 추천받기";
  }
}

function renderNews(articles) {
  const feed = document.getElementById("newsFeed");
  if (!articles || articles.length === 0) {
    feed.innerHTML = `
      <div class="empty-state">
        <div class="big-icon">📋</div>
        <h3>뉴스를 불러와보세요</h3>
        <p>위의 '새로 추천받기' 버튼을 눌러<br>맞춤 뉴스를 확인하세요.</p>
      </div>`;
    return;
  }

  feed.innerHTML = articles.map((n, i) => {
    const color   = CAT_COLORS[n.category] || "#888";
    const kr      = CAT_KR[n.category]    || n.category;
    const title   = (n.title || "").replace(/</g, "&lt;");
    const desc    = (n.description || "").replace(/</g, "&lt;");
    const safeUrl = encodeURIComponent(n.url || "");
    const safeCat = encodeURIComponent(n.category || "");

    return `
      <div class="news-card" style="animation-delay:${i * 0.04}s">
        <div class="news-card-body">
          <span class="news-tag" style="background:${color}">${kr}</span>
          <div class="news-title">${title}</div>
          ${desc ? `<div class="news-desc">${desc}</div>` : ""}
        </div>
        <div class="news-actions">
          <div class="news-number">${String(i + 1).padStart(2, "0")}</div>
          <button class="btn-read" onclick="doClick('${safeUrl}','${safeCat}')">기사 보기 →</button>
        </div>
      </div>`;
  }).join("");
}

async function doClick(encodedUrl, encodedCat) {
  const url      = decodeURIComponent(encodedUrl);
  const category = decodeURIComponent(encodedCat);

  try {
    await fetch(`${API}/log`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ news_url: url, news_category: category, action: "click" }),
    });
  } catch {}

  window.open(url, "_blank");
  setTimeout(loadStats, 700);
}

function setAuthError(msg) {
  document.getElementById("authError").textContent = msg;
}

function showError(msg) {
  document.getElementById("errorMsg").innerHTML = `<div class="error-msg">${msg}</div>`;
}

function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2800);
}
