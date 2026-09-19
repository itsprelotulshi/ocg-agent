// State Management
const state = {
  currentSessionId: null,
  user: null,
  token: localStorage.getItem("sb_access_token") || "",
  skills: [],
  activeSkillIds: [],
  isGenerating: false,
  catalog: { mcp: [], plugins: [], skills: [] },
  installedPackages: { mcp: {}, plugins: {}, skills: {} },
  memories: [],
  currentMarketFilter: "all",
  currentMemoryCategory: "all",
  supabaseClient: null,
  realtimeChannel: null,
  realtimeStatus: "offline",
  supabaseConfig: { url: "", anonKey: "" },
};

// DOM References
const elements = {
  sessionsList: document.getElementById("sessions-list"),
  skillsList: document.getElementById("skills-list"),
  mcpStatusBox: document.getElementById("mcp-status-box"),
  mcpToolCount: document.getElementById("mcp-tool-count"),
  mcpServerTags: document.getElementById("mcp-server-tags"),
  reloadMcpBtn: document.getElementById("reload-mcp-btn"),
  newChatBtn: document.getElementById("new-chat-btn"),
  messagesViewport: document.getElementById("messages-viewport"),
  messagesList: document.getElementById("messages-list"),
  welcomeContainer: document.getElementById("welcome-container"),
  chatTextarea: document.getElementById("chat-textarea"),
  sendBtn: document.getElementById("send-btn"),
  activeSessionTitle: document.getElementById("active-session-title"),
  userEmail: document.getElementById("user-email"),
  userRole: document.getElementById("user-role"),
  userAvatar: document.getElementById("user-avatar"),
  llmStatusBadge: document.getElementById("llm-status-badge"),
  activeSkillsChips: document.getElementById("active-skills-chips"),
  realtimeStatusBadge: document.getElementById("realtime-status-badge"),
  realtimeStatusLabel: document.getElementById("realtime-status-label"),

  // Navigation & Badges
  sidebarMemoryCount: document.getElementById("sidebar-memory-count"),
  navMemoryBtn: document.getElementById("nav-memory-btn"),
  navMemoryCount: document.getElementById("nav-memory-count"),
  marketplaceModalBtn: document.getElementById("marketplace-modal-btn"),
  memoryModalBtn: document.getElementById("memory-modal-btn"),
  navMarketplaceBtn: document.getElementById("nav-marketplace-btn"),

  // Marketplace Modal
  marketplaceModal: document.getElementById("marketplace-modal"),
  marketplaceModalClose: document.getElementById("marketplace-modal-close"),
  tabBtnCatalog: document.getElementById("tab-btn-catalog"),
  tabBtnCustom: document.getElementById("tab-btn-custom"),
  tabBtnInstalled: document.getElementById("tab-btn-installed"),
  paneCatalog: document.getElementById("pane-catalog"),
  paneCustom: document.getElementById("pane-custom"),
  paneInstalled: document.getElementById("pane-installed"),
  catalogGrid: document.getElementById("catalog-grid"),
  catalogSearch: document.getElementById("catalog-search"),
  installedPackagesList: document.getElementById("installed-packages-list"),
  customInstallForm: document.getElementById("custom-install-form"),
  customInstallType: document.getElementById("custom-install-type"),
  customInstallName: document.getElementById("custom-install-name"),
  customInstallUrl: document.getElementById("custom-install-url"),
  customInstallConfig: document.getElementById("custom-install-config"),
  customInstallCode: document.getElementById("custom-install-code"),
  customInstallBtn: document.getElementById("custom-install-btn"),
  customInstallFeedback: document.getElementById("custom-install-feedback"),
  mcpConfigGroup: document.getElementById("mcp-config-group"),
  codeContentGroup: document.getElementById("code-content-group"),

  // Memory Modal
  memoryModal: document.getElementById("memory-modal"),
  memoryModalClose: document.getElementById("memory-modal-close"),
  memoryCategoryPills: document.getElementById("memory-category-pills"),
  toggleAddMemoryBtn: document.getElementById("toggle-add-memory-btn"),
  clearMemoriesBtn: document.getElementById("clear-memories-btn"),
  addMemoryPanel: document.getElementById("add-memory-panel"),
  addMemoryForm: document.getElementById("add-memory-form"),
  newMemCategory: document.getElementById("new-mem-category"),
  newMemKey: document.getElementById("new-mem-key"),
  newMemContent: document.getElementById("new-mem-content"),
  cancelAddMemoryBtn: document.getElementById("cancel-add-memory-btn"),
  memoriesList: document.getElementById("memories-list"),

  // Auth (inside Settings modal Account panel)
  authForm: document.getElementById("auth-form"),
  authEmail: document.getElementById("auth-email"),
  authPassword: document.getElementById("auth-password"),
  authFeedback: document.getElementById("auth-feedback"),
  authSubmitBtn: document.getElementById("auth-submit-btn"),

  // Settings Modal
  settingsModal: document.getElementById("settings-modal"),
  settingsModalBtn: document.getElementById("settings-modal-btn"),
  settingsModalClose: document.getElementById("settings-modal-close"),
  settingsForm: document.getElementById("settings-form"),
  settingModel: document.getElementById("setting-model"),
  settingTemp: document.getElementById("setting-temp"),
  settingBaseUrl: document.getElementById("setting-base-url"),
  settingApiKey: document.getElementById("setting-api-key"),
  settingSupabaseUrl: document.getElementById("setting-supabase-url"),
  settingSupabaseAnonKey: document.getElementById("setting-supabase-anon-key"),
  settingsFeedback: document.getElementById("settings-feedback"),

  sidebar: document.getElementById("sidebar"),
  toggleSidebarBtn: document.getElementById("toggle-sidebar-btn"),
};


// API Helpers
async function apiFetch(url, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) {
    headers["Authorization"] = `Bearer ${state.token}`;
  }
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    let errDetail = "Request failed";
    try {
      const errJson = await response.json();
      errDetail = errJson.detail || errDetail;
    } catch (_) { }
    throw new Error(errDetail);
  }
  return response.json();
}

// Track whether the demo-mode banner has already been shown in this session
let _demoNoticedShown = false;

// Page-load progress bar helper
function setLoadingProgress(pct) {
  const bar = document.getElementById('page-loading-bar');
  if (!bar) return;
  bar.style.width = pct + '%';
  if (pct >= 100) setTimeout(() => { bar.style.opacity = '0'; }, 350);
}

// Initialization
async function initApp() {
  setLoadingProgress(5);
  setupEventListeners();
  setLoadingProgress(15);
  await checkAuth();
  setLoadingProgress(35);
  await loadMCPStatus();
  setLoadingProgress(55);
  await loadSkills();
  setLoadingProgress(70);
  await loadSessions();
  setLoadingProgress(85);
  await loadInfo();
  setLoadingProgress(95);
  await loadMemoriesCount();
  setLoadingProgress(100);
}


// Authentication
async function checkAuth() {
  try {
    const user = await apiFetch("/api/auth/me");
    state.user = user;
    elements.userEmail.textContent = user.email || "Guest Mode";
    elements.userRole.textContent = user.is_guest ? "Guest Mode" : `Supabase User (${user.role})`;
    elements.userAvatar.textContent = user.is_guest ? "\u{1F464}" : "\u{1F512}";
    updateAuthModalView();
  } catch (err) {
    console.warn("Auth check fallback:", err);
    state.user = { is_guest: true, email: "guest@local", role: "guest" };
    elements.userEmail.textContent = "Guest Mode";
    elements.userRole.textContent = "Unauthenticated";
    updateAuthModalView();
  }
}

function updateAuthModalView() {
  const isGuest = !state.user || state.user.is_guest;

  // Settings modal sidebar nav profile header
  const navEmail = document.getElementById("settings-nav-email");
  const navRole = document.getElementById("settings-nav-role");
  const navAvatar = document.getElementById("settings-nav-avatar");
  if (navEmail) navEmail.textContent = isGuest ? "Guest Mode" : (state.user.email || "\u2014");
  if (navRole) navRole.textContent = isGuest ? "Unauthenticated" : `Supabase User \u00b7 ${state.user.role || "authenticated"}`;
  if (navAvatar) navAvatar.textContent = isGuest ? "\u{1F464}" : "\u{1F512}";

  // Account panel: show login form or profile view
  const loginView = document.getElementById("sp-login-view");
  const profileView = document.getElementById("sp-profile-view");
  if (loginView) loginView.style.display = isGuest ? "block" : "none";
  if (profileView) profileView.style.display = isGuest ? "none" : "block";

  if (!isGuest) {
    const heroEmail = document.getElementById("sp-hero-email");
    const heroRole = document.getElementById("sp-hero-role");
    const heroAvatar = document.getElementById("sp-avatar-lg");
    if (heroEmail) heroEmail.textContent = state.user.email || "\u2014";
    if (heroRole) heroRole.textContent = `Supabase User \u00b7 ${state.user.role || "authenticated"}`;
    if (heroAvatar) heroAvatar.textContent = "\u{1F512}";
  }
}

// MCP Status
async function loadMCPStatus() {
  try {
    const res = await apiFetch("/api/mcp/status");
    if (elements.mcpToolCount) {
      elements.mcpToolCount.textContent = `${res.total_tools} MCP tools available`;
    }
    if (elements.mcpServerTags) {
      elements.mcpServerTags.innerHTML = "";
      res.servers.forEach((s) => {
        const tag = document.createElement("span");
        tag.className = "server-tag";
        tag.textContent = `${s.name} (${s.tools_count})`;
        elements.mcpServerTags.appendChild(tag);
      });
    }
    const settingsMcpTags = document.getElementById("settings-mcp-tags");
    if (settingsMcpTags && elements.mcpServerTags) {
      settingsMcpTags.innerHTML = elements.mcpServerTags.innerHTML;
    }
  } catch (e) {
    if (elements.mcpToolCount) elements.mcpToolCount.textContent = "MCP Offline";
  }
}

// Skills
async function loadSkills() {
  try {
    const res = await apiFetch("/api/skills");
    state.skills = res.skills;
    renderSkills();
  } catch (e) {
    console.error("Failed to load skills:", e);
  }
}

function renderSkills() {
  if (!elements.skillsList) return;
  elements.skillsList.innerHTML = "";
  state.skills.forEach((s) => {
    const item = document.createElement("div");
    item.className = "skill-item";
    item.innerHTML = `
      <span>${s.name}</span>
      <input type="checkbox" class="skill-toggle" data-id="${s.id}" ${s.enabled ? "checked" : ""}>
    `;
    elements.skillsList.appendChild(item);
  });

  // Event listener for toggles
  document.querySelectorAll(".skill-toggle").forEach((cb) => {
    cb.addEventListener("change", async (e) => {
      const id = e.target.getAttribute("data-id");
      try {
        await apiFetch(`/api/skills/${id}/toggle`, { method: "POST" });
        const skill = state.skills.find((s) => s.id === id);
        if (skill) skill.enabled = e.target.checked;
        updateActiveSkillsChips();
      } catch (err) {
        alert("Failed to toggle skill: " + err.message);
      }
    });
  });

  updateActiveSkillsChips();
}

function updateActiveSkillsChips() {
  if (!elements.activeSkillsChips) return;
  elements.activeSkillsChips.innerHTML = "";
  state.skills.filter((s) => s.enabled).forEach((s) => {
    const chip = document.createElement("span");
    chip.className = "badge badge-outline";
    chip.textContent = `\u{1F3AF} ${s.name}`;
    elements.activeSkillsChips.appendChild(chip);
  });
}

// Sessions
async function loadSessions() {
  try {
    const res = await apiFetch("/api/sessions");
    renderSessions(res.sessions);
    if (res.sessions.length > 0 && !state.currentSessionId) {
      selectSession(res.sessions[0].id, res.sessions[0].title);
    }
  } catch (e) {
    console.error("Failed to load sessions:", e);
  }
}

function renderSessions(sessions) {
  elements.sessionsList.innerHTML = "";
  sessions.forEach((s) => {
    const div = document.createElement("div");
    div.className = `session-item ${s.id === state.currentSessionId ? "active" : ""}`;
    div.dataset.id = s.id;
    div.innerHTML = `
      <span class="session-title">${escapeHtml(s.title || "Conversation")}</span>
      <button class="session-delete-btn" data-id="${s.id}" title="Delete session">\u2715</button>
    `;
    div.addEventListener("click", (e) => {
      if (!e.target.classList.contains("session-delete-btn")) {
        selectSession(s.id, s.title);
      }
    });
    elements.sessionsList.appendChild(div);
  });

  // Delete handlers
  document.querySelectorAll(".session-delete-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const id = e.target.dataset.id;
      if (confirm("Delete this conversation?")) {
        try {
          await apiFetch(`/api/sessions/${id}`, { method: "DELETE" });
          if (state.currentSessionId === id) {
            state.currentSessionId = null;
            elements.messagesList.innerHTML = "";
            elements.welcomeContainer.style.display = "block";
            elements.activeSessionTitle.textContent = "New Conversation";
          }
          await loadSessions();
        } catch (err) {
          alert("Error deleting session: " + err.message);
        }
      }
    });
  });
}

async function selectSession(sessionId, title) {
  state.currentSessionId = sessionId;
  elements.activeSessionTitle.textContent = title || "Conversation";

  // Update active class in list
  document.querySelectorAll(".session-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.id === sessionId);
  });

  elements.welcomeContainer.style.display = "none";
  elements.messagesList.innerHTML = "";

  // Fetch messages
  try {
    const res = await apiFetch(`/api/sessions/${sessionId}/messages`);
    res.messages.forEach((m) => appendMessageUI(m.role, m.content, m.tool_calls, m.tool_results, m.id));
    scrollToBottom();
  } catch (err) {
    console.error("Failed to load messages:", err);
  }
}

// System Info
async function loadInfo() {
  try {
    const info = await apiFetch("/api/info");
    elements.llmStatusBadge.textContent = `${info.model} ${info.is_llm_configured ? "\u{1F7E2}" : "\u26AA Demo"}`;
    if (elements.settingModel) elements.settingModel.value = info.model;
    if (elements.settingBaseUrl) elements.settingBaseUrl.value = info.base_url;

    if (elements.settingSupabaseUrl && info.supabase_url && !elements.settingSupabaseUrl.value) {
      elements.settingSupabaseUrl.value = info.supabase_url;
    }
    if (elements.settingSupabaseAnonKey && info.supabase_anon_key && !elements.settingSupabaseAnonKey.value) {
      elements.settingSupabaseAnonKey.value = info.supabase_anon_key;
    }

    // Initialize Supabase Realtime synchronization
    if (info.supabase_url && info.supabase_anon_key) {
      initSupabaseRealtime(info.supabase_url, info.supabase_anon_key);
    } else {
      updateRealtimeBadge("offline", "Realtime: Offline (Demo)");
    }
  } catch (e) {
    console.warn("Could not load info:", e);
    updateRealtimeBadge("offline", "Realtime: Offline");
  }
}

// ==============================================================================
// Supabase Realtime Synchronizer
// ==============================================================================

function updateRealtimeBadge(status, customLabel = null) {
  state.realtimeStatus = status;
  if (!elements.realtimeStatusBadge || !elements.realtimeStatusLabel) return;

  elements.realtimeStatusBadge.classList.remove("connected", "connecting", "offline");
  elements.realtimeStatusBadge.classList.add(status);

  if (customLabel) {
    elements.realtimeStatusLabel.textContent = customLabel;
  } else if (status === "connected") {
    elements.realtimeStatusLabel.textContent = "";
  } else if (status === "connecting") {
    elements.realtimeStatusLabel.textContent = "Connecting...";
  } else {
    elements.realtimeStatusLabel.textContent = "Offline";
  }
}

function initSupabaseRealtime(url, anonKey) {
  if (!url || !anonKey || url.includes("mock") || anonKey.includes("mock")) {
    updateRealtimeBadge("offline", "Realtime: Offline (Demo)");
    return;
  }

  if (!window.supabase || typeof window.supabase.createClient !== "function") {
    console.warn("Supabase JS SDK still loading, retrying realtime in 400ms...");
    setTimeout(() => initSupabaseRealtime(url, anonKey), 400);
    return;
  }

  if (state.supabaseClient && state.supabaseConfig.url === url && state.supabaseConfig.anonKey === anonKey) {
    return;
  }

  state.supabaseConfig = { url, anonKey };

  try {
    updateRealtimeBadge("connecting");
    state.supabaseClient = window.supabase.createClient(url, anonKey, {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
      },
      realtime: {
        params: {
          eventsPerSecond: 10,
        },
      },
    });

    if (state.token && state.token !== "mock-access-token-demo") {
      try {
        state.supabaseClient.realtime.setAuth(state.token);
      } catch (e) {
        console.warn("Realtime setAuth note:", e);
      }
    }

    setupRealtimeSubscriptions();
  } catch (err) {
    console.error("Failed to initialize Supabase Realtime client:", err);
    updateRealtimeBadge("offline");
  }
}

function setupRealtimeSubscriptions() {
  if (!state.supabaseClient) return;

  if (state.realtimeChannel) {
    try {
      state.supabaseClient.removeChannel(state.realtimeChannel);
    } catch (_) { }
    state.realtimeChannel = null;
  }

  updateRealtimeBadge("connecting");

  const channel = state.supabaseClient.channel("ocg-agent-db-sync");

  channel
    .on(
      "postgres_changes",
      { event: "*", schema: "public", table: "sessions" },
      (payload) => handleRealtimeSession(payload)
    )
    .on(
      "postgres_changes",
      { event: "*", schema: "public", table: "messages" },
      (payload) => handleRealtimeMessage(payload)
    )
    .on(
      "postgres_changes",
      { event: "*", schema: "public", table: "agent_memories" },
      (payload) => handleRealtimeMemory(payload)
    )
    .subscribe((status, err) => {
      console.log(`[Supabase Realtime] Channel status: ${status}`, err || "");
      if (status === "SUBSCRIBED") {
        updateRealtimeBadge("connected");
      } else if (status === "TIMED_OUT" || status === "CHANNEL_ERROR") {
        updateRealtimeBadge("offline");
        setTimeout(() => {
          if (state.realtimeStatus === "offline" && state.supabaseClient) {
            setupRealtimeSubscriptions();
          }
        }, 5000);
      } else if (status === "CLOSED") {
        updateRealtimeBadge("connecting");
      }
    });

  state.realtimeChannel = channel;
}

async function handleRealtimeSession(payload) {
  const { eventType, new: newRecord, old: oldRecord } = payload;

  if (eventType === "INSERT") {
    if (!newRecord) return;
    const existing = elements.sessionsList.querySelector(`[data-id="${newRecord.id}"]`);
    if (!existing) {
      const div = document.createElement("div");
      div.className = `session-item ${newRecord.id === state.currentSessionId ? "active" : ""}`;
      div.dataset.id = newRecord.id;
      div.innerHTML = `
        <span class="session-title">${escapeHtml(newRecord.title || "Conversation")}</span>
        <button class="session-delete-btn" data-id="${newRecord.id}" title="Delete session">\u2715</button>
      `;
      div.addEventListener("click", (e) => {
        if (!e.target.classList.contains("session-delete-btn")) {
          selectSession(newRecord.id, newRecord.title);
        }
      });
      const delBtn = div.querySelector(".session-delete-btn");
      if (delBtn) {
        delBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          if (confirm("Delete this conversation?")) {
            try {
              await apiFetch(`/api/sessions/${newRecord.id}`, { method: "DELETE" });
              if (state.currentSessionId === newRecord.id) {
                state.currentSessionId = null;
                elements.messagesList.innerHTML = "";
                elements.welcomeContainer.style.display = "block";
                elements.activeSessionTitle.textContent = "New Conversation";
              }
              await loadSessions();
            } catch (err) {
              alert("Error deleting session: " + err.message);
            }
          }
        });
      }
      elements.sessionsList.prepend(div);
      div.classList.add("realtime-flash");
      setTimeout(() => div.classList.remove("realtime-flash"), 1200);
    }
  } else if (eventType === "UPDATE") {
    if (!newRecord) return;
    const existing = elements.sessionsList.querySelector(`[data-id="${newRecord.id}"]`);
    if (existing) {
      const titleEl = existing.querySelector(".session-title");
      if (titleEl) titleEl.textContent = newRecord.title || "Conversation";
      existing.classList.add("realtime-flash");
      setTimeout(() => existing.classList.remove("realtime-flash"), 1200);
    }
    if (state.currentSessionId === newRecord.id) {
      elements.activeSessionTitle.textContent = newRecord.title || "Conversation";
    }
  } else if (eventType === "DELETE") {
    if (!oldRecord) return;
    const existing = elements.sessionsList.querySelector(`[data-id="${oldRecord.id}"]`);
    if (existing) {
      existing.remove();
    }
    if (state.currentSessionId === oldRecord.id) {
      state.currentSessionId = null;
      elements.messagesList.innerHTML = "";
      elements.welcomeContainer.style.display = "block";
      elements.activeSessionTitle.textContent = "New Conversation";
    }
  }
}

function handleRealtimeMessage(payload) {
  const { eventType, new: newRecord, old: oldRecord } = payload;

  if (eventType === "INSERT") {
    if (!newRecord || newRecord.session_id !== state.currentSessionId) {
      return;
    }

    // 1. If an element with this exact message id already exists, skip
    if (elements.messagesList.querySelector(`[data-id="${newRecord.id}"]`)) {
      return;
    }

    // 2. Deduplicate user message sent from this tab: attach data-id to the local row
    if (newRecord.role === "user") {
      const userRows = elements.messagesList.querySelectorAll(".message-row.user:not([data-id])");
      if (userRows.length > 0) {
        const lastUserRow = userRows[userRows.length - 1];
        const contentEl = lastUserRow.querySelector(".message-content");
        if (contentEl && contentEl.textContent.trim() === (newRecord.content || "").trim()) {
          lastUserRow.dataset.id = newRecord.id;
          return;
        }
      }
    }

    // 3. Deduplicate assistant message completed in this tab via SSE stream
    if (newRecord.role === "assistant" && state.isGenerating) {
      const assistantRows = elements.messagesList.querySelectorAll(".message-row.assistant:not([data-id])");
      if (assistantRows.length > 0) {
        const lastAssistant = assistantRows[assistantRows.length - 1];
        lastAssistant.dataset.id = newRecord.id;
        return;
      }
    }

    // 4. If generated by another tab / device, append in real-time
    appendMessageUI(
      newRecord.role,
      newRecord.content,
      newRecord.tool_calls,
      newRecord.tool_results,
      newRecord.id
    );

    const newEl = elements.messagesList.querySelector(`[data-id="${newRecord.id}"]`);
    if (newEl) {
      newEl.classList.add("realtime-flash");
      setTimeout(() => newEl.classList.remove("realtime-flash"), 1200);
    }
    scrollToBottom();
  } else if (eventType === "UPDATE") {
    if (newRecord && newRecord.session_id === state.currentSessionId) {
      const existing = elements.messagesList.querySelector(`[data-id="${newRecord.id}"]`);
      if (existing) {
        const contentEl = existing.querySelector(".message-content");
        if (contentEl) {
          contentEl.innerHTML = newRecord.role === "assistant" ? marked.parse(newRecord.content || "") : escapeHtml(newRecord.content || "");
          applyCodeHighlighting(contentEl);
          existing.classList.add("realtime-flash");
          setTimeout(() => existing.classList.remove("realtime-flash"), 1200);
        }
      }
    }
  } else if (eventType === "DELETE") {
    if (oldRecord && oldRecord.id) {
      const existing = elements.messagesList.querySelector(`[data-id="${oldRecord.id}"]`);
      if (existing) {
        existing.style.opacity = "0";
        existing.style.transition = "opacity 0.25s ease";
        setTimeout(() => existing.remove(), 250);
      }
    }
  }
}

async function handleRealtimeMemory(payload) {
  await loadMemoriesCount();

  if (elements.navMemoryBtn) {
    elements.navMemoryBtn.classList.add("badge-pulse");
    setTimeout(() => elements.navMemoryBtn.classList.remove("badge-pulse"), 600);
  }
  if (elements.sidebarMemoryCount) {
    elements.sidebarMemoryCount.classList.add("badge-pulse");
    setTimeout(() => elements.sidebarMemoryCount.classList.remove("badge-pulse"), 600);
  }

  if (elements.memoryModal && elements.memoryModal.classList.contains("open")) {
    await loadMemories(state.currentMemoryCategory);
  }
}

// Chat Sending & Streaming
async function handleSend() {
  const text = elements.chatTextarea.value.trim();
  if (!text || state.isGenerating) return;

  elements.chatTextarea.value = "";
  elements.chatTextarea.style.height = "auto";
  elements.welcomeContainer.style.display = "none";

  // 1. Add User Message
  appendMessageUI("user", text);
  scrollToBottom();

  // 2. Prepare Assistant Bubble
  const assistantRow = createAssistantMessageRow();
  elements.messagesList.appendChild(assistantRow);
  const contentEl = assistantRow.querySelector(".message-content");
  const typingDots = assistantRow.querySelector("#typing-dots");
  scrollToBottom();

  state.isGenerating = true;
  elements.sendBtn.disabled = true;
  elements.sendBtn.innerHTML = '<span class="send-icon">\u23F8</span>';

  // Ensure session exists
  if (!state.currentSessionId) {
    try {
      const res = await apiFetch("/api/sessions", {
        method: "POST",
        body: JSON.stringify({ title: text.slice(0, 60) }),
      });
      state.currentSessionId = res.session.id;
      elements.activeSessionTitle.textContent = res.session.title;
      await loadSessions();
    } catch (err) {
      contentEl.innerHTML = `<div class="feedback-msg error">Failed to create session: ${escapeHtml(err.message)}</div>`;
      state.isGenerating = false;
      elements.sendBtn.disabled = false;
      elements.sendBtn.innerHTML = '<span class="send-icon">\u27A4</span>';
      return;
    }
  }

  try {
    const activeSkills = (state.skills || []).filter((s) => s.enabled).map((s) => s.id);
    const response = await fetch(`/api/sessions/${state.currentSessionId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}),
      },
      body: JSON.stringify({
        message: text,
        session_id: state.currentSessionId,
        skills: activeSkills,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let firstToken = true;
    let accumulatedText = "";
    const toolsContainer = assistantRow.querySelector(".tools-container");

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        const raw = line.trim();
        if (!raw || !raw.startsWith("data: ")) continue;
        const jsonStr = raw.slice(6);
        if (jsonStr === "[DONE]") continue;

        try {
          const parsed = JSON.parse(jsonStr);
          const event = parsed.event;
          const data = parsed.data || {};

          if (event === "token") {
            if (firstToken && typingDots) {
              typingDots.remove();
              firstToken = false;
            }
            const tokenStr = data.token !== undefined ? data.token : (data.content || "");
            accumulatedText += tokenStr;
            contentEl.innerHTML = marked.parse(accumulatedText);
            applyCodeHighlighting(contentEl);
            scrollToBottom();
          } else if (event === "tool_call") {
            const card = createToolCard(data.id, data.name, data.arguments);
            toolsContainer.appendChild(card);
            scrollToBottom();
          } else if (event === "tool_result") {
            updateToolCardResult(toolsContainer, data.id, data.content, data.is_error);
            scrollToBottom();
          } else if (event === "done") {
            if (typingDots) typingDots.remove();
            const finalContent = data.content || accumulatedText;
            if (finalContent) {
              contentEl.innerHTML = marked.parse(finalContent);
              applyCodeHighlighting(contentEl);
            }
            if (data.session_title) {
              elements.activeSessionTitle.textContent = data.session_title;
              await loadSessions();
            }
            scrollToBottom();
            if (data.new_memories && data.new_memories.length > 0) {
              await loadMemoriesCount();
            }
          } else if (event === "error") {
            if (typingDots) typingDots.remove();
            contentEl.innerHTML += `<div class="feedback-msg error">${escapeHtml(data.message || "An error occurred")}</div>`;
          }
        } catch (e) {
          console.error("SSE parse error:", e, raw);
        }
      }
    }

    // If typing dots still present (no tokens arrived), remove them
    if (typingDots && typingDots.parentNode) typingDots.remove();

  } catch (err) {
    if (typingDots && typingDots.parentNode) typingDots.remove();
    contentEl.innerHTML += `<div class="feedback-msg error">Error: ${escapeHtml(err.message)}</div>`;
  } finally {
    state.isGenerating = false;
    elements.sendBtn.disabled = false;
    elements.sendBtn.innerHTML = '<span class="send-icon">\u27A4</span>';
    elements.chatTextarea.focus();
  }
}

// UI Helpers
function appendMessageUI(role, content, toolCalls = null, toolResults = null, messageId = null) {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;
  if (messageId) {
    row.dataset.id = messageId;
  }
  const avatar = role === "user" ? "\u{1F464}" : "\u{1FA90}";

  let toolHtml = "";
  if (toolResults && toolResults.length > 0) {
    toolHtml = `<div class="tools-container">`;
    toolResults.forEach((tr) => {
      toolHtml += `
        <div class="tool-call-card">
          <div class="tool-call-header">
            <span class="tool-title">\u26A1 ${escapeHtml(tr.tool_name || tr.name || "Tool")}</span>
            <span class="tool-badge-pill">Completed</span>
          </div>
          <div class="tool-call-body">
            <div class="tool-result-content ${tr.is_error ? "error" : ""}">${escapeHtml(tr.content || "")}</div>
          </div>
        </div>
      `;
    });
    toolHtml += `</div>`;
  }

  const parsedContent = role === "assistant" ? marked.parse(content || "") : escapeHtml(content || "");

  row.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-body" style="flex: 1;">
      ${toolHtml}
      <div class="message-content">${parsedContent}</div>
    </div>
  `;

  elements.messagesList.appendChild(row);
  if (role === "assistant") {
    applyCodeHighlighting(row.querySelector(".message-content"));
  }
}

function createAssistantMessageRow() {
  const row = document.createElement("div");
  row.className = "message-row assistant";
  row.innerHTML = `
    <div class="message-avatar">\u{1FA90}</div>
    <div class="message-body" style="flex: 1;">
      <div class="tools-container"></div>
      <div class="message-content">
        <div class="typing-indicator" id="typing-dots">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    </div>
  `;
  return row;
}

function createToolCard(id, name, args) {
  const card = document.createElement("div");
  card.className = "tool-call-card";
  card.id = `tool-card-${id}`;
  card.innerHTML = `
    <div class="tool-call-header">
      <span class="tool-title">\u26A1 ${escapeHtml(name)}</span>
      <span class="tool-badge-pill" id="badge-${id}">Running...</span>
    </div>
    <div class="tool-call-body">
      <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 4px;">Arguments: <code>${escapeHtml(typeof args === "string" ? args : JSON.stringify(args))}</code></div>
      <div class="tool-result-content" id="result-${id}">Executing tool...</div>
    </div>
  `;
  return card;
}

function updateToolCardResult(container, id, content, isError) {
  const badge = container.querySelector(`#badge-${id}`);
  const resultEl = container.querySelector(`#result-${id}`);
  if (badge) {
    badge.textContent = isError ? "Error" : "Done";
    badge.style.backgroundColor = isError ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)";
    badge.style.color = isError ? "#ffa1a1" : "#86efac";
  }
  if (resultEl) {
    resultEl.textContent = content;
    if (isError) resultEl.classList.add("error");
  }
}

function scrollToBottom() {
  elements.messagesViewport.scrollTop = elements.messagesViewport.scrollHeight;
}

function applyCodeHighlighting(element) {
  if (window.hljs && element) {
    element.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });
  }
}

function escapeHtml(text) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
  return String(text).replace(/[&<>"']/g, (m) => map[m]);
}

// ==============================================================================
// Memory & Self-Improvisation Logic
// ==============================================================================

async function loadMemoriesCount() {
  try {
    const res = await apiFetch("/api/memory");
    state.memories = res.memories || [];
    const count = state.memories.length;
    if (elements.sidebarMemoryCount) elements.sidebarMemoryCount.textContent = count;
    if (elements.navMemoryCount) elements.navMemoryCount.textContent = count;
  } catch (err) {
    console.warn("Failed to load memories count:", err);
  }
}

async function loadMemories(category = null) {
  try {
    const url = category && category !== "all" ? `/api/memory?category=${category}` : "/api/memory";
    const res = await apiFetch(url);
    state.memories = res.memories || [];
    renderMemories(state.memories);
    loadMemoriesCount();
  } catch (err) {
    elements.memoriesList.innerHTML = `<div class="feedback-msg error">Error loading memories: ${escapeHtml(err.message)}</div>`;
  }
}

function renderMemories(memories) {
  elements.memoriesList.innerHTML = "";
  if (!memories || memories.length === 0) {
    elements.memoriesList.innerHTML = `
      <div style="text-align: center; padding: 36px 16px; color: var(--text-muted);">
        <div style="font-size: 32px; margin-bottom: 8px;">\u{1F9E0}</div>
        <div style="font-size: 14px; font-weight: 600; color: var(--text-secondary); margin-bottom: 4px;">No Memories Recorded Yet</div>
        <p style="font-size: 12px; max-width: 380px; margin: 0 auto;">As you converse with the agent, user facts, preferences, project constraints, and self-improvised rules are automatically learned and stored here.</p>
      </div>
    `;
    return;
  }

  memories.forEach((m) => {
    const card = document.createElement("div");
    card.className = "memory-card";
    const catClass = `cat-${m.category || "fact"}`;
    const dateStr = m.updated_at ? new Date(m.updated_at).toLocaleDateString() : "Active";

    card.innerHTML = `
      <div class="memory-card-header">
        <div class="memory-card-left">
          <span class="memory-cat-badge ${catClass}">${escapeHtml(m.category || "FACT")}</span>
          <span class="memory-key">${escapeHtml(m.key)}</span>
        </div>
        <button class="icon-btn-small mem-delete-btn" data-id="${m.id}" title="Delete memory">\u2715</button>
      </div>
      <div class="memory-content">${escapeHtml(m.content)}</div>
      <div class="memory-meta">
        <span>Source: <strong>${escapeHtml(m.source || "auto_extracted")}</strong></span>
        <span>${dateStr}</span>
      </div>
    `;

    card.querySelector(".mem-delete-btn").addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      if (confirm("Delete this memory?")) {
        try {
          await apiFetch(`/api/memory/${id}`, { method: "DELETE" });
          await loadMemories(state.currentMemoryCategory);
        } catch (err) {
          alert("Failed to delete memory: " + err.message);
        }
      }
    });

    elements.memoriesList.appendChild(card);
  });
}

// ==============================================================================
// Marketplace / Extensions
// ==============================================================================

async function loadMarketplaceCatalog() {
  try {
    const [catalogRes, installedRes] = await Promise.all([
      apiFetch("/api/marketplace/catalog"),
      apiFetch("/api/marketplace/installed"),
    ]);
    state.catalog = catalogRes;
    state.installedPackages = installedRes;
    renderCatalog();
  } catch (err) {
    elements.catalogGrid.innerHTML = `<div class="feedback-msg error">Failed to load catalog: ${escapeHtml(err.message)}</div>`;
  }
}

function renderCatalog() {
  const query = elements.catalogSearch.value.toLowerCase();
  const filter = state.currentMarketFilter;

  const allItems = [
    ...state.catalog.mcp.map((x) => ({ ...x, type: "mcp" })),
    ...state.catalog.plugins.map((x) => ({ ...x, type: "plugin" })),
    ...state.catalog.skills.map((x) => ({ ...x, type: "skill" })),
  ];

  const filtered = allItems.filter((item) => {
    const matchesFilter = filter === "all" || item.type === filter || (filter === "mcp" && item.type === "mcp");
    const matchesQuery = !query || (item.name || "").toLowerCase().includes(query) || (item.description || "").toLowerCase().includes(query);
    return matchesFilter && matchesQuery;
  });

  elements.catalogGrid.innerHTML = "";

  if (filtered.length === 0) {
    elements.catalogGrid.innerHTML = `<div style="color: var(--text-muted); padding: 24px; text-align: center; grid-column: 1/-1;">No items match your search.</div>`;
    return;
  }

  const mcpInstalled = state.installedPackages?.mcp || {};
  const pluginsInstalled = state.installedPackages?.plugins || {};
  const skillsInstalled = state.installedPackages?.skills || {};

  filtered.forEach((item) => {
    const card = document.createElement("div");
    card.className = "marketplace-card";
    const typeClass = `type-${item.type}`;

    const cleanId = (item.id || "").toLowerCase();
    const cleanIdUnderscore = cleanId.replace(/-/g, "_");

    const isInstalled =
      (item.type === "mcp" && Boolean(
        mcpInstalled[item.id] ||
        mcpInstalled[cleanId] ||
        mcpInstalled[cleanIdUnderscore] ||
        mcpInstalled[item.name] ||
        Object.keys(mcpInstalled).some(k => k.toLowerCase() === cleanId || k.toLowerCase() === cleanIdUnderscore)
      )) ||
      (item.type === "plugin" && Boolean(
        pluginsInstalled[item.id] ||
        pluginsInstalled[cleanId] ||
        pluginsInstalled[cleanIdUnderscore] ||
        pluginsInstalled[item.name] ||
        Object.keys(pluginsInstalled).some(k => k.toLowerCase() === cleanId || k.toLowerCase() === cleanIdUnderscore)
      )) ||
      (item.type === "skill" && Boolean(
        skillsInstalled[item.id] ||
        skillsInstalled[cleanId] ||
        skillsInstalled[cleanIdUnderscore] ||
        skillsInstalled[item.name] ||
        Object.keys(skillsInstalled).some(k => k.toLowerCase() === cleanId || k.toLowerCase() === cleanIdUnderscore)
      ));

    card.innerHTML = `
      <div class="card-header-row">
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:20px;">${item.icon || "📦"}</span>
          <span class="card-type-badge ${typeClass}">${item.type.toUpperCase()}</span>
          ${item.category ? `<span style="font-size:10px;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">${escapeHtml(item.category)}</span>` : ""}
        </div>
        ${isInstalled ? '<span class="installed-badge">✔ Installed</span>' : ""}
      </div>
      <div class="card-name" style="margin-top:4px;">${escapeHtml(item.name || item.id)}</div>
      <div class="card-desc">${escapeHtml(item.description || "")}</div>
      <div class="card-footer">
        <span class="card-author">${item.author ? `By ${escapeHtml(item.author)}` : ""}</span>
        ${item.source_url ? `<a href="${item.source_url}" target="_blank" rel="noopener noreferrer" style="font-size:11px;color:var(--accent-primary);text-decoration:none;margin-left:8px;margin-right:auto;" title="View on GitHub">GitHub ↗</a>` : ""}
        ${isInstalled
          ? `<button class="btn btn-sm btn-secondary catalog-action-btn installed" disabled style="opacity:0.85;cursor:default;">✔ Installed</button>`
          : `<button class="btn btn-sm btn-primary catalog-action-btn" data-id="${item.id}" data-type="${item.type}">Install</button>`
        }
      </div>
    `;

    if (!isInstalled) {
      const actionBtn = card.querySelector(".catalog-action-btn");
      actionBtn.addEventListener("click", async () => {
        actionBtn.disabled = true;
        actionBtn.textContent = "Installing...";
        try {
          await apiFetch("/api/marketplace/install", {
            method: "POST",
            body: JSON.stringify({
              type: item.type,
              id: item.id,
              name: item.name,
              source_url: item.source_url,
              config: item.config,
            }),
          });
          // Immediately record as installed in client state
          if (!state.installedPackages[item.type]) {
            state.installedPackages[item.type] = {};
          }
          state.installedPackages[item.type][item.id] = { id: item.id, name: item.name };

          // Immediately update the card UI to show installed state (fixes button staying "Install")
          actionBtn.textContent = "✔ Installed";
          actionBtn.classList.remove("btn-primary");
          actionBtn.classList.add("btn-secondary", "installed");
          actionBtn.style.opacity = "0.85";
          actionBtn.style.cursor = "default";
          // Also add the installed badge to the card header if not already there
          const cardHeaderRow = card.querySelector(".card-header-row");
          if (cardHeaderRow && !cardHeaderRow.querySelector(".installed-badge")) {
            const badge = document.createElement("span");
            badge.className = "installed-badge";
            badge.textContent = "✔ Installed";
            cardHeaderRow.appendChild(badge);
          }

          await loadMCPStatus();
          await loadSkills();
          // Refresh catalog in background to sync full installed state
          loadMarketplaceCatalog();
        } catch (err) {
          alert("Installation failed: " + err.message);
          actionBtn.disabled = false;
          actionBtn.textContent = "Install";
        }
      });
    }

    elements.catalogGrid.appendChild(card);
  });
}

async function loadInstalledPackages() {
  try {
    const res = await apiFetch("/api/marketplace/installed");
    state.installedPackages = res;
    renderInstalledPackages();
  } catch (err) {
    elements.installedPackagesList.innerHTML = `<div class="feedback-msg error">Failed to load installed: ${escapeHtml(err.message)}</div>`;
  }
}

function renderInstalledPackages() {
  elements.installedPackagesList.innerHTML = "";
  const allInstalled = [];

  Object.entries(state.installedPackages.mcp || {}).forEach(([id, p]) => allInstalled.push({ ...p, id, type: "mcp" }));
  Object.entries(state.installedPackages.plugins || {}).forEach(([id, p]) => allInstalled.push({ ...p, id, type: "plugin" }));
  Object.entries(state.installedPackages.skills || {}).forEach(([id, p]) => allInstalled.push({ ...p, id, type: "skill" }));

  if (allInstalled.length === 0) {
    elements.installedPackagesList.innerHTML = `
      <div style="text-align: center; padding: 32px 16px; color: var(--text-muted);">
        <p>No custom packages installed yet.</p>
        <p style="font-size: 12px;">Install community tools from the Curated Catalog or directly from any GitHub repo URL.</p>
      </div>
    `;
    return;
  }

  allInstalled.forEach((p) => {
    const row = document.createElement("div");
    row.className = "installed-item";
    const typeClass = `type-${p.type}`;
    row.innerHTML = `
      <div class="installed-item-info">
        <span class="card-type-badge ${typeClass}">${p.type.toUpperCase()}</span>
        <div>
          <div class="installed-item-name">${escapeHtml(p.name || p.id)}</div>
          <div class="installed-item-source">Source: ${escapeHtml(p.source || "config")}</div>
        </div>
      </div>
      <button class="btn btn-danger btn-sm uninstall-pkg-btn" data-type="${p.type}" data-id="${p.id}">Uninstall</button>
    `;

    row.querySelector(".uninstall-pkg-btn").addEventListener("click", async () => {
      if (confirm(`Uninstall ${p.name || p.id}?`)) {
        try {
          await apiFetch("/api/marketplace/uninstall", {
            method: "POST",
            body: JSON.stringify({ type: p.type, id: p.id }),
          });
          await loadInstalledPackages();
          await loadMCPStatus();
          await loadSkills();
          await loadMarketplaceCatalog();
        } catch (err) {
          alert("Uninstall failed: " + err.message);
        }
      }
    });

    elements.installedPackagesList.appendChild(row);
  });
}

// Event Listeners
function setupEventListeners() {
  // Chat Input
  elements.chatTextarea.addEventListener("input", () => {
    elements.chatTextarea.style.height = "auto";
    elements.chatTextarea.style.height = elements.chatTextarea.scrollHeight + "px";
  });

  elements.chatTextarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  elements.sendBtn.addEventListener("click", handleSend);

  // New Chat
  elements.newChatBtn.addEventListener("click", async () => {
    try {
      const res = await apiFetch("/api/sessions", {
        method: "POST",
        body: JSON.stringify({ title: "New Conversation" }),
      });
      await loadSessions();
      selectSession(res.session.id, res.session.title);
    } catch (e) {
      alert("Failed to create session: " + e.message);
    }
  });

  // Suggestion Cards
  document.querySelectorAll(".suggestion-card").forEach((card) => {
    card.addEventListener("click", () => {
      elements.chatTextarea.value = card.dataset.prompt;
      handleSend();
    });
  });

  // Reload MCP
  if (elements.reloadMcpBtn) {
    elements.reloadMcpBtn.addEventListener("click", async () => {
      if (elements.mcpToolCount) elements.mcpToolCount.textContent = "Reloading...";
      try {
        await apiFetch("/api/mcp/reload", { method: "POST" });
        await loadMCPStatus();
      } catch (err) {
        alert("Reload failed: " + err.message);
      }
    });
  }

  // Sidebar toggle
  elements.toggleSidebarBtn.addEventListener("click", () => {
    const isHidden = elements.sidebar.style.display === "none";
    elements.sidebar.style.display = isHidden ? "flex" : "none";
  });

  // ==================== Marketplace Modal Events ====================
  const openMarketplace = async () => {
    elements.marketplaceModal.classList.add("open");
    await loadMarketplaceCatalog();
  };

  if (elements.marketplaceModalBtn) elements.marketplaceModalBtn.addEventListener("click", openMarketplace);
  if (elements.navMarketplaceBtn) elements.navMarketplaceBtn.addEventListener("click", openMarketplace);

  if (elements.marketplaceModalClose) {
    elements.marketplaceModalClose.addEventListener("click", () => {
      elements.marketplaceModal.classList.remove("open");
    });
  }

  // Marketplace Tabs
  const switchMarketTab = (activeTabBtn, activePane) => {
    [elements.tabBtnCatalog, elements.tabBtnCustom, elements.tabBtnInstalled].forEach((b) => b.classList.remove("active"));
    [elements.paneCatalog, elements.paneCustom, elements.paneInstalled].forEach((p) => p.classList.remove("active"));
    activeTabBtn.classList.add("active");
    activePane.classList.add("active");
  };

  elements.tabBtnCatalog.addEventListener("click", () => switchMarketTab(elements.tabBtnCatalog, elements.paneCatalog));
  elements.tabBtnCustom.addEventListener("click", () => switchMarketTab(elements.tabBtnCustom, elements.paneCustom));
  elements.tabBtnInstalled.addEventListener("click", () => {
    switchMarketTab(elements.tabBtnInstalled, elements.paneInstalled);
    loadInstalledPackages();
  });

  // Marketplace Catalog Filters & Search
  document.querySelectorAll("#pane-catalog .filter-pills .pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      document.querySelectorAll("#pane-catalog .filter-pills .pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      state.currentMarketFilter = pill.dataset.filter;
      renderCatalog();
    });
  });

  elements.catalogSearch.addEventListener("input", renderCatalog);

  // Custom Install Type Switching
  elements.customInstallType.addEventListener("change", () => {
    const val = elements.customInstallType.value;
    if (val === "mcp") {
      elements.mcpConfigGroup.style.display = "flex";
      elements.codeContentGroup.style.display = "none";
    } else {
      elements.mcpConfigGroup.style.display = "none";
      elements.codeContentGroup.style.display = "flex";
    }
  });

  // Custom Install Form Submission
  elements.customInstallForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const type = elements.customInstallType.value;
    const name = elements.customInstallName.value.trim();
    const url = elements.customInstallUrl.value.trim();
    const configRaw = elements.customInstallConfig.value.trim();
    const code = elements.customInstallCode.value.trim();

    let config = null;
    if (configRaw) {
      try {
        config = JSON.parse(configRaw);
      } catch (_) {
        elements.customInstallFeedback.className = "feedback-msg error";
        elements.customInstallFeedback.textContent = "Invalid JSON in MCP configuration.";
        return;
      }
    }

    elements.customInstallBtn.disabled = true;
    elements.customInstallBtn.textContent = "Installing...";
    elements.customInstallFeedback.className = "feedback-msg";
    elements.customInstallFeedback.style.display = "none";

    try {
      await apiFetch("/api/marketplace/install", {
        method: "POST",
        body: JSON.stringify({
          type,
          name,
          id: name,
          source_url: url || undefined,
          code: code || undefined,
          config: config || undefined,
        }),
      });

      elements.customInstallFeedback.className = "feedback-msg success";
      elements.customInstallFeedback.textContent = `Successfully installed ${name}!`;
      elements.customInstallForm.reset();
      await loadMCPStatus();
      await loadSkills();
      await loadMarketplaceCatalog();
      setTimeout(() => switchMarketTab(elements.tabBtnInstalled, elements.paneInstalled), 1200);
    } catch (err) {
      elements.customInstallFeedback.className = "feedback-msg error";
      elements.customInstallFeedback.textContent = "Error: " + err.message;
    } finally {
      elements.customInstallBtn.disabled = false;
      elements.customInstallBtn.textContent = "Install Package";
    }
  });

  // ==================== Memory Modal Events ====================
  const openMemoryModal = async () => {
    elements.memoryModal.classList.add("open");
    await loadMemories(state.currentMemoryCategory);
  };

  if (elements.memoryModalBtn) elements.memoryModalBtn.addEventListener("click", openMemoryModal);
  if (elements.navMemoryBtn) elements.navMemoryBtn.addEventListener("click", openMemoryModal);

  if (elements.memoryModalClose) {
    elements.memoryModalClose.addEventListener("click", () => {
      elements.memoryModal.classList.remove("open");
    });
  }

  // Memory Category Filters
  document.querySelectorAll("#memory-category-pills .pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      document.querySelectorAll("#memory-category-pills .pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      state.currentMemoryCategory = pill.dataset.cat;
      loadMemories(state.currentMemoryCategory);
    });
  });

  // Toggle Add Memory Form
  elements.toggleAddMemoryBtn.addEventListener("click", () => {
    const isHidden = elements.addMemoryPanel.style.display === "none";
    elements.addMemoryPanel.style.display = isHidden ? "block" : "none";
    if (isHidden) elements.newMemKey.focus();
  });

  elements.cancelAddMemoryBtn.addEventListener("click", () => {
    elements.addMemoryPanel.style.display = "none";
  });

  // Add Memory Form Submit
  elements.addMemoryForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const category = elements.newMemCategory.value;
    const key = elements.newMemKey.value.trim();
    const content = elements.newMemContent.value.trim();

    if (!key || !content) return;

    try {
      await apiFetch("/api/memory", {
        method: "POST",
        body: JSON.stringify({ category, key, content, source: "user_specified" }),
      });
      elements.addMemoryForm.reset();
      elements.addMemoryPanel.style.display = "none";
      await loadMemories(state.currentMemoryCategory);
    } catch (err) {
      alert("Failed to save memory: " + err.message);
    }
  });

  // Clear All Memories
  elements.clearMemoriesBtn.addEventListener("click", async () => {
    if (confirm("Are you sure you want to clear all long-term memories and self-learned rules?")) {
      try {
        await apiFetch("/api/memory/clear", { method: "POST" });
        await loadMemories(state.currentMemoryCategory);
      } catch (err) {
        alert("Failed to clear memories: " + err.message);
      }
    }
  });

  // ==================== Settings Modal (sidebar layout) ====================
  elements.settingsModalBtn.addEventListener("click", () => {
    updateAuthModalView();
    elements.settingsModal.classList.add("open");
  });
  elements.settingsModalClose.addEventListener("click", () => {
    elements.settingsModal.classList.remove("open");
  });
  // Close on backdrop click
  const settingsBackdrop = elements.settingsModal ? elements.settingsModal.querySelector(".modal-backdrop") : null;
  if (settingsBackdrop) settingsBackdrop.addEventListener("click", () => {
    elements.settingsModal.classList.remove("open");
  });

  // Settings sidebar nav switching
  function switchSettingsPanel(panelId) {
    document.querySelectorAll(".settings-nav-item").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".settings-panel").forEach(p => p.classList.remove("active"));
    const targetBtn = document.querySelector(`.settings-nav-item[data-panel="${panelId}"]`);
    const targetPanel = document.getElementById(panelId);
    if (targetBtn) targetBtn.classList.add("active");
    if (targetPanel) targetPanel.classList.add("active");
    if (panelId === "spanel-mcp") {
      const tagsEl = document.getElementById("settings-mcp-tags");
      if (tagsEl && elements.mcpServerTags) tagsEl.innerHTML = elements.mcpServerTags.innerHTML;
    }
  }
  document.querySelectorAll(".settings-nav-item").forEach(btn => {
    btn.addEventListener("click", () => switchSettingsPanel(btn.dataset.panel));
  });

  // Auth form — inside settings Account panel
  let isSignupTab = false;
  const tabSignin = document.getElementById("tab-signin");
  const tabSignup = document.getElementById("tab-signup");
  if (tabSignin) tabSignin.addEventListener("click", () => {
    isSignupTab = false;
    tabSignin.classList.add("active");
    if (tabSignup) tabSignup.classList.remove("active");
    if (elements.authSubmitBtn) elements.authSubmitBtn.textContent = "Sign In with Supabase";
  });
  if (tabSignup) tabSignup.addEventListener("click", () => {
    isSignupTab = true;
    tabSignup.classList.add("active");
    if (tabSignin) tabSignin.classList.remove("active");
    if (elements.authSubmitBtn) elements.authSubmitBtn.textContent = "Create Supabase Account";
  });

  elements.authForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const endpoint = isSignupTab ? "/api/auth/signup" : "/api/auth/signin";
    const email = elements.authEmail.value;
    const password = elements.authPassword.value;
    elements.authFeedback.className = "feedback-msg";
    elements.authFeedback.style.display = "none";

    const btn = elements.authSubmitBtn;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = `<span class="auth-spinner"></span>${isSignupTab ? "Creating Account..." : "Signing In..."}`;

    try {
      const res = await apiFetch(endpoint, { method: "POST", body: JSON.stringify({ email, password }) });
      const token = res.data?.session?.access_token;
      if (token) {
        state.token = token;
        localStorage.setItem("sb_access_token", token);
        if (state.supabaseClient) {
          try {
            state.supabaseClient.realtime.setAuth(token);
            setupRealtimeSubscriptions();
          } catch (e) {
            console.warn("Auth token setAuth error:", e);
          }
        }
      }
      elements.authFeedback.className = "feedback-msg success";
      elements.authFeedback.textContent = isSignupTab ? "Account created successfully!" : "Authenticated with Supabase!";
      await checkAuth();
      await loadSessions();
      await loadMemoriesCount();
    } catch (err) {
      elements.authFeedback.className = "feedback-msg error";
      elements.authFeedback.textContent = err.message;
    } finally {
      btn.disabled = false;
      btn.textContent = originalText;
    }
  });

  // Profile menu quick-links (inside Account panel)
  document.querySelectorAll(".sp-menu-item[data-goto]").forEach((item) => {
    item.addEventListener("click", () => {
      const targetPanel = item.getAttribute("data-goto");
      switchSettingsPanel(targetPanel);
    });
  });

  // Logout button (in Account panel)
  const spLogoutBtn = document.getElementById("sp-logout-btn");
  if (spLogoutBtn) {
    spLogoutBtn.addEventListener("click", async () => {
      const spinner = document.getElementById("sp-logout-spinner");
      spLogoutBtn.disabled = true;
      if (spinner) spinner.style.display = "inline-block";
      try { await apiFetch("/api/auth/signout", { method: "POST" }); } catch (_) { }
      state.token = "";
      state.user = { is_guest: true, email: "guest@local", role: "guest" };
      localStorage.removeItem("sb_access_token");
      if (state.supabaseClient) {
        try {
          state.supabaseClient.realtime.setAuth(state.supabaseConfig.anonKey);
          setupRealtimeSubscriptions();
        } catch (_) { }
      }
      await checkAuth();
      await loadSessions();
      await loadMemoriesCount();
      spLogoutBtn.disabled = false;
      if (spinner) spinner.style.display = "none";
    });
  }

  // Extensions & MCP quick-nav buttons
  const settingsOpenMarketplace = document.getElementById("settings-open-marketplace");
  const settingsOpenMemory = document.getElementById("settings-open-memory");
  const settingsOpenMarketplaceMcp = document.getElementById("settings-open-marketplace-mcp");
  if (settingsOpenMarketplace) settingsOpenMarketplace.addEventListener("click", async () => {
    elements.settingsModal.classList.remove("open");
    elements.marketplaceModal.classList.add("open");
    await loadMarketplaceCatalog();
  });
  if (settingsOpenMemory) settingsOpenMemory.addEventListener("click", async () => {
    elements.settingsModal.classList.remove("open");
    elements.memoryModal.classList.add("open");
    await loadMemories(state.currentMemoryCategory);
  });
  if (settingsOpenMarketplaceMcp) settingsOpenMarketplaceMcp.addEventListener("click", async () => {
    elements.settingsModal.classList.remove("open");
    elements.marketplaceModal.classList.add("open");
    await loadMarketplaceCatalog();
  });

  // Agent Config form
  elements.settingsForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      model: elements.settingModel.value,
      temperature: parseFloat(elements.settingTemp.value),
      base_url: elements.settingBaseUrl.value,
      api_key: elements.settingApiKey.value || undefined,
      supabase_url: elements.settingSupabaseUrl.value || undefined,
      supabase_anon_key: elements.settingSupabaseAnonKey.value || undefined,
    };
    elements.settingsFeedback.className = "feedback-msg";
    try {
      await apiFetch("/api/settings", { method: "POST", body: JSON.stringify(payload) });
      elements.settingsFeedback.className = "feedback-msg success";
      elements.settingsFeedback.textContent = "Settings updated successfully!";
      await loadInfo();
      if (payload.supabase_url && payload.supabase_anon_key) {
        initSupabaseRealtime(payload.supabase_url, payload.supabase_anon_key);
      }
    } catch (err) {
      elements.settingsFeedback.className = "feedback-msg error";
      elements.settingsFeedback.textContent = err.message;
    }
  });

  // Reconnect realtime on clicking badge if offline
  if (elements.realtimeStatusBadge) {
    elements.realtimeStatusBadge.style.cursor = "pointer";
    elements.realtimeStatusBadge.addEventListener("click", () => {
      if (state.supabaseConfig.url && state.supabaseConfig.anonKey) {
        initSupabaseRealtime(state.supabaseConfig.url, state.supabaseConfig.anonKey);
      }
    });
  }
}

// Run app
document.addEventListener("DOMContentLoaded", initApp);
