const API = "";


let token = localStorage.getItem("token") || null;
let userId = localStorage.getItem("userId") || null;
let nick = localStorage.getItem("nick") || null;

window.addEventListener("DOMContentLoaded", () => {
  if (token && userId) {
    showMain();
    loadStats();
  }
});


function showTab(tab) {
  document.getElementById("loginForm").style.display = tab === "login" ? "" : "none";
  document.getElementById("registerForm").style.display = tab === "register" ? "" : "none";
  document.querySelectorAll(".tab").forEach((el, i) => {
    el.classList.toggle("active", (i === 0) === (tab === "login"));
  });
  clearMsg();
}


function parseError(detail) {
  if (!detail) return "오류가 발생했습니다.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map(d => d.msg || JSON.stringify(d)).join(", ");
  return JSON.stringify(detail);
}
function setError(msg) { document.getElementById("error").textContent = typeof msg === "string" ? msg : parseError(msg); document.getElementById("success").textContent = ""; }
function setSuccess(msg) { document.getElementById("success").textContent = msg; document.getElementById("error").textContent = ""; }
function clearMsg() { setError(""); }


async function doRegister() {
  const email = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const nickname = document.getElementById("regNickname").value.trim();
  const interest = document.getElementById("regInterest").value;

  if (!email || !password || !nickname || !interest) { setError("모든 항목을 입력해주세요."); return; }

  try {
    const res = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, nickname, interest }),
    });
    const data = await res.json();
    if (!res.ok) { setError(parseError(data.detail) || "회원가입 실패"); return; }
    setSuccess(`회원가입 완료. (ID: ${data.id}) 로그인해주세요.`);
    showTab("login");
  } catch { setError("서버에 연결할 수 없습니다."); }
}

async function doLogin() {
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;

  if (!email || !password) { setError("이메일과 비밀번호를 입력해주세요."); return; }

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) { setError(parseError(data.detail) || "로그인 실패"); return; }

    token = data.access_token;
    userId = String(data.user_id);
    nick = data.nickname;
    localStorage.setItem("token", token);
    localStorage.setItem("userId", userId);
    localStorage.setItem("nick", nick);

    showMain();
    loadStats();
  } catch { setError("서버에 연결할 수 없습니다."); }
}

function doLogout() {
  token = userId = nick = null;
  localStorage.clear();
  document.getElementById("authSection").style.display = "";
  document.getElementById("mainSection").style.display = "none";
  document.getElementById("newsList").innerHTML = "";
}


function showMain() {
  document.getElementById("authSection").style.display = "none";
  document.getElementById("mainSection").style.display = "block";
  document.getElementById("userInfo").textContent = `${nick}님 (ID: ${userId})`;
}


async function loadStats() {
  try {
    const res = await fetch(`${API}/stats/${userId}`, authHeader());
    if (!res.ok) return;
    const data = await res.json();
    renderChart(data.stats);
  } catch { }
}

function renderChart(stats) {
  const chart = document.getElementById("chart");
  chart.innerHTML = stats.map(s => `
    <div class="bar-row">
      <span class="bar-label">${s.category}</span>
      <div class="bar-bg">
        <div class="bar-fill" style="width:${s.ratio}%"></div>
      </div>
      <span class="bar-pct">${s.ratio}%</span>
    </div>
  `).join("");
}


async function loadNews() {
  const list = document.getElementById("newsList");
  list.innerHTML = "<p style='color:#888'>불러오는 중...</p>";

  try {
    const res = await fetch(`${API}/recommend/${userId}`, authHeader());
    const data = await res.json();

    if (!res.ok) { list.innerHTML = `<p style='color:red'>${data.detail || "오류"}</p>`; return; }
    if (!data.length) { list.innerHTML = "<p>추천 뉴스가 없습니다.</p>"; return; }

    list.innerHTML = data.map(n => `
      <div class="news-item">
        <span class="badge">${n.category}</span>
        <h3>${n.title}</h3>
        <p>${n.description || ""}</p>
        <div class="news-btns">
          <button class="btn-secondary btn-sm" onclick="viewLog(${n.id})">조회</button>
          <button class="btn-primary btn-sm"   onclick="clickLog(${n.id}, '${escUrl(n.url)}')">기사 보기</button>
        </div>
      </div>
    `).join("");
  } catch { list.innerHTML = "<p style='color:red'>서버에 연결할 수 없습니다.</p>"; }
}

async function viewLog(newsId) {
  await fetch(`${API}/log`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader().headers },
    body: JSON.stringify({ news_id: newsId, action: "view" }),
  });
  alert("조회 로그가 저장되었습니다.");
}

async function clickLog(newsId, url) {
  await fetch(`${API}/log`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader().headers },
    body: JSON.stringify({ news_id: newsId, action: "click" }),
  });
  window.open(url, "_blank");

  setTimeout(loadStats, 500);
}


function authHeader() {
  return { headers: { Authorization: `Bearer ${token}` } };
}

function escUrl(url) {
  return (url || "").replace(/'/g, "%27");
}
