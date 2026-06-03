const API = "http:

const CAT_KO = {
  general: "일반", technology: "기술", business: "경제",
  sports: "스포츠", science: "과학", health: "건강", entertainment: "엔터"
};
const CAT_COLOR = {
  general: "#4a6fa5", technology: "#1a6b8a", business: "#9a6e00",
  sports: "#1a7a3e", science: "#6b3fa0", health: "#a0302e", entertainment: "#b5450b"
};

let token = localStorage.getItem("np_token") || null;
let userId = localStorage.getItem("np_uid") || null;
let nickname = localStorage.getItem("np_nick") || null;

window.addEventListener("DOMContentLoaded", () => {
  setDateLabel();
  if (token && userId) {
    showMain();
    loadNews();
    loadStats();
  }
});

function setDateLabel() {
  const now = new Date();
  const days = ["일", "월", "화", "수", "목", "금", "토"];
  document.getElementById("dateLabel").textContent =
    `${now.getFullYear()}년 ${now.getMonth()+1}월 ${now.getDate()}일 ${days[now.getDay()]}요일`;
}

function switchTab(tab) {
  const isLogin = (tab === "login");
  document.getElementById("loginForm").style.display    = isLogin ? "" : "none";
  document.getElementById("registerForm").style.display = isLogin ? "none" : "";
  document.getElementById("tabLogin").classList.toggle("active", isLogin);
  document.getElementById("tabRegister").classList.toggle("active", !isLogin);
  document.getElementById("loginError").textContent = "";
  document.getElementById("registerError").textContent = "";
}

async function login() {
  const email = document.getElementById("loginEmail").value.trim();
  const pw    = document.getElementById("loginPw").value;
  const errEl = document.getElementById("loginError");
  const btn   = document.getElementById("btnLogin");
  errEl.textContent = "";

  if (!email || !pw) { errEl.textContent = "이메일과 비밀번호를 입력해주세요."; return; }

  btn.disabled = true;
  btn.textContent = "로그인 중...";

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password: pw }),
    });
    const data = await res.json();
    if (!res.ok) { errEl.textContent = data.detail || "로그인 실패"; return; }

    token    = data.access_token;
    userId   = String(data.user_id);
    nickname = data.nickname;
    localStorage.setItem("np_token", token);
    localStorage.setItem("np_uid",   userId);
    localStorage.setItem("np_nick",  nickname);
    showMain();
    loadNews();
    loadStats();
  } catch {
    errEl.textContent = "서버에 연결할 수 없습니다.";
  } finally {
    btn.disabled = false;
    btn.textContent = "로그인";
  }
}

async function register() {
  const email    = document.getElementById("regEmail").value.trim();
  const pw       = document.getElementById("regPw").value;
  const nick     = document.getElementById("regNickname").value.trim();
  const interest = document.getElementById("regInterest").value;
  const errEl    = document.getElementById("registerError");
  const btn      = document.getElementById("btnRegister");
  errEl.textContent = "";

  if (!email || !pw || !nick || !interest) {
    errEl.textContent = "모든 항목을 입력해주세요."; return;
  }

  btn.disabled = true;
  btn.textContent = "가입 중...";

  try {
    const res = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password: pw, nickname: nick, interest }),
    });
    const data = await res.json();
    if (!res.ok) { errEl.textContent = data.detail || "가입 실패"; return; }

    document.getElementById("loginEmail").value = email;
    document.getElementById("loginPw").value    = pw;
    switchTab("login");
    toast("가입 완료! 로그인해주세요.");
  } catch {
    errEl.textContent = "서버에 연결할 수 없습니다.";
  } finally {
    btn.disabled = false;
    btn.textContent = "가입하기";
  }
}

function logout() {
  token = null; userId = null; nickname = null;
  localStorage.removeItem("np_token");
  localStorage.removeItem("np_uid");
  localStorage.removeItem("np_nick");
  document.getElementById("authScreen").style.display   = "";
  document.getElementById("mainLayout").classList.remove("visible");
  document.getElementById("mastheadRight").style.display = "none";
  document.getElementById("newsList").innerHTML = "";
  document.getElementById("statsArea").innerHTML =
    '<div style="color:var(--muted);font-size:13px;">추천을 받으면 관심도가 표시됩니다.</div>';
}

function showMain() {
  document.getElementById("authScreen").style.display   = "none";
  document.getElementById("mainLayout").classList.add("visible");
  document.getElementById("mastheadRight").style.display = "";
  document.getElementById("nicknameDisplay").textContent = nickname || "사용자";
  document.getElementById("avatarLetter").textContent   = (nickname || "U")[0].toUpperCase();
}

async function loadNews() {
  const list  = document.getElementById("newsList");
  const errEl = document.getElementById("newsError");
  const btn   = document.getElementById("btnRefresh");
  errEl.innerHTML = "";
  btn.disabled    = true;

  list.innerHTML = Array.from({length: 5}, () => `
    <div class="skeleton-card">
      <div class="skeleton-line" style="width:60px;height:18px;margin-bottom:12px;"></div>
      <div class="skeleton-line" style="width:90%;height:14px;margin-bottom:8px;"></div>
      <div class="skeleton-line" style="width:75%;height:14px;"></div>
    </div>
  `).join("");

  try {
    const res = await fetch(`${API}/recommend/${userId}`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!res.ok) {
      const d = await res.json();
      list.innerHTML = "";
      errEl.innerHTML = `<div class="news-error">${d.detail || "오류가 발생했습니다."}</div>`;
      return;
    }

    const data = await res.json();
    list.innerHTML = "";

    if (!data.length) {
      list.innerHTML = `
        <div class="empty-state">
          <div style="font-size:28px;">📰</div>
          <p>추천 뉴스가 없습니다.<br>뉴스 데이터를 먼저 수집해주세요.</p>
        </div>`;
      return;
    }

    data.forEach((n, i) => {
      const card = document.createElement("div");
      card.className = "news-card";
      card.style.animationDelay = `${i * 40}ms`;
      const color = CAT_COLOR[n.category] || "#555";
      const koName = CAT_KO[n.category] || n.category;
      const safeUrl = n.url ? encodeURI(n.url) : "#";
      card.innerHTML = `
        <div class="card-body">
          <span class="card-tag" style="background:${color}">${koName}</span>
          <div class="card-title">${escHtml(n.title)}</div>
          <div class="card-desc">${escHtml(n.description || "")}</div>
        </div>
        <div class="card-actions">
          <div class="card-num">${String(i+1).padStart(2,"0")}</div>
          <button class="btn-read" onclick="clickNews(${n.id}, '${safeUrl}')">기사 보기 →</button>
        </div>
      `;
      list.appendChild(card);
    });

    loadStats();
    const count = data.length;
    toast(`${count}개의 뉴스를 추천받았습니다 ✓`);

  } catch {
    list.innerHTML = "";
    errEl.innerHTML = `<div class="news-error">서버에 연결할 수 없습니다. (${API})</div>`;
  } finally {
    btn.disabled = false;
  }
}

async function clickNews(newsId, url) {
  try {
    await fetch(`${API}/log`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ user_id: parseInt(userId), news_id: newsId, action: "click" }),
    });
    loadStats();
  } catch {}
  window.open(decodeURI(url), "_blank");
}

async function loadStats() {
  try {
    const res = await fetch(`${API}/stats/${userId}`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!res.ok) return;
    const data = await res.json();
    renderStats(data);
  } catch {}
}

function renderStats(data) {

  const statsArea = document.getElementById("statsArea");
  if (!statsArea) return;

  let entries = [];

  if (Array.isArray(data.categories)) {
    entries = data.categories.map(c => ({
      key: c.name, ratio: c.ratio ?? c.score
    }));
  } else {
    entries = Object.entries(data).map(([k, v]) => ({
      key: k, ratio: typeof v === "object" ? (v.ratio ?? v.score) : v
    }));
  }

  if (!entries.length) return;

  entries.sort((a, b) => b.ratio - a.ratio);

  statsArea.innerHTML = entries.map(({ key, ratio }) => {
    const pct = Math.round((ratio <= 1 ? ratio * 100 : ratio) * 10) / 10;
    const color = CAT_COLOR[key] || "#555";
    const koName = CAT_KO[key] || key;
    return `
      <div class="stat-row">
        <div class="stat-label">
          <span>${koName}</span>
          <span>${pct}%</span>
        </div>
        <div class="stat-bar-bg">
          <div class="stat-bar-fill" style="width:${pct}%;background:${color};"></div>
        </div>
      </div>`;
  }).join("");
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

let toastTimer;
function toast(msg) {
  const el = document.getElementById("noticeBadge");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 3000);
}
