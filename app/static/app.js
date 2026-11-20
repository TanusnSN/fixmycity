"use strict";

/* ---- Self-contained bootstrap: builds the page skeleton and styles itself, so an old
   index.html / style.css cannot hold the new design back. ---- */
(function bootstrap() {
  document.querySelectorAll('link[rel="stylesheet"][href*="style.css"]').forEach((l) => l.remove());
  const st = document.createElement("style");
  st.id = "fmc-style";
  st.textContent = "\n:root { --bg:#070d0c; --card:#0f1a17; --card2:#0b1412; --text:#e8f1ee; --muted:#8aa39b; --line:#1f322d; --brand:#12805a; --brand-hi:#34d399; --brand-text:#fff; --danger:#f87171; color-scheme: dark; }\n* { box-sizing: border-box; }\n[hidden] { display: none !important; }\nbody { margin:0; min-height:100vh; display:flex; flex-direction:column; color:var(--text); background: radial-gradient(1200px 600px at 20% -10%, #0f2a22 0, transparent 60%), var(--bg); font: 15px/1.55 Inter, system-ui, -apple-system, \"Segoe UI\", Roboto, sans-serif; }\nh2 { margin:0 0 14px; } h3 { margin:0 0 8px; font-size:1.05rem; }\na { color: var(--brand-hi); } small, .muted { color: var(--muted); }\nheader { display:flex; flex-wrap:wrap; gap:6px 14px; align-items:center; padding:12px 24px; position:sticky; top:0; z-index:1000; background:rgba(7,13,12,.85); backdrop-filter:blur(8px); border-bottom:1px solid var(--line); }\nheader .brand { font-weight:800; font-size:1.2rem; color:#fff; text-decoration:none; display:flex; align-items:center; }\n.logo { display:inline-grid; place-items:center; width:34px; height:34px; border-radius:10px; background:var(--brand); margin-right:10px; font-size:1rem; }\n.accent { color: var(--brand-hi); }\nheader a.link { text-decoration:none; color:var(--muted); padding:5px 10px; border-radius:8px; }\nheader a.link:hover { color:var(--text); background:var(--card); }\nheader .spacer { flex:1; }\nmain { flex:1; width:100%; max-width:1100px; margin:0 auto; padding:22px 16px 50px; }\nfooter { border-top:1px solid var(--line); padding:14px 24px; color:var(--muted); font-size:.85rem; display:flex; flex-wrap:wrap; gap:6px 26px; justify-content:center; }\n.card { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; margin-bottom:16px; }\n.grid { display:grid; grid-template-columns:1fr 1fr; gap:12px 16px; } .grid .full { grid-column:1 / -1; }\n.stack { display:grid; gap:14px; }\n@media (max-width:700px) { .grid { grid-template-columns:1fr; } }\nlabel { display:flex; flex-direction:column; gap:6px; font-weight:600; font-size:.85rem; }\ninput, select, textarea { font:inherit; padding:11px 12px; border:1px solid #20332e; border-radius:10px; background:var(--card2); color:var(--text); width:100%; }\ninput::placeholder, textarea::placeholder { color:#4d625b; }\ninput:focus, select:focus, textarea:focus, button:focus-visible, a:focus-visible { outline:2px solid var(--brand-hi); outline-offset:2px; }\nbutton { font:inherit; cursor:pointer; padding:10px 16px; border-radius:10px; border:1px solid var(--line); background:var(--card2); color:var(--text); }\nbutton:hover { border-color:var(--brand); }\nbutton.primary { background:var(--brand); color:var(--brand-text); border-color:var(--brand); font-weight:700; } button.primary:hover { background:#159a6c; }\nbutton.danger { color:var(--danger); border-color:#5b2b2b; } button.small { padding:4px 10px; font-size:.85rem; } button:disabled { opacity:.55; cursor:not-allowed; }\n.row { display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:space-between; }\n.tabs { display:grid; grid-template-columns:1fr 1fr; gap:4px; padding:4px; margin:14px 0 18px; border-radius:12px; background:var(--card2); border:1px solid var(--line); }\n.tabs button { border:0; background:transparent; color:var(--muted); font-weight:600; } .tabs button.active { background:#15271f; color:#fff; }\n.hero { display:grid; grid-template-columns:1.15fr 1fr; gap:56px; align-items:center; min-height:66vh; }\n@media (max-width:900px) { .hero { grid-template-columns:1fr; gap:28px; min-height:0; } }\n.hero h1 { font-size:clamp(2.3rem,5.2vw,3.7rem); line-height:1.04; letter-spacing:-.03em; font-weight:700; margin:14px 0; }\n.hero .lead { color:var(--muted); font-size:1.05rem; max-width:480px; }\n.eyebrow { color:var(--brand-hi); font-size:.72rem; letter-spacing:.18em; font-weight:700; }\n.eyebrow::before { content:\"\"; display:inline-block; width:24px; height:1px; background:currentColor; margin-right:10px; vertical-align:middle; }\n.trust { display:flex; flex-wrap:wrap; gap:8px 20px; margin:18px 0; color:var(--muted); font-size:.85rem; }\n.helpbox { border:1px solid var(--line); background:var(--card); border-radius:12px; padding:12px 14px; display:inline-block; font-size:.9rem; }\n.auth { padding:28px; border-radius:18px; margin:0; box-shadow:0 20px 60px rgba(0,0,0,.35); } .auth h2 { margin-bottom:4px; font-size:1.5rem; }\n.map { height:320px; border-radius:12px; border:1px solid var(--line); z-index:0; } .map.tall { height:62vh; min-height:360px; }\n.leaflet-container { background:#0b1412; } .leaflet-tile-pane { filter:invert(1) hue-rotate(180deg) brightness(.92) contrast(.9); }\n.leaflet-popup-content-wrapper, .leaflet-popup-tip { background:var(--card); color:var(--text); }\n.badge { display:inline-block; padding:1px 9px; border-radius:999px; font-size:.75rem; font-weight:700; color:#fff; background:var(--c,#6b7280); white-space:nowrap; }\n.flag { color:var(--danger); font-weight:700; font-size:.8rem; }\n.list-item { display:block; text-decoration:none; color:inherit; cursor:pointer; } .list-item:hover { border-color:var(--brand); }\n.stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:16px; }\n.stat { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:14px; color:var(--muted); } .stat b { display:block; font-size:1.8rem; line-height:1.1; color:var(--text); }\n.bars .bar { display:grid; grid-template-columns:140px 1fr 36px; gap:8px; align-items:center; margin:6px 0; font-size:.9rem; }\n.bars .fill { height:12px; background:var(--brand); border-radius:6px; min-width:3px; }\n.table-wrap { overflow-x:auto; } table { width:100%; border-collapse:collapse; font-size:.92rem; }\nth, td { text-align:left; padding:9px 10px; border-bottom:1px solid var(--line); vertical-align:top; } th { color:var(--muted); font-weight:600; }\ntbody tr.click { cursor:pointer; } tbody tr.click:hover { background:var(--card2); }\n.filters { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; align-items:end; }\n.timeline { list-style:none; margin:0; padding:0 0 0 14px; border-left:3px solid var(--line); }\n.timeline li { margin:0 0 12px; padding-left:12px; position:relative; }\n.timeline li::before { content:\"\"; position:absolute; left:-22px; top:6px; width:11px; height:11px; border-radius:50%; background:var(--brand-hi); }\n.photos { display:flex; flex-wrap:wrap; gap:8px; margin:10px 0; } .photos img { height:110px; border-radius:10px; border:1px solid var(--line); }\n.match { border:1px solid var(--line); border-left:4px solid #d97706; border-radius:10px; padding:8px 12px; margin:8px 0; background:var(--card2); } .match.likely { border-left-color:var(--danger); }\n.legend { display:flex; flex-wrap:wrap; gap:10px; margin-top:10px; font-size:.85rem; color:var(--muted); }\n.legend i { display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:4px; background:var(--c); }\n#toast { position:fixed; left:50%; bottom:24px; transform:translateX(-50%); background:#e8f1ee; color:#07120e; padding:10px 18px; border-radius:10px; opacity:0; pointer-events:none; transition:opacity .25s; z-index:3000; max-width:90vw; }\n#toast.show { opacity:1; } #toast.err { background:#b42318; color:#fff; }\n.notice { padding:10px 12px; border-radius:10px; background:var(--card2); border:1px dashed var(--line); margin-bottom:12px; }\n\nhtml{scroll-behavior:smooth}\n.card{transition:border-color .15s,transform .15s}.list-item:hover{transform:translateY(-1px)}\n.how{margin:56px 0 10px}.how h2{text-align:center;font-size:1.6rem}\n.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-top:18px}\n.step{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}\n.step span{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;background:var(--brand);color:#fff;font-weight:700;margin-bottom:10px}\n.step p{margin:6px 0 0;color:var(--muted);font-size:.9rem}\n.loading{display:flex;align-items:center;gap:10px;color:var(--muted);padding:40px 0;justify-content:center}\n.spin{width:18px;height:18px;border:3px solid var(--line);border-top-color:var(--brand-hi);border-radius:50%;animation:sp .8s linear infinite}\n@keyframes sp{to{transform:rotate(360deg)}}\n";
  document.head.appendChild(st);
  const addLink = (href) => {
    if (document.querySelector('link[href="' + href + '"]')) return;
    const l = document.createElement("link"); l.rel = "stylesheet"; l.href = href; document.head.appendChild(l);
  };
  addLink("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap");
  addLink("https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css");
  document.title = "FixMyCity";
  document.body.innerHTML = '<header id="nav"></header><main id="view" aria-live="polite"></main><footer id="foot"></footer><div id="toast" role="status"></div>';
})();
function ensureLeaflet() {
  if (window.L) return Promise.resolve();
  return new Promise((res) => {
    const sc = document.createElement("script");
    sc.src = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js";
    sc.onload = res; sc.onerror = res; document.head.appendChild(sc);
  });
}

/* ---------- helpers ---------- */
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (s) => (s ? new Date(s + "Z").toLocaleString() : "");
const label = (s) => String(s).replace(/_/g, " ").toLowerCase().replace(/^./, (c) => c.toUpperCase());

const CATS = ["ROAD", "STREETLIGHT", "WATER_LEAKAGE", "DRAINAGE", "OTHER"];
const STATUSES = ["SUBMITTED", "VERIFIED", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "REJECTED", "REOPENED", "WITHDRAWN"];
const PRIOS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const NEXT = {
  SUBMITTED: ["VERIFIED", "REJECTED"], VERIFIED: ["ASSIGNED", "REJECTED"],
  ASSIGNED: ["IN_PROGRESS", "VERIFIED"], IN_PROGRESS: ["RESOLVED", "ASSIGNED"],
  RESOLVED: [], REJECTED: ["VERIFIED"], REOPENED: ["VERIFIED", "ASSIGNED", "IN_PROGRESS"], WITHDRAWN: [],
};
const SCOLOR = { SUBMITTED: "#6b7280", VERIFIED: "#2563eb", ASSIGNED: "#7c3aed", IN_PROGRESS: "#d97706", RESOLVED: "#16a34a", REJECTED: "#dc2626", REOPENED: "#db2777", WITHDRAWN: "#9ca3af" };
const PCOLOR = { LOW: "#16a34a", MEDIUM: "#d97706", HIGH: "#ea580c", CRITICAL: "#dc2626" };
const badge = (s) => `<span class="badge" style="--c:${SCOLOR[s]}">${label(s)}</span>`;
const pbadge = (p) => `<span class="badge" style="--c:${PCOLOR[p]}">${label(p)}</span>`;
const fmtHours = (h) => (h == null ? "n/a" : h < 1 ? `${Math.round(h * 60)} min` : h < 48 ? `${h.toFixed(1)} h` : `${(h / 24).toFixed(1)} days`);
const options = (list, sel) => list.map((o) => `<option value="${o}" ${o === sel ? "selected" : ""}>${label(o)}</option>`).join("");

let token = localStorage.getItem("token");
let me = null;
let map = null;
const HELPLINE = { phone: "1800-000-0000", email: "support@fixmycity.example", hours: "Mon-Sat, 9 AM - 6 PM" };
function renderFooter() {
  const tel = HELPLINE.phone.replace(/[^+\d]/g, "");
  $("#foot").innerHTML = `<span><b>Customer care &amp; helpline</b></span>
    <span>&#9742; <a href="tel:${tel}">${esc(HELPLINE.phone)}</a></span>
    <span>&#9993; <a href="mailto:${esc(HELPLINE.email)}">${esc(HELPLINE.email)}</a></span>
    <span>${esc(HELPLINE.hours)}</span>`;
}
const view = () => $("#view");

function toast(msg, isErr = false) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "show" + (isErr ? " err" : "");
  clearTimeout(toast.t);
  toast.t = setTimeout(() => (t.className = ""), 3500);
}

async function api(path, opts = {}) {
  const headers = {};
  if (token) headers.Authorization = "Bearer " + token;
  let body = opts.body;
  if (body && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }
  const res = await fetch(path, { method: opts.method || "GET", headers, body });
  if (res.status === 204) return null;
  let data = null;
  try { data = await res.json(); } catch (e) { /* no body */ }
  if (!res.ok) {
    if (res.status === 401 && token && !opts.login) { logout(false); }
    let msg = data && data.detail;
    if (Array.isArray(msg)) msg = msg.map((e) => `${e.loc.slice(-1)[0]}: ${e.msg}`).join("; ");
    const err = new Error(msg || `Request failed (${res.status})`);
    err.status = res.status;
    throw err;
  }
  return data;
}

function go(path) {
  if (location.hash === "#" + path) route();
  else location.hash = path;
}

function logout(redirect = true) {
  token = null; me = null;
  localStorage.removeItem("token");
  if (redirect) { toast("Logged out"); go("/login"); }
}

/* ---------- maps ---------- */
function newMap(id, center = [12.2958, 76.6394], zoom = 13) {
  if (map) { map.remove(); map = null; }
  map = L.map(id).setView(center, zoom);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  return map;
}
function dot(c) {
  return L.circleMarker([c.lat, c.lng], { radius: 9, color: "#fff", weight: 2, fillColor: SCOLOR[c.status], fillOpacity: 0.95 });
}

/* ---------- navigation ---------- */
function renderNav() {
  const links = [`<a class="link" href="#/map">Public Map</a>`];
  if (me && me.role === "CITIZEN") links.push(`<a class="link" href="#/report">Report</a>`, `<a class="link" href="#/mine">My complaints</a>`);
  if (me) links.push(`<a class="link" href="#/notifications">Notifications <span id="bell"></span></a>`);
  if (me && me.role === "ADMIN") links.push(`<a class="link" href="#/admin">Dashboard</a>`, `<a class="link" href="#/admin/complaints">Complaints</a>`);
  if (me && me.role === "CITIZEN") links.push(`<a class="link" href="#/community">Community</a>`);
  if (me && me.role === "ADMIN") links.push(`<a class="link" href="#/admin/users">Users</a>`);
  $("#nav").innerHTML =
    `<a class="brand" href="#/map"><span class="logo">&#128205;</span>Fix<span class="accent">My</span>City</a><span class="spacer"></span>${links.join("")}` +
    (me
      ? `<span class="muted">${esc(me.name)} (${label(me.role)})</span><button class="small" id="logout">Log out</button>`
      : `<a class="link" href="#/login">Log in</a>`);
  const lo = $("#logout");
  if (lo) lo.onclick = () => logout();
  refreshBell();
}

async function route() {
  const h = location.hash.slice(1) || (me ? (me.role === "ADMIN" ? "/admin" : "/report") : "/login");
  const [a, b, c] = h.split("/").filter(Boolean);
  if (map) { map.remove(); map = null; }
  renderNav();
  if (a !== "login") view().innerHTML = '<div class="loading"><span class="spin"></span>Loading...</div>';
  try {
    if (a === "login") return viewLogin();
    if (a === "map") return await viewMap();
    if (!me) return go("/login");
    if (a === "notifications") return await viewNotifications();
    if (a === "community" && me.role === "CITIZEN") return await viewCommunity();
    if (a === "report" && me.role === "CITIZEN") return viewReport();
    if (a === "mine" && me.role === "CITIZEN") return b ? await viewMineDetail(b) : await viewMine();
    if (a === "admin" && me.role === "ADMIN") {
      if (b === "users") return await viewAdminUsers();
      if (b === "complaints") return await viewAdminList();
      if (b === "complaint" && c) return await viewAdminDetail(c);
      return await viewDashboard();
    }
    view().innerHTML = `<div class="card">That page is not available for your account.</div>`;
  } catch (e) {
    view().innerHTML = `<div class="card"><h3>Something went wrong</h3><p>${esc(e.message)}</p></div>`;
  }
}

/* ---------- login / register ---------- */
function viewLogin() {
  const tel = HELPLINE.phone.replace(/[^+\d]/g, "");
  view().innerHTML = `
    <section class="hero">
      <div class="hero-text">
        <div class="eyebrow">CIVIC SERVICES, SIMPLIFIED</div>
        <h1>A better city starts with <span class="accent">your voice.</span></h1>
        <p class="lead">Report local issues, follow their progress, and help make your neighbourhood work better for everyone.</p>
        <div class="trust"><span>&#10003; Secure &amp; private</span><span>&#10003; Email verified</span><span>&#10003; Duplicate-aware</span></div>
        <div class="helpbox"><b>Customer care &amp; helpline</b><br>
          <a href="tel:${tel}">${esc(HELPLINE.phone)}</a> &middot; <a href="mailto:${esc(HELPLINE.email)}">${esc(HELPLINE.email)}</a><br>
          <small>${esc(HELPLINE.hours)}</small></div>
      </div>
      <div class="auth card" id="auth"></div>
    </section>
    <section class="how">
      <h2>How FixMyCity works</h2>
      <div class="steps">
        <div class="step"><span>1</span><b>Report</b><p>Drop a pin, describe the problem and add photos.</p></div>
        <div class="step"><span>2</span><b>Duplicates linked</b><p>Similar reports nearby are matched, so crews see one problem, not ten.</p></div>
        <div class="step"><span>3</span><b>Authorities act</b><p>Departments are assigned and urgent issues are prioritised.</p></div>
        <div class="step"><span>4</span><b>Track and get notified</b><p>Follow every update here and by email.</p></div>
      </div>
    </section>`;
  const box = $("#auth");
  let email = "";
  const input = (name, text, type, attrs) => `<label>${text}<input name="${name}" type="${type}" ${attrs || ""}></label>`;
  const pass = (name, text, ac) => input(name, text, "password", `required minlength="6" maxlength="72" autocomplete="${ac}"`);
  const codeBox = input("code", "Verification code", "text", 'required inputmode="numeric" pattern="[0-9]{6}" maxlength="6" autocomplete="one-time-code" placeholder="123456"');
  const tabs = (m) => `<div class="tabs"><button type="button" data-m="login" class="${m === "login" ? "active" : ""}">Login</button><button type="button" data-m="register" class="${m === "register" ? "active" : ""}">Register</button></div>`;

  async function finish(res) {
    token = res.access_token;
    localStorage.setItem("token", token);
    me = await api("/auth/me");
    toast(`Welcome, ${me.name}`);
    go(me.role === "ADMIN" ? "/admin" : "/report");
  }
  const loginWith = async (mail, password) =>
    finish(await api("/auth/login", { method: "POST", login: true, body: new URLSearchParams({ username: mail, password }) }));

  async function submit(mode, f) {
    if (mode === "login") {
      email = f.get("email").trim();
      try { await loginWith(email, f.get("password")); }
      catch (err) {
        if (err.status === 403) {
          await api("/auth/resend-code", { method: "POST", body: { email } }).catch(() => {});
          return show("verify", "Your email is not verified yet. We sent you a code.");
        }
        throw err;
      }
    } else if (mode === "register") {
      email = f.get("email").trim();
      const user = await api("/auth/register", { method: "POST", body: { name: f.get("name"), email, phone: f.get("phone"), password: f.get("password") } });
      if (user.is_verified) await loginWith(email, f.get("password"));
      else show("verify", "Account created. Check your inbox for the code.");
    } else if (mode === "verify") {
      await finish(await api("/auth/verify-email", { method: "POST", body: { email, code: f.get("code").trim() } }));
    } else if (mode === "forgot") {
      email = f.get("email").trim();
      await api("/auth/forgot-password", { method: "POST", body: { email } });
      show("reset", "If that email has an account, a reset code is on its way.");
    } else if (mode === "reset") {
      await api("/auth/reset-password", { method: "POST", body: { email, code: f.get("code").trim(), new_password: f.get("new_password") } });
      show("login", "Password updated. Please log in.");
    }
  }

  function show(mode, note) {
    const nt = note ? `<div class="notice">${esc(note)}</div>` : "";
    const views = {
      login: `<h2>Welcome back</h2><p class="muted">Sign in to track and manage your reports.</p>${tabs("login")}${nt}
        <form id="f" class="stack">${input("email", "Email or phone number", "text", 'required autocomplete="username" placeholder="you@example.com or 9876543210"')}
        ${pass("password", "Password", "current-password")}
        <button class="primary">Login to your account &rarr;</button>
        <a href="#" data-m="forgot">Forgot password?</a></form>`,
      register: `<h2>Create your account</h2><p class="muted">Use your real email. We send a code to confirm it is yours.</p>${tabs("register")}
        <form id="f" class="stack">${input("name", "Full name", "text", 'required minlength="2" maxlength="60" autocomplete="name"')}
        ${input("email", "Email address", "email", 'required autocomplete="email" placeholder="you@example.com"')}
        ${input("phone", "Mobile number", "tel", 'required pattern="[0-9+ ]{10,15}" autocomplete="tel" placeholder="9876543210"')}
        ${pass("password", "Password (at least 6 characters)", "new-password")}
        <button class="primary">Create account &rarr;</button></form>`,
      verify: `<h2>Verify your email</h2><p class="muted">Enter the 6-digit code sent to <b>${esc(email)}</b>. It is valid for 15 minutes.</p>${nt}
        <form id="f" class="stack">${codeBox}<button class="primary">Verify and continue &rarr;</button>
        <span><a href="#" data-m="resend">Resend code</a> &middot; <a href="#" data-m="login">Back to login</a></span></form>`,
      forgot: `<h2>Forgot password?</h2><p class="muted">Enter your account email and we will send a reset code.</p>
        <form id="f" class="stack">${input("email", "Email address", "email", "required")}
        <button class="primary">Send reset code</button><a href="#" data-m="login">Back to login</a></form>`,
      reset: `<h2>Set a new password</h2><p class="muted">Enter the code from your email and choose a new password.</p>${nt}
        <form id="f" class="stack">${codeBox}${pass("new_password", "New password", "new-password")}
        <button class="primary">Update password</button><a href="#" data-m="login">Back to login</a></form>`,
    };
    box.innerHTML = views[mode];
    box.querySelectorAll("[data-m]").forEach((el) => (el.onclick = async (e) => {
      e.preventDefault();
      if (el.dataset.m === "resend") {
        try { await api("/auth/resend-code", { method: "POST", body: { email } }); toast("If a new code was due, it has been sent"); }
        catch (err) { toast(err.message, true); }
      } else show(el.dataset.m);
    }));
    $("#f").onsubmit = async (e) => {
      e.preventDefault();
      try { await submit(mode, new FormData(e.target)); } catch (err) { toast(err.message, true); }
    };
  }
  show("login");
}

/* ---------- public map ---------- */
async function viewMap() {
  view().innerHTML = `<h2>Public complaint map</h2><div id="pmap" class="map tall"></div>
    <div class="legend">${STATUSES.map((s) => `<span><i style="--c:${SCOLOR[s]}"></i>${label(s)}</span>`).join("")}</div>`;
  newMap("pmap");
  const rows = await api("/complaints/public?limit=200");
  rows.forEach((c) => {
    const support = me && me.role === "CITIZEN" && c.status !== "RESOLVED"
      ? `<br><button class="small" data-support="${c.id}">I also face this</button>` : "";
    dot(c).addTo(map).bindPopup(
      `<b>${esc(c.title)}</b><br>${badge(c.status)} ${pbadge(c.priority)}<br>${label(c.category)} &middot; ${c.supporters_count} supporter(s)${support}`);
  });
  if (rows.length) map.fitBounds(rows.map((c) => [c.lat, c.lng]), { padding: [30, 30], maxZoom: 16 });
}

/* ---------- citizen: report ---------- */
function viewReport() {
  view().innerHTML = `
    <h2>Report a problem</h2>
    <form id="rf" class="card grid">
      <label>Title<input name="title" required minlength="5" maxlength="120" placeholder="e.g. Deep pothole near bus stop"></label>
      <label>Category<select name="category">${options(CATS)}</select></label>
      <label class="full">Description<textarea name="description" rows="4" required minlength="10" maxlength="2000" placeholder="What is wrong, and how bad is it?"></textarea></label>
      <div class="full">
        <div class="row"><strong>Location</strong><button type="button" id="loc" class="small">Use my location</button></div>
        <div id="pick" class="map"></div>
        <small id="coords">Click the map to drop a pin.</small>
      </div>
      <label class="full">Address or landmark (optional)<input name="address" maxlength="255"></label>
      <label class="full">Photos (up to 3, max 5 MB each)<input type="file" name="photos" accept="image/jpeg,image/png,image/webp" multiple></label>
      <div id="dup" class="full"></div>
      <button class="primary full" id="sub">Submit complaint</button>
    </form>`;
  newMap("pick");
  const f = $("#rf");
  let pos = null, marker = null, timer = null, matches = [], supported = false;

  function setPos(lat, lng) {
    pos = { lat, lng };
    if (marker) marker.setLatLng([lat, lng]); else marker = L.marker([lat, lng]).addTo(map);
    $("#coords").textContent = `Pin at ${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    schedule();
  }
  map.on("click", (e) => setPos(e.latlng.lat, e.latlng.lng));
  $("#loc").onclick = () => {
    if (!navigator.geolocation) return toast("Geolocation is not supported by this browser", true);
    navigator.geolocation.getCurrentPosition(
      (p) => { map.setView([p.coords.latitude, p.coords.longitude], 17); setPos(p.coords.latitude, p.coords.longitude); },
      () => toast("Could not get your location. Click the map instead.", true));
  };

  function schedule() { clearTimeout(timer); timer = setTimeout(checkDup, 600); }
  ["title", "description", "category"].forEach((n) => f.elements[n].addEventListener("input", schedule));

  async function checkDup() {
    const box = $("#dup");
    const title = f.elements.title.value.trim(), description = f.elements.description.value.trim();
    if (!pos || title.length < 5 || description.length < 10) { matches = []; box.innerHTML = ""; return; }
    try {
      matches = await api("/complaints/check-duplicate", {
        method: "POST", body: { category: f.elements.category.value, lat: pos.lat, lng: pos.lng, title, description } });
    } catch (e) { return; }
    box.innerHTML = matches.length
      ? `<div class="notice"><strong>Similar complaints nearby.</strong> If one of these is the same problem, support it instead of filing a new report.</div>` +
        matches.map((m) => `<div class="match ${m.level === "LIKELY" ? "likely" : ""}">
          <div class="row"><b>#${m.id} ${esc(m.title)}</b><span>${Math.round(m.confidence * 100)}% match</span></div>
          <small>${m.level === "LIKELY" ? "Likely duplicate" : "Possible duplicate"} &middot; ${m.distance_m} m away &middot; ${badge(m.status)} &middot; ${m.supporters_count} supporter(s)</small><br>
          <button type="button" class="small" data-support="${m.id}">I also face this</button></div>`).join("")
      : "";
  }
  document.addEventListener("supported", () => { supported = true; }, { once: true });

  f.onsubmit = async (e) => {
    e.preventDefault();
    if (!pos) return toast("Please click the map to mark the location", true);
    if (matches.some((m) => m.level === "LIKELY") && !supported &&
        !confirm("A very similar complaint already exists nearby. Submit a new one anyway?")) return;
    const files = [...f.elements.photos.files];
    if (files.length > 3) return toast("You can upload at most 3 photos", true);
    const fd = new FormData();
    fd.append("title", f.elements.title.value.trim());
    fd.append("description", f.elements.description.value.trim());
    fd.append("category", f.elements.category.value);
    fd.append("lat", pos.lat); fd.append("lng", pos.lng);
    if (f.elements.address.value.trim()) fd.append("address", f.elements.address.value.trim());
    files.forEach((p) => fd.append("photos", p));
    $("#sub").disabled = true;
    try {
      const c = await api("/complaints", { method: "POST", body: fd });
      toast("Complaint submitted");
      go(`/mine/${c.id}`);
    } catch (err) { toast(err.message, true); $("#sub").disabled = false; }
  };
}

/* ---------- citizen: my complaints ---------- */
async function viewMine() {
  const rows = await api("/complaints/mine");
  view().innerHTML = `<h2>My complaints</h2>` + (rows.length
    ? rows.map((c) => `<a class="card list-item" href="#/mine/${c.id}">
        <div class="row"><b>#${c.id} ${esc(c.title)}</b>${badge(c.status)}</div>
        <small>${label(c.category)} &middot; ${fmt(c.created_at)} &middot; ${c.supporters_count} supporter(s)</small></a>`).join("")
    : `<div class="card">You haven't reported anything yet. <a href="#/report">Report a problem</a></div>`);
}

function timelineHtml(list) {
  return `<ul class="timeline">${list.map((t) => `<li>${badge(t.new_status)}
    <small>${fmt(t.changed_at)}</small>${t.remarks ? `<div>${esc(t.remarks)}</div>` : ""}</li>`).join("")}</ul>`;
}
function photosHtml(list) {
  return list.length ? `<div class="photos">${list.map((p) => `<a href="${p.url}" target="_blank" rel="noopener"><img src="${p.url}" alt="Complaint photo"></a>`).join("")}</div>` : "";
}

async function viewMineDetail(id) {
  const c = await api(`/complaints/${id}`);
  const canEdit = c.status === "SUBMITTED";
  const canWithdraw = ["SUBMITTED", "VERIFIED", "REOPENED"].includes(c.status);
  view().innerHTML = `<p><a href="#/mine">&larr; My complaints</a></p>
    <div class="card">
      <div class="row"><h2 style="margin:0">#${c.id} ${esc(c.title)}</h2>${badge(c.status)}</div>
      <p>${esc(c.description)}</p>
      <small>${label(c.category)} &middot; reported ${fmt(c.created_at)} &middot; ${c.supporters_count} supporter(s)${c.address ? " &middot; " + esc(c.address) : ""}</small>
      ${photosHtml(c.photos)}
      ${canEdit || canWithdraw ? `<p>${canEdit ? `<button id="edit">Edit report</button> ` : ""}${canWithdraw ? `<button id="wd" class="danger">Withdraw report</button>` : ""}</p>` : ""}
    </div>
    <form id="ef" class="card grid" hidden>
      <h3 class="full">Edit your report</h3>
      <label>Title<input name="title" required minlength="5" maxlength="120" value="${esc(c.title)}"></label>
      <label>Category<select name="category">${options(CATS, c.category)}</select></label>
      <label class="full">Description<textarea name="description" rows="4" required minlength="10" maxlength="2000">${esc(c.description)}</textarea></label>
      <label class="full">Address or landmark<input name="address" maxlength="255" value="${esc(c.address || "")}"></label>
      <div class="full"><button class="primary">Save changes</button> <button type="button" id="ec">Cancel</button></div>
    </form>
    <div class="card"><h3>Progress</h3>${timelineHtml(c.timeline)}</div>
    <div id="rp"></div>
    <div id="dmap" class="map"></div>`;
  newMap("dmap", [c.lat, c.lng], 17);
  dot(c).addTo(map);
  if (canEdit) {
    $("#edit").onclick = () => { $("#ef").hidden = false; $("#ef").scrollIntoView({ behavior: "smooth" }); };
    $("#ec").onclick = () => ($("#ef").hidden = true);
    $("#ef").onsubmit = async (e) => {
      e.preventDefault();
      const f = e.target.elements;
      try {
        await api(`/complaints/${id}`, { method: "PATCH", body: { title: f.title.value, description: f.description.value, category: f.category.value, address: f.address.value } });
        toast("Report updated"); route();
      } catch (err) { toast(err.message, true); }
    };
  }
  if (canWithdraw) {
    $("#wd").onclick = async () => {
      if (!confirm("Withdraw this report? It will be removed from the public map and the work queue.")) return;
      try { await api(`/complaints/${id}/withdraw`, { method: "POST" }); toast("Report withdrawn"); go("/mine"); }
      catch (err) { toast(err.message, true); }
    };
  }
  if (c.status === "RESOLVED") {
    $("#rp").innerHTML = `<form id="rof" class="card"><h3>Not actually fixed?</h3>
      <label>Tell us what is still wrong<textarea name="reason" required minlength="5" maxlength="500" rows="3"></textarea></label>
      <p><button class="danger">Reopen complaint</button></p></form>`;
    $("#rof").onsubmit = async (e) => {
      e.preventDefault();
      try {
        await api(`/complaints/${id}/reopen`, { method: "POST", body: { reason: e.target.reason.value } });
        toast("Complaint reopened"); route();
      } catch (err) { toast(err.message, true); }
    };
  }
}

/* ---------- admin: dashboard ---------- */
function bars(obj, colors) {
  const entries = Object.entries(obj);
  if (!entries.length) return `<p class="muted">No data yet.</p>`;
  const max = Math.max(...entries.map(([, v]) => v));
  return `<div class="bars">${entries.map(([k, v]) => `<div class="bar"><span>${esc(label(k))}</span>
    <div><div class="fill" style="width:${(v / max) * 100}%;${colors && colors[k] ? "background:" + colors[k] : ""}"></div></div><b>${v}</b></div>`).join("")}</div>`;
}

async function viewDashboard() {
  const s = await api("/admin/stats");
  view().innerHTML = `<div class="row"><h2>Dashboard</h2><span><button id="rc">Recalculate priorities</button> <button id="pg" class="danger">Clear old resolved records</button></span></div>
    <div class="stats">
      <div class="stat"><b>${s.total}</b>Total complaints</div>
      <div class="stat"><b>${s.open}</b>Open</div>
      <div class="stat"><b style="color:var(--danger)">${s.overdue}</b>Overdue (past SLA)</div>
      <div class="stat"><b>${s.resolved}</b>Resolved (${s.resolution_rate}%)</div>
      <div class="stat"><b>${s.merged_duplicates}</b>Duplicates merged</div>
    </div>
    <div class="grid">
      <div class="card"><h3>By status</h3>${bars(s.by_status, SCOLOR)}</div>
      <div class="card"><h3>By priority</h3>${bars(s.by_priority, PCOLOR)}</div>
      <div class="card"><h3>By category</h3>${bars(s.by_category)}</div>
      <div class="card"><h3>By department</h3>${bars(s.by_department)}</div>
    </div>
    <p><a href="#/admin/complaints">Open the complaints list &rarr;</a></p>`;
  $("#pg").onclick = async () => {
    const days = prompt("Delete resolved complaints older than how many days? (0 = all resolved)", "0");
    if (days === null) return;
    try {
      const q = `/admin/purge?older_than_days=${encodeURIComponent(days)}`;
      const preview = await api(q, { method: "DELETE" });
      if (!preview.would_delete) return toast("Nothing to delete");
      if (!confirm(`Permanently delete ${preview.would_delete} resolved complaint(s) with their photos and history? This cannot be undone.`)) return;
      const r = await api(q + "&confirm=true", { method: "DELETE" });
      toast(`Deleted ${r.deleted} complaint(s)`); route();
    } catch (e) { toast(e.message, true); }
  };
  $("#rc").onclick = async () => {
    try { const r = await api("/admin/recalculate", { method: "POST" }); toast(`Recalculated ${r.recalculated} complaints`); route(); }
    catch (e) { toast(e.message, true); }
  };
}

/* ---------- admin: list ---------- */
async function viewAdminList() {
  const depts = await api("/admin/departments");
  view().innerHTML = `<h2>Complaints</h2>
    <form id="ff" class="card filters">
      <label>Search title<input name="q" placeholder="pothole..."></label>
      <label>Status<select name="status"><option value="">All</option>${options(STATUSES)}</select></label>
      <label>Category<select name="category"><option value="">All</option>${options(CATS)}</select></label>
      <label>Priority<select name="priority"><option value="">All</option>${options(PRIOS)}</select></label>
      <label>Department<select name="department_id"><option value="">All</option>${depts.map((d) => `<option value="${d.id}">${esc(d.name)}</option>`).join("")}</select></label>
      <label>Sort<select name="sort"><option value="newest">Newest first</option><option value="score">Highest priority score</option></select></label>
      <button class="primary">Apply</button>
    </form>
    <div class="card table-wrap" id="tbl"></div>`;
  async function load() {
    const p = new URLSearchParams();
    new FormData($("#ff")).forEach((v, k) => { if (v) p.set(k, v); });
    const rows = await api("/admin/complaints?" + p.toString());
    $("#tbl").innerHTML = rows.length
      ? `<table><thead><tr><th>#</th><th>Title</th><th>Category</th><th>Status</th><th>Priority</th><th>Department</th><th>Reports</th></tr></thead><tbody>` +
        rows.map((c) => `<tr class="click" data-open="${c.id}"><td>${c.id}</td>
          <td>${esc(c.title)} ${c.is_overdue ? `<span class="flag">OVERDUE</span>` : ""}</td><td>${label(c.category)}</td>
          <td>${badge(c.status)}</td><td>${pbadge(c.priority)} <small>${c.priority_score}${c.priority_manual ? " (manual)" : ""}</small></td>
          <td>${esc(c.department_name || "-")}</td><td>${1 + c.duplicates_count} + ${c.supporters_count} supporters</td></tr>`).join("") + `</tbody></table>`
      : `<p class="muted">No complaints match these filters.</p>`;
  }
  $("#ff").onsubmit = (e) => { e.preventDefault(); load().catch((err) => toast(err.message, true)); };
  await load();
}

/* ---------- admin: detail ---------- */
async function viewAdminDetail(id) {
  const [c, d, depts, dups, prio] = await Promise.all([
    api(`/admin/complaints/${id}`), api(`/complaints/${id}`), api("/admin/departments"),
    api(`/admin/complaints/${id}/duplicates`), api(`/admin/complaints/${id}/priority`)]);
  const similar = c.master_complaint_id ? [] : await api(`/admin/complaints/${id}/similar`);
  const isDup = !!c.master_complaint_id;
  const nextOptions = c.status === "WITHDRAWN" ? [c.status] : STATUSES.filter((x) => x !== "WITHDRAWN");

  view().innerHTML = `<p><a href="#/admin/complaints">&larr; All complaints</a></p>
    <div class="card">
      <div class="row"><h2 style="margin:0">#${c.id} ${esc(c.title)}</h2><span>${badge(c.status)} ${pbadge(c.priority)}</span></div>
      <p>${esc(c.description)}</p>
      <small>${label(c.category)} &middot; by ${esc(c.citizen_name || "?")} &middot; ${fmt(c.created_at)} &middot; ${c.supporters_count} supporter(s) &middot; ${c.duplicates_count} merged duplicate(s)
      ${c.is_overdue ? ` &middot; <span class="flag">OVERDUE</span>` : ""}${c.address ? " &middot; " + esc(c.address) : ""}</small>
      ${photosHtml(d.photos)}
    </div>
    ${isDup ? `<div class="notice">This is a duplicate of <a href="#/admin/complaint/${c.master_complaint_id}">#${c.master_complaint_id}</a>. Update the main complaint instead.
      <button class="small" id="unmerge">Separate it</button></div>` : `
    <form id="af" class="card grid">
      <h3 class="full">Update complaint</h3>
      <label>Status<select name="status">${options(nextOptions, c.status)}</select></label>
      <label>Department<select name="department_id"><option value="">${c.department_name ? "Keep: " + esc(c.department_name) : "Not assigned"}</option>${depts.map((x) => `<option value="${x.id}">${esc(x.name)}</option>`).join("")}</select></label>
      <label>Priority<select name="priority"><option value="">Keep (${label(c.priority)}${c.priority_manual ? ", manual" : ", automatic"})</option><option value="AUTO">Automatic (use score)</option>${options(PRIOS)}</select></label>
      <label>Category<select name="category">${options(CATS, c.category)}</select></label>
      <label class="full">Remarks (required for Resolved / Rejected)<textarea name="remarks" rows="2" maxlength="500"></textarea></label>
      <button class="primary full">Save changes</button>
    </form>`}
    <div class="grid">
      <div class="card"><h3>Why this priority? (score ${prio.score})</h3>
        <table><tbody>${prio.components.map((p) => `<tr><td>${esc(p.label)}</td><td><small>${esc(p.detail)}</small></td><td><b>+${p.points}</b></td></tr>`).join("")}</tbody></table>
        <small>LOW &lt; 30 &le; MEDIUM &lt; 50 &le; HIGH &lt; 70 &le; CRITICAL</small></div>
      <div class="card"><h3>Progress</h3>${timelineHtml(d.timeline)}</div>
    </div>
    ${isDup ? "" : `<div class="card"><h3>Possible duplicates nearby</h3>${similar.length ? similar.map((m) => `<div class="match ${m.level === "LIKELY" ? "likely" : ""}">
      <div class="row"><b>#${m.id} ${esc(m.title)}</b><span>${Math.round(m.confidence * 100)}% &middot; ${m.distance_m} m</span></div>
      <small>${m.level === "LIKELY" ? "Likely" : "Possible"} duplicate &middot; ${badge(m.status)}</small><br>
      <button class="small" data-merge-into="${m.id}">Merge this into #${m.id}</button>
      <button class="small" data-absorb="${m.id}">Merge #${m.id} into this</button></div>`).join("") : `<p class="muted">Nothing similar found nearby.</p>`}</div>`}
    ${dups.length ? `<div class="card"><h3>Merged duplicates (${dups.length})</h3>${dups.map((x) => `<div class="row"><span>#${x.id} ${esc(x.title)} <small>by ${esc(x.citizen_name || "?")}</small></span>
      <button class="small" data-unmerge="${x.id}">Separate</button></div>`).join("")}</div>` : ""}
    <div id="dmap" class="map"></div>`;
  newMap("dmap", [c.lat, c.lng], 17);
  dot(c).addTo(map);

  const act = async (path, body, msg) => {
    try { await api(path, { method: "POST", body }); toast(msg); route(); } catch (e) { toast(e.message, true); }
  };
  view().querySelectorAll("[data-merge-into]").forEach((b) => (b.onclick = () => act(`/admin/complaints/${id}/merge`, { master_id: +b.dataset.mergeInto }, "Merged")));
  view().querySelectorAll("[data-absorb]").forEach((b) => (b.onclick = () => act(`/admin/complaints/${b.dataset.absorb}/merge`, { master_id: +id }, "Merged")));
  view().querySelectorAll("[data-unmerge]").forEach((b) => (b.onclick = () => act(`/admin/complaints/${b.dataset.unmerge}/unmerge`, null, "Separated")));
  const um = $("#unmerge");
  if (um) um.onclick = () => act(`/admin/complaints/${id}/unmerge`, null, "Separated");

  const af = $("#af");
  if (af) af.onsubmit = async (e) => {
    e.preventDefault();
    const f = af.elements, body = {};
    if (f.status.value !== c.status) body.status = f.status.value;
    if (f.category.value !== c.category) body.category = f.category.value;
    if (f.department_id.value) body.department_id = +f.department_id.value;
    if (f.priority.value === "AUTO") body.auto_priority = true;
    else if (f.priority.value) body.priority = f.priority.value;
    if (f.remarks.value.trim()) body.remarks = f.remarks.value.trim();
    try { await api(`/admin/complaints/${id}`, { method: "PATCH", body }); toast("Saved"); route(); }
    catch (err) { toast(err.message, true); }
  };
}

/* ---------- notifications ---------- */
async function refreshBell() {
  const el = $("#bell");
  if (!el || !me) return;
  try {
    const r = await api("/notifications/unread-count");
    el.innerHTML = r.unread ? `<span class="badge" style="--c:#dc2626">${r.unread}</span>` : "";
  } catch (e) { /* ignore */ }
}
setInterval(refreshBell, 30000);

async function viewNotifications() {
  const rows = await api("/notifications");
  const link = (n) => !n.complaint_id ? "#/notifications"
    : me.role === "ADMIN" ? `#/admin/complaint/${n.complaint_id}` : `#/mine/${n.complaint_id}`;
  view().innerHTML = `<div class="row"><h2>Notifications</h2><button id="ra">Mark all as read</button></div>` +
    (rows.length ? rows.map((n) => `<a class="card list-item" href="${link(n)}" data-read="${n.id}"
      style="${n.is_read ? "" : "border-left:4px solid var(--brand)"}"><div class="row">
      <span>${n.is_read ? esc(n.message) : "<b>" + esc(n.message) + "</b>"}</span><small>${fmt(n.created_at)}</small></div></a>`).join("")
      : `<div class="card">No notifications yet.</div>`);
  $("#ra").onclick = async () => {
    try { await api("/notifications/read-all", { method: "POST" }); toast("All marked as read"); route(); }
    catch (e) { toast(e.message, true); }
  };
}

/* ---------- global click handling ---------- */
document.addEventListener("click", async (e) => {
  const rd = e.target.closest("[data-read]");
  if (rd) api(`/notifications/${rd.dataset.read}/read`, { method: "POST" }).then(refreshBell).catch(() => {});
  const open = e.target.closest("[data-open]");
  if (open) return go(`/admin/complaint/${open.dataset.open}`);
  const sup = e.target.closest("[data-support]");
  if (sup) {
    sup.disabled = true;
    try {
      await api(`/complaints/${sup.dataset.support}/support`, { method: "POST" });
      sup.textContent = "Supported ✓";
      toast("Thanks, your support was added");
      document.dispatchEvent(new Event("supported"));
    } catch (err) { toast(err.message, true); sup.disabled = false; }
  }
});

window.addEventListener("hashchange", route);
(async function init() {
  await ensureLeaflet();
  if (token) {
    try { me = await api("/auth/me"); } catch (e) { token = null; localStorage.removeItem("token"); }
  }
  renderFooter();
  route();
})();

async function viewCommunity() {
  const rows = (await api("/complaints/public?limit=200")).sort((a, b) => b.supporters_count - a.supporters_count);
  view().innerHTML = `<h2>Community issues</h2><p class="muted">See problems reported around the city. If you face the same one, tap <b>I also face this</b>. More supporters means a higher priority.</p>` +
    (rows.length ? rows.map((c) => `<div class="card"><div class="row"><b>#${c.id} ${esc(c.title)}</b>${badge(c.status)}</div>
      <small>${label(c.category)} &middot; ${fmt(c.created_at)} &middot; ${c.supporters_count} supporter(s)</small>
      <p><button class="small primary" data-support="${c.id}" ${c.status === "RESOLVED" ? "disabled" : ""}>&#128077; I also face this</button></p></div>`).join("")
      : `<div class="card">No complaints yet.</div>`);
}

async function viewAdminUsers() {
  const rows = await api("/admin/users");
  view().innerHTML = `<h2>Citizens</h2><p class="muted">Block accounts that file fake or repeated reports. Blocked users cannot log in. Red numbers mean 3 or more.</p>
    <div class="card table-wrap">${rows.length ? `<table><thead><tr><th>Name</th><th>Contact</th><th>Reports</th><th>Rejected</th><th>Duplicates</th><th>Status</th><th></th></tr></thead><tbody>` +
    rows.map((u) => `<tr><td>${esc(u.name)}</td><td>${esc(u.email)}<br><small>${esc(u.phone || "")}</small></td><td>${u.reports}</td>
      <td>${u.rejected >= 3 ? `<span class="flag">${u.rejected}</span>` : u.rejected}</td>
      <td>${u.duplicates >= 3 ? `<span class="flag">${u.duplicates}</span>` : u.duplicates}</td>
      <td>${u.is_blocked ? `<span class="badge" style="--c:#dc2626">Blocked</span><br><small>${esc(u.blocked_reason || "")}</small>` : `<span class="badge" style="--c:#16a34a">Active</span>`}</td>
      <td>${u.is_blocked ? `<button class="small" data-unblock="${u.id}">Unblock</button>` : `<button class="small danger" data-block="${u.id}">Block</button>`}</td></tr>`).join("") +
    `</tbody></table>` : `<p class="muted">No citizens yet.</p>`}</div>`;
  const act = async (path, body, msg) => { try { await api(path, { method: "POST", body }); toast(msg); route(); } catch (e) { toast(e.message, true); } };
  view().querySelectorAll("[data-block]").forEach((b) => (b.onclick = () => {
    const reason = prompt("Reason for blocking (shown to the user):", "Fake or repeated reports");
    if (reason !== null) act(`/admin/users/${b.dataset.block}/block`, { reason }, "User blocked");
  }));
  view().querySelectorAll("[data-unblock]").forEach((b) => (b.onclick = () => act(`/admin/users/${b.dataset.unblock}/unblock`, null, "User unblocked")));
}