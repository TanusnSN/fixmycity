"use strict";

/* ---------- helpers ---------- */
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (s) => (s ? new Date(s + "Z").toLocaleString() : "");
const label = (s) => String(s).replace(/_/g, " ").toLowerCase().replace(/^./, (c) => c.toUpperCase());

const CATS = ["ROAD", "STREETLIGHT", "WATER_LEAKAGE", "DRAINAGE", "OTHER"];
const STATUSES = ["SUBMITTED", "VERIFIED", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "REJECTED", "REOPENED"];
const PRIOS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const NEXT = {
  SUBMITTED: ["VERIFIED", "REJECTED"], VERIFIED: ["ASSIGNED", "REJECTED"],
  ASSIGNED: ["IN_PROGRESS", "VERIFIED"], IN_PROGRESS: ["RESOLVED", "ASSIGNED"],
  RESOLVED: [], REJECTED: ["VERIFIED"], REOPENED: ["VERIFIED", "ASSIGNED", "IN_PROGRESS"],
};
const SCOLOR = { SUBMITTED: "#6b7280", VERIFIED: "#2563eb", ASSIGNED: "#7c3aed", IN_PROGRESS: "#d97706", RESOLVED: "#16a34a", REJECTED: "#dc2626", REOPENED: "#db2777" };
const PCOLOR = { LOW: "#16a34a", MEDIUM: "#d97706", HIGH: "#ea580c", CRITICAL: "#dc2626" };
const badge = (s) => `<span class="badge" style="--c:${SCOLOR[s]}">${label(s)}</span>`;
const pbadge = (p) => `<span class="badge" style="--c:${PCOLOR[p]}">${label(p)}</span>`;
const options = (list, sel) => list.map((o) => `<option value="${o}" ${o === sel ? "selected" : ""}>${label(o)}</option>`).join("");

let token = localStorage.getItem("token");
let me = null;
let map = null;
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
    throw new Error(msg || `Request failed (${res.status})`);
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
  const links = [`<a class="link" href="#/map">Public map</a>`];
  if (me && me.role === "CITIZEN") links.push(`<a class="link" href="#/report">Report</a>`, `<a class="link" href="#/mine">My complaints</a>`);
  if (me && me.role === "ADMIN") links.push(`<a class="link" href="#/admin">Dashboard</a>`, `<a class="link" href="#/admin/complaints">Complaints</a>`);
  $("#nav").innerHTML =
    `<a class="brand" href="#/map">FixMyCity</a>${links.join("")}<span class="spacer"></span>` +
    (me
      ? `<span class="muted">${esc(me.name)} (${label(me.role)})</span><button class="small" id="logout">Log out</button>`
      : `<a class="link" href="#/login">Log in</a>`);
  const lo = $("#logout");
  if (lo) lo.onclick = () => logout();
}

async function route() {
  const h = location.hash.slice(1) || (me ? (me.role === "ADMIN" ? "/admin" : "/report") : "/map");
  const [a, b, c] = h.split("/").filter(Boolean);
  if (map) { map.remove(); map = null; }
  renderNav();
  try {
    if (a === "login") return viewLogin();
    if (a === "map") return await viewMap();
    if (!me) return go("/login");
    if (a === "report" && me.role === "CITIZEN") return viewReport();
    if (a === "mine" && me.role === "CITIZEN") return b ? await viewMineDetail(b) : await viewMine();
    if (a === "admin" && me.role === "ADMIN") {
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
  view().innerHTML = `
    <div class="card" style="max-width:440px;margin:30px auto">
      <div class="tabs"><button id="tl" class="active">Log in</button><button id="tr">Register</button></div>
      <form id="f" class="grid" style="grid-template-columns:1fr">
        <label id="nm" hidden>Full name<input name="name" minlength="2" maxlength="60" autocomplete="name"></label>
        <label>Email<input name="email" type="email" required autocomplete="email"></label>
        <label>Password<input name="password" type="password" required minlength="6" maxlength="72" autocomplete="current-password"></label>
        <button class="primary" id="go">Log in</button>
      </form>
    </div>`;
  let mode = "login";
  const setMode = (m) => {
    mode = m;
    $("#tl").classList.toggle("active", m === "login");
    $("#tr").classList.toggle("active", m === "register");
    $("#nm").hidden = m === "login";
    $("#go").textContent = m === "login" ? "Log in" : "Create account";
  };
  $("#tl").onclick = () => setMode("login");
  $("#tr").onclick = () => setMode("register");
  $("#f").onsubmit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    const email = f.get("email"), password = f.get("password");
    try {
      if (mode === "register") await api("/auth/register", { method: "POST", body: { name: f.get("name"), email, password } });
      const res = await api("/auth/login", { method: "POST", login: true, body: new URLSearchParams({ username: email, password }) });
      token = res.access_token;
      localStorage.setItem("token", token);
      me = await api("/auth/me");
      toast(`Welcome, ${me.name}`);
      go(me.role === "ADMIN" ? "/admin" : "/report");
    } catch (err) { toast(err.message, true); }
  };
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
  view().innerHTML = `<p><a href="#/mine">&larr; My complaints</a></p>
    <div class="card">
      <div class="row"><h2 style="margin:0">#${c.id} ${esc(c.title)}</h2>${badge(c.status)}</div>
      <p>${esc(c.description)}</p>
      <small>${label(c.category)} &middot; reported ${fmt(c.created_at)} &middot; ${c.supporters_count} supporter(s)${c.address ? " &middot; " + esc(c.address) : ""}</small>
      ${photosHtml(c.photos)}
    </div>
    <div class="card"><h3>Progress</h3>${timelineHtml(c.timeline)}</div>
    <div id="rp"></div>
    <div id="dmap" class="map"></div>`;
  newMap("dmap", [c.lat, c.lng], 17);
  dot(c).addTo(map);
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
  view().innerHTML = `<div class="row"><h2>Dashboard</h2><button id="rc">Recalculate priorities</button></div>
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
  const nextOptions = [c.status, ...NEXT[c.status]];

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

/* ---------- global click handling ---------- */
document.addEventListener("click", async (e) => {
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
  if (token) {
    try { me = await api("/auth/me"); } catch (e) { token = null; localStorage.removeItem("token"); }
  }
  route();
})();
