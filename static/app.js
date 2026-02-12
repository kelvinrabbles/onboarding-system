/* ===================================================================
   Solutions PM — SPA Application
   =================================================================== */

// ── API helper ─────────────────────────────────────────────────────
const api = {
  async get(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error((await r.json()).error || r.statusText);
    return r.json();
  },
  async post(url, body) {
    const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || r.statusText);
    return data;
  },
  async put(url, body) {
    const r = await fetch(url, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || r.statusText);
    return data;
  }
};

// ── Toasts ─────────────────────────────────────────────────────────
function toast(msg, type = "success") {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  document.getElementById("toastContainer").appendChild(el);
  setTimeout(() => el.remove(), 3800);
}

// ── Helpers ────────────────────────────────────────────────────────
function fmtDate(d) {
  if (!d) return "—";
  if (d.length <= 10 && d.includes("-")) {
    const [y, m, day] = d.split("-");
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${months[+m - 1]} ${+day}, ${y}`;
  }
  return d;
}

function fmtRate(v) {
  if (!v) return "—";
  v = String(v).replace(/[$,]/g, "");
  const n = parseFloat(v);
  return isNaN(n) ? v : `$${n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}/hr`;
}

function initials(name) {
  return name.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2);
}

function badge(status) {
  if (!status) status = "Pending";
  const s = status.toLowerCase();
  let cls = "badge-pending";
  if (s.includes("complete")) cls = "badge-complete";
  else if (s.includes("progress")) cls = "badge-progress";
  else if (s === "sent") cls = "badge-sent";
  else if (s === "generated") cls = "badge-generated";
  return `<span class="badge ${cls}">${status}</span>`;
}

function activityIcon(type) {
  const t = type.toLowerCase();
  if (t.includes("email") || t.includes("reminder")) return "📧";
  if (t.includes("document")) return "📄";
  if (t.includes("complete")) return "✅";
  if (t.includes("status")) return "🔄";
  return "👤";
}

function fmtTimeAgo(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const mins = Math.floor((now - d) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

// ── Router ─────────────────────────────────────────────────────────
let currentPage = "dashboard";
let currentDetail = null;

function navigate(page, detail) {
  currentPage = page;
  currentDetail = detail || null;

  // Update nav
  document.querySelectorAll(".nav-item").forEach(n => n.classList.toggle("active", n.dataset.page === page));

  // Show page
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  const target = page === "detail" ? "page-detail" : page === "new" ? "page-new" : `page-${page}`;
  const el = document.getElementById(target);
  if (el) el.classList.add("active");

  // Close mobile sidebar
  document.getElementById("sidebar").classList.remove("open");

  // Render
  render();
}

async function render() {
  try {
    switch (currentPage) {
      case "dashboard": await renderDashboard(); break;
      case "consultants": await renderConsultants(); break;
      case "detail": await renderDetail(currentDetail); break;
      case "new": renderNewForm(); break;
      case "emails": await renderEmails(); break;
      case "reports": await renderReports(); break;
    }
  } catch (err) {
    toast(err.message, "error");
  }
}

// ── Sidebar stats ──────────────────────────────────────────────────
async function refreshSidebarStats() {
  try {
    const s = await api.get("/api/summary");
    document.getElementById("sidebarStats").innerHTML = `
      <div class="stat-row"><span>Total</span><span class="stat-val">${s.total}</span></div>
      <div class="stat-row"><span>Pending</span><span class="stat-val">${s.pending}</span></div>
      <div class="stat-row"><span>In Progress</span><span class="stat-val">${s.in_progress}</span></div>
      <div class="stat-row"><span>Complete</span><span class="stat-val">${s.complete}</span></div>
    `;
  } catch (e) { /* silent */ }
}

// ── Dashboard ──────────────────────────────────────────────────────
async function renderDashboard() {
  const [summary, consultants] = await Promise.all([
    api.get("/api/summary"),
    api.get("/api/consultants")
  ]);

  const el = document.getElementById("page-dashboard");
  el.innerHTML = `
    <div class="page-header">
      <div>
        <h1>Dashboard</h1>
        <div class="sub">Welcome back, Kelvin</div>
      </div>
      <button class="btn btn-primary" onclick="navigate('new')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        New Onboarding
      </button>
    </div>

    <div class="metrics-grid">
      <div class="metric-card brand">
        <div class="metric-label">Total Consultants</div>
        <div class="metric-value">${summary.total}</div>
        <div class="metric-icon">👥</div>
      </div>
      <div class="metric-card amber">
        <div class="metric-label">Pending</div>
        <div class="metric-value">${summary.pending}</div>
        <div class="metric-icon">⏳</div>
      </div>
      <div class="metric-card blue">
        <div class="metric-label">In Progress</div>
        <div class="metric-value">${summary.in_progress}</div>
        <div class="metric-icon">🔄</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">Complete</div>
        <div class="metric-value">${summary.complete}</div>
        <div class="metric-icon">✅</div>
      </div>
    </div>

    <div class="two-col">
      <div class="card">
        <div class="card-header">
          <div class="card-title">Recent Consultants</div>
          <button class="btn btn-ghost btn-sm" onclick="navigate('consultants')">View All →</button>
        </div>
        ${consultants.length ? consultants.slice(0, 5).map(c => `
          <div class="consultant-row" onclick="navigate('detail', ${c.id})" style="cursor:pointer">
            <div>
              <div class="consultant-name">${c.name}</div>
              <div class="consultant-email">${c.position || ''}</div>
            </div>
            <div class="progress-wrap">
              <div class="progress-bar"><div class="progress-fill" style="width:${c.doc_progress}%"></div></div>
              <div class="progress-text">${c.doc_completed}/${c.doc_total}</div>
            </div>
            <div class="consultant-date">${fmtDate(c.start_date)}</div>
            <div>${badge(c.status)}</div>
            <div><button class="btn btn-ghost btn-sm" onclick="event.stopPropagation();navigate('detail',${c.id})">View</button></div>
          </div>
        `).join('') : `<div class="empty-state"><div class="empty-icon">📋</div><p>No consultants yet. Click <strong>New Onboarding</strong> to get started!</p></div>`}
      </div>

      <div class="card" id="dashActivity">
        <div class="card-header">
          <div class="card-title">Recent Activity</div>
        </div>
        <div class="spinner"></div>
      </div>
    </div>
  `;

  // Load activity feed asynchronously
  loadDashActivity(consultants);
  refreshSidebarStats();
}

async function loadDashActivity(consultants) {
  const container = document.getElementById("dashActivity");
  if (!container) return;

  let allActs = [];
  for (const c of consultants.slice(0, 10)) {
    try {
      const acts = await api.get(`/api/consultants/${c.id}/activities`);
      acts.forEach(a => { a._name = c.name; });
      allActs = allActs.concat(acts.slice(0, 3));
    } catch (e) { /* skip */ }
  }

  allActs.sort((a, b) => (b.timestamp || "").localeCompare(a.timestamp || ""));
  allActs = allActs.slice(0, 8);

  const header = `<div class="card-header"><div class="card-title">Recent Activity</div></div>`;

  if (!allActs.length) {
    container.innerHTML = header + `<div class="empty-state"><div class="empty-icon">📝</div><p>No activity yet</p></div>`;
    return;
  }

  container.innerHTML = header + `
    <div class="activity-list">
      ${allActs.map(a => `
        <div class="activity-item">
          <div class="activity-icon">${activityIcon(a.activity_type)}</div>
          <div class="activity-content">
            <div class="activity-type">${a.activity_type}</div>
            <div class="activity-desc">${a.description || ''}</div>
            <div class="activity-time">${fmtTimeAgo(a.timestamp)}</div>
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

// ── Consultants list ───────────────────────────────────────────────
async function renderConsultants() {
  const consultants = await api.get("/api/consultants");

  const el = document.getElementById("page-consultants");
  el.innerHTML = `
    <div class="page-header">
      <div>
        <h1>Consultants</h1>
        <div class="sub">Manage all consultant onboarding</div>
      </div>
      <button class="btn btn-primary" onclick="navigate('new')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        New Consultant
      </button>
    </div>

    <div class="filters">
      <input type="text" class="search-input" id="searchInput" placeholder="Search by name or position…" oninput="filterConsultants()">
      <select class="filter-select" id="statusFilter" onchange="filterConsultants()">
        <option value="All">All Statuses</option>
        <option value="Pending">Pending</option>
        <option value="In Progress">In Progress</option>
        <option value="Complete">Complete</option>
      </select>
    </div>

    <div class="consultant-list" id="consultantList">
      ${renderConsultantRows(consultants)}
    </div>
  `;

  // Store data for filtering
  window._consultantsData = consultants;
}

function renderConsultantRows(list) {
  if (!list.length) return `<div class="empty-state"><div class="empty-icon">👥</div><p>No consultants found.</p></div>`;

  return list.map(c => `
    <div class="consultant-row" onclick="navigate('detail', ${c.id})">
      <div>
        <div class="consultant-name">${c.name}</div>
        <div class="consultant-email">${c.email}</div>
      </div>
      <div class="consultant-role">${c.position || '—'}</div>
      <div class="consultant-date">${fmtDate(c.start_date)}</div>
      <div class="progress-wrap">
        <div class="progress-bar"><div class="progress-fill" style="width:${c.doc_progress}%"></div></div>
        <div class="progress-text">${c.doc_completed}/${c.doc_total}</div>
      </div>
      <div>${badge(c.status)}</div>
    </div>
  `).join("");
}

function filterConsultants() {
  const q = (document.getElementById("searchInput").value || "").toLowerCase();
  const s = document.getElementById("statusFilter").value;
  let filtered = window._consultantsData || [];

  if (q) filtered = filtered.filter(c => c.name.toLowerCase().includes(q) || (c.position || "").toLowerCase().includes(q));
  if (s !== "All") filtered = filtered.filter(c => c.status === s);

  document.getElementById("consultantList").innerHTML = renderConsultantRows(filtered);
}

// ── Consultant detail ──────────────────────────────────────────────
async function renderDetail(id) {
  const el = document.getElementById("page-detail");
  el.innerHTML = `<div class="spinner"></div>`;

  const data = await api.get(`/api/consultants/${id}`);
  const c = data.consultant;

  el.innerHTML = `
    <a href="#" class="back-link" onclick="event.preventDefault();navigate('consultants')">← Back to Consultants</a>

    <div class="detail-header">
      <div class="detail-avatar">${initials(c.name)}</div>
      <div class="detail-info">
        <div class="detail-name">${c.name}</div>
        <div class="detail-sub">${c.position || ''} · ${c.email}</div>
      </div>
      <div>${badge(c.status)}</div>
    </div>

    <div class="metrics-grid">
      <div class="metric-card brand">
        <div class="metric-label">Hourly Rate</div>
        <div class="metric-value">${fmtRate(c.pay_rate)}</div>
      </div>
      <div class="metric-card amber">
        <div class="metric-label">Start Date</div>
        <div class="metric-value" style="font-size:1.3rem">${fmtDate(c.start_date)}</div>
      </div>
      <div class="metric-card blue">
        <div class="metric-label">Documents</div>
        <div class="metric-value">${data.completed_documents}/${data.total_documents}</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">Progress</div>
        <div class="metric-value">${data.completion_percentage.toFixed(0)}%</div>
      </div>
    </div>

    <div class="detail-actions" style="margin-bottom:24px">
      <button class="btn btn-primary" onclick="generateDocs(${c.id})">
        📄 Generate Docs
      </button>
      <button class="btn btn-secondary" onclick="sendOffer(${c.id})">
        📧 Send Offer
      </button>
      <button class="btn btn-secondary" onclick="sendReminder(${c.id})">
        ⏰ Send Reminder
      </button>
      <select class="status-select" onchange="updateStatus(${c.id}, this.value)" id="statusSel">
        <option value="Pending" ${c.status === 'Pending' ? 'selected' : ''}>Pending</option>
        <option value="In Progress" ${c.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
        <option value="Complete" ${c.status === 'Complete' ? 'selected' : ''}>Complete</option>
      </select>
    </div>

    <hr class="divider">

    <div class="two-col">
      <div class="card">
        <div class="card-header">
          <div class="card-title">📋 Document Checklist</div>
          ${!data.documents.length ? `<button class="btn btn-ghost btn-sm" onclick="addStandardDocs(${c.id})">+ Add Docs</button>` : ''}
        </div>
        <div class="doc-list">
        <div class="doc-list">
          ${data.documents.length ? data.documents.map(d => {
    const fname = d.file_path ? d.file_path.split(/[\\/]/).pop() : "";
    return `
            <div class="doc-item">
              <div class="doc-check ${d.status === 'Completed' ? 'done' : ''}" onclick="toggleDoc(${d.id}, '${d.status}')" title="Mark ${d.status === 'Completed' ? 'pending' : 'complete'}"></div>
              <div style="flex:1">
                <div class="doc-name">${d.document_type}</div>
                ${d.file_path ? `<a href="/api/download/${fname}" class="doc-link" target="_blank" style="display:block;font-size:0.85rem;color:var(--primary);text-decoration:none;margin-top:2px">⬇️ Download File</a>` : ''}
              </div>
              ${badge(d.status)}
            </div>
          `}).join('') : `<div class="empty-state"><p>No documents tracked yet.</p><button class="btn btn-primary btn-sm" onclick="addStandardDocs(${c.id})">Add Standard Documents</button></div>`}
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">📝 Activity Log</div>
        </div>
        <div class="activity-list">
          ${data.activities.length ? data.activities.slice(0, 15).map(a => `
            <div class="activity-item">
              <div class="activity-icon">${activityIcon(a.activity_type)}</div>
              <div class="activity-content">
                <div class="activity-type">${a.activity_type}</div>
                <div class="activity-desc">${a.description || ''}</div>
                <div class="activity-time">${fmtTimeAgo(a.timestamp)}</div>
              </div>
            </div>
          `).join('') : `<div class="empty-state"><p>No activity yet</p></div>`}
        </div>
      </div>
    </div>
  `;
}

// ── Detail actions ─────────────────────────────────────────────────
async function generateDocs(id) {
  try {
    const res = await api.post(`/api/consultants/${id}/generate-docs`);
    toast("Documents generated successfully!");

    // Auto-download files (for serverless compatibility)
    if (res.files && res.files.length) {
      res.files.forEach(f => {
        const link = document.createElement("a");
        link.href = `data:${f.type};base64,${f.data}`;
        link.download = f.name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        toast(`Downloading ${f.name}...`, "info");
      });
    }

    renderDetail(id);
    refreshSidebarStats();
  } catch (e) { toast(e.message, "error"); }
}

async function sendOffer(id) {
  try {
    const r = await api.post(`/api/consultants/${id}/send-offer`);
    toast(r.message);
    renderDetail(id);
  } catch (e) { toast(e.message, "error"); }
}

async function sendReminder(id) {
  try {
    const r = await api.post(`/api/consultants/${id}/send-reminder`);
    toast(r.message);
    renderDetail(id);
  } catch (e) { toast(e.message, "error"); }
}

async function updateStatus(id, status) {
  try {
    await api.put(`/api/consultants/${id}/status`, { status });
    toast(`Status updated to ${status}`);
    renderDetail(id);
    refreshSidebarStats();
  } catch (e) { toast(e.message, "error"); }
}

async function toggleDoc(docId, currentStatus) {
  const newStatus = currentStatus === "Completed" ? "Pending" : "Completed";
  try {
    await api.put(`/api/documents/${docId}/status`, { status: newStatus });
    toast(`Document ${newStatus === 'Completed' ? 'completed ✓' : 'marked pending'}`);
    renderDetail(currentDetail);
    refreshSidebarStats();
  } catch (e) { toast(e.message, "error"); }
}

async function addStandardDocs(id) {
  try {
    await api.post(`/api/consultants/${id}/add-standard-docs`);
    toast("Standard documents added!");
    renderDetail(id);
  } catch (e) { toast(e.message, "error"); }
}

// ── New consultant form ────────────────────────────────────────────
function renderNewForm() {
  const el = document.getElementById("page-new");
  el.innerHTML = `
    <a href="#" class="back-link" onclick="event.preventDefault();navigate('consultants')">← Cancel</a>

    <div class="page-header">
      <div>
        <h1>New Consultant Onboarding</h1>
        <div class="sub">Enter consultant information to start the onboarding process</div>
      </div>
    </div>

    <div class="card" style="max-width:720px">
      <div class="form-grid" id="newForm">
        <div class="form-group">
          <label class="form-label">Full Name <span class="req">*</span></label>
          <input type="text" class="form-input" id="f_name" placeholder="John Smith">
        </div>
        <div class="form-group">
          <label class="form-label">Email Address <span class="req">*</span></label>
          <input type="email" class="form-input" id="f_email" placeholder="john@example.com">
        </div>
        <div class="form-group">
          <label class="form-label">Position / Role <span class="req">*</span></label>
          <input type="text" class="form-input" id="f_position" placeholder="Senior Consultant">
        </div>
        <div class="form-group">
          <label class="form-label">Reporting Manager</label>
          <input type="text" class="form-input" id="f_manager" placeholder="Debbie Murray">
        </div>
        <div class="form-group">
          <label class="form-label">Hourly Rate ($)</label>
          <input type="text" class="form-input" id="f_pay" placeholder="25.00">
        </div>
        <div class="form-group">
          <label class="form-label">Start Date</label>
          <input type="date" class="form-input" id="f_start">
        </div>
        <div class="form-group">
          <label class="form-label">End Date (if contract)</label>
          <input type="date" class="form-input" id="f_end">
        </div>
        <div class="form-group">
          <label class="form-label">Employment Type</label>
          <select class="form-select" id="f_type">
            <option>Full-Time Consultant</option>
            <option>Part-Time Consultant</option>
            <option>Contract</option>
            <option>1099 Contractor</option>
          </select>
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" onclick="submitNewConsultant()">
          ✅ Start Onboarding
        </button>
        <button class="btn btn-secondary" onclick="navigate('consultants')">Cancel</button>
      </div>
    </div>
  `;
}

async function submitNewConsultant() {
  const name = document.getElementById("f_name").value.trim();
  const email = document.getElementById("f_email").value.trim();
  const position = document.getElementById("f_position").value.trim();

  if (!name || !email || !position) {
    toast("Please fill in all required fields", "error");
    return;
  }

  const data = {
    name,
    email,
    position,
    manager: document.getElementById("f_manager").value.trim(),
    pay_rate: document.getElementById("f_pay").value.trim(),
    start_date: document.getElementById("f_start").value || null,
    end_date: document.getElementById("f_end").value || null,
    employment_type: document.getElementById("f_type").value,
    add_standard_docs: true
  };

  try {
    const c = await api.post("/api/consultants", data);
    toast(`${name} added successfully!`);
    navigate("detail", c.id);
    refreshSidebarStats();
  } catch (e) { toast(e.message, "error"); }
}

// ── Emails page ────────────────────────────────────────────────────
async function renderEmails() {
  const consultants = await api.get("/api/consultants");

  const el = document.getElementById("page-emails");
  el.innerHTML = `
    <div class="page-header">
      <div>
        <h1>Email Management</h1>
        <div class="sub">Send emails and manage templates</div>
      </div>
    </div>

    <div class="section-title">Email Templates</div>
    <div class="template-grid">
      <div class="template-card">
        <div class="template-icon">📨</div>
        <div class="template-title">Offer Letter</div>
        <div class="template-desc">Send the official offer letter with compensation details and attached document</div>
      </div>
      <div class="template-card">
        <div class="template-icon">📋</div>
        <div class="template-title">Document Request</div>
        <div class="template-desc">Request completion of onboarding documents (W-4, I-9, Direct Deposit)</div>
      </div>
      <div class="template-card">
        <div class="template-icon">⏰</div>
        <div class="template-title">Reminder</div>
        <div class="template-desc">Friendly reminder for pending items and outstanding documents</div>
      </div>
      <div class="template-card">
        <div class="template-icon">🎉</div>
        <div class="template-title">Welcome</div>
        <div class="template-desc">First-day welcome email with schedule and team information</div>
      </div>
    </div>

    <hr class="divider">

    <div class="section-title">Send Email</div>
    <div class="card" style="max-width:700px">
      ${consultants.length ? `
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Select Consultant</label>
            <select class="form-select" id="email_consultant">
              ${consultants.map(c => `<option value="${c.id}">${c.name} — ${c.email}</option>`).join("")}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Email Type</label>
            <select class="form-select" id="email_type">
              <option value="offer">Offer Letter</option>
              <option value="reminder">Document Reminder</option>
            </select>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn btn-primary" onclick="sendEmailAction()">📤 Send Email</button>
        </div>
      ` : `<div class="empty-state"><p>Add consultants first to send emails</p></div>`}
    </div>

    <hr class="divider">

    <div class="section-title">Bulk Actions</div>
    <div class="card" style="max-width:700px">
      <div class="form-grid">
        <div class="form-group full">
          <label class="form-label">Action</label>
          <select class="form-select" id="bulk_action">
            <option>Send reminder to all with pending documents</option>
            <option>Send reminder to all pending > 7 days</option>
            <option>Send welcome to all starting this week</option>
          </select>
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-secondary" onclick="toast('Bulk emails queued!','info')">📤 Send All</button>
      </div>
    </div>
  `;
}

async function sendEmailAction() {
  const cid = document.getElementById("email_consultant").value;
  const type = document.getElementById("email_type").value;

  try {
    if (type === "offer") {
      const r = await api.post(`/api/consultants/${cid}/send-offer`);
      toast(r.message);
    } else {
      const r = await api.post(`/api/consultants/${cid}/send-reminder`);
      toast(r.message);
    }
  } catch (e) { toast(e.message, "error"); }
}

// ── Reports page ───────────────────────────────────────────────────
async function renderReports() {
  const [summary, consultants] = await Promise.all([
    api.get("/api/summary"),
    api.get("/api/consultants")
  ]);

  const maxVal = Math.max(summary.pending, summary.in_progress, summary.complete, 1);

  const el = document.getElementById("page-reports");
  el.innerHTML = `
    <div class="page-header">
      <div>
        <h1>Reports</h1>
        <div class="sub">Onboarding analytics and data exports</div>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric-card brand">
        <div class="metric-label">Total Consultants</div>
        <div class="metric-value">${summary.total}</div>
        <div class="metric-icon">👥</div>
      </div>
      <div class="metric-card amber">
        <div class="metric-label">Pending</div>
        <div class="metric-value">${summary.pending}</div>
        <div class="metric-icon">⏳</div>
      </div>
      <div class="metric-card blue">
        <div class="metric-label">In Progress</div>
        <div class="metric-value">${summary.in_progress}</div>
        <div class="metric-icon">🔄</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">Complete</div>
        <div class="metric-value">${summary.complete}</div>
        <div class="metric-icon">✅</div>
      </div>
    </div>

    <hr class="divider">

    <div class="two-col">
      <div class="card">
        <div class="card-header">
          <div class="card-title">Status Breakdown</div>
        </div>
        <div class="chart-bars">
          <div class="chart-col">
            <div class="chart-val">${summary.pending}</div>
            <div class="chart-bar amber" style="height:${(summary.pending / maxVal) * 140}px; min-height: 4px;"></div>
            <div class="chart-label">Pending</div>
          </div>
          <div class="chart-col">
            <div class="chart-val">${summary.in_progress}</div>
            <div class="chart-bar blue" style="height:${(summary.in_progress / maxVal) * 140}px; min-height: 4px;"></div>
            <div class="chart-label">In Progress</div>
          </div>
          <div class="chart-col">
            <div class="chart-val">${summary.complete}</div>
            <div class="chart-bar green" style="height:${(summary.complete / maxVal) * 140}px; min-height: 4px;"></div>
            <div class="chart-label">Complete</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">Export Data</div>
        </div>
        <div class="export-grid">
          <a href="/api/export/consultants" class="btn btn-secondary btn-sm" download>📥 Consultants CSV</a>
          <a href="/api/export/documents" class="btn btn-secondary btn-sm" download>📥 Documents CSV</a>
          <a href="/api/export/activities" class="btn btn-secondary btn-sm" download>📥 Activity Log CSV</a>
        </div>
      </div>
    </div>
  `;
}

// ── Event listeners ────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Navigation
  document.querySelectorAll(".nav-item").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      navigate(link.dataset.page);
    });
  });

  // Mobile hamburger
  const hamburger = document.getElementById("hamburger");
  const sidebar = document.getElementById("sidebar");
  if (hamburger) {
    hamburger.addEventListener("click", () => sidebar.classList.toggle("open"));
  }

  // Close sidebar on outside click (mobile)
  document.addEventListener("click", e => {
    if (window.innerWidth <= 768 && sidebar.classList.contains("open")) {
      if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    }
  });

  // Initial load
  navigate("dashboard");
});
