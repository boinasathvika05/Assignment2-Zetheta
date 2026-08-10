document.addEventListener("DOMContentLoaded", () => {
  let conversationId = null;
  let authToken = null;
  let currentUser = {
    name: "Sathvika Sharma",
    email: "customer@nexbank.in",
    role: "CUSTOMER"
  };

  let bankProfile = {
    custName: "Sathvika Sharma",
    custId: "CUST-882194",
    accNum: "110294817502",
    accType: "Savings Account",
    accBal: "128450.00",
    cardNum: "4532 1111 2222 4521",
    cardStatus: "ACTIVE",
    ifsc: "NXBK0008821"
  };

  // Load saved bank profile from LocalStorage if available
  const savedProfile = localStorage.getItem("nexbank_user_bank_profile");
  if (savedProfile) {
    try {
      bankProfile = JSON.parse(savedProfile);
    } catch (e) {
      console.warn("Could not parse saved bank profile.");
    }
  }

  // Update UI with Current Bank Profile
  function updateBankProfileUI() {
    document.getElementById("disp-acc-num").textContent = bankProfile.accNum;
    document.getElementById("disp-acc-bal").textContent = `₹ ${parseFloat(bankProfile.accBal).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
    document.getElementById("disp-acc-type").textContent = bankProfile.accType;
    document.getElementById("disp-cust-id").textContent = bankProfile.custId;
    document.getElementById("disp-ifsc").textContent = bankProfile.ifsc;

    // Card widget
    const last4 = bankProfile.cardNum.slice(-4) || "4521";
    document.getElementById("card-display-number").textContent = `•••• •••• •••• ${last4}`;
    document.getElementById("card-display-status").textContent = bankProfile.cardStatus;
    if (bankProfile.cardStatus === "BLOCKED") {
      document.getElementById("card-display-status").className = "text-danger";
    } else {
      document.getElementById("card-display-status").className = "text-success";
    }

    // Populate Input fields
    document.getElementById("input-cust-name").value = bankProfile.custName;
    document.getElementById("input-cust-id").value = bankProfile.custId;
    document.getElementById("input-acc-num").value = bankProfile.accNum;
    document.getElementById("input-acc-type").value = bankProfile.accType;
    document.getElementById("input-acc-bal").value = bankProfile.accBal;
    document.getElementById("input-card-num").value = bankProfile.cardNum;
    document.getElementById("input-card-status").value = bankProfile.cardStatus;
    document.getElementById("input-ifsc").value = bankProfile.ifsc;
  }

  updateBankProfileUI();

  // Bank Profile Form Toggle
  const btnToggleBank = document.getElementById("btn-toggle-edit-bank");
  const formBankDetails = document.getElementById("form-bank-details");

  btnToggleBank.addEventListener("click", () => {
    formBankDetails.classList.toggle("hidden");
    btnToggleBank.textContent = formBankDetails.classList.contains("hidden") 
      ? "⚙️ Edit Bank & Account Details" 
      : "✖ Close Bank Details Form";
  });

  // Save Bank Profile Submit
  formBankDetails.addEventListener("submit", (e) => {
    e.preventDefault();
    bankProfile.custName = document.getElementById("input-cust-name").value.trim();
    bankProfile.custId = document.getElementById("input-cust-id").value.trim();
    bankProfile.accNum = document.getElementById("input-acc-num").value.trim();
    bankProfile.accType = document.getElementById("input-acc-type").value;
    bankProfile.accBal = document.getElementById("input-acc-bal").value.trim();
    bankProfile.cardNum = document.getElementById("input-card-num").value.trim();
    bankProfile.cardStatus = document.getElementById("input-card-status").value;
    bankProfile.ifsc = document.getElementById("input-ifsc").value.trim();

    localStorage.setItem("nexbank_user_bank_profile", JSON.stringify(bankProfile));
    updateBankProfileUI();
    formBankDetails.classList.add("hidden");
    btnToggleBank.textContent = "⚙️ Edit Bank & Account Details";

    alert("✅ Bank Profile Updated Successfully! AI Assistant will now reference your updated account details.");
  });

  // Navigation Tabs
  const navItems = document.querySelectorAll(".nav-item");
  const tabContents = document.querySelectorAll(".tab-content");
  const pageTitle = document.getElementById("page-title");
  const pageSubtitle = document.getElementById("page-subtitle");

  const tabTitles = {
    customer: { title: "Customer AI Assistant", sub: "Interactive Banking Agent with Hybrid RAG & Real-Time Security" },
    supervisor: { title: "Supervisor Operations Console", sub: "15 Escalation Triggers, SLA Monitoring & Human Handoff Queue" },
    analytics: { title: "Executive Analytics & CSAT Monitor", sub: "Real-time CSAT Tracking, Containment Rate & Latency Metrics" },
    guardrail: { title: "Safety & Compliance Guardrails", sub: "Prompt Injection Protection, PII Redaction & SEBI Compliance" },
    admin: { title: "Admin & RAG Infrastructure", sub: "Vector Database Seeding, Version Control & System Diagnostics" }
  };

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const targetTab = item.getAttribute("data-tab");
      navItems.forEach(i => i.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      item.classList.add("active");
      document.getElementById(`tab-${targetTab}`).classList.add("active");

      if (tabTitles[targetTab]) {
        pageTitle.textContent = tabTitles[targetTab].title;
        pageSubtitle.textContent = tabTitles[targetTab].sub;
      }

      if (targetTab === "supervisor") loadEscalations();
      if (targetTab === "analytics") loadMetrics();
    });
  });

  // Auth Modal Elements
  const authModal = document.getElementById("auth-modal");
  const btnOpenAuth = document.getElementById("btn-open-auth");
  const btnCloseAuth = document.getElementById("btn-close-auth");
  const tabBtnLogin = document.getElementById("tab-btn-login");
  const tabBtnRegister = document.getElementById("tab-btn-register");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");

  btnOpenAuth.addEventListener("click", () => authModal.classList.remove("hidden"));
  btnCloseAuth.addEventListener("click", () => authModal.classList.add("hidden"));

  tabBtnLogin.addEventListener("click", () => {
    tabBtnLogin.classList.add("active");
    tabBtnRegister.classList.remove("active");
    formLogin.classList.remove("hidden");
    formRegister.classList.add("hidden");
  });

  tabBtnRegister.addEventListener("click", () => {
    tabBtnRegister.classList.add("active");
    tabBtnLogin.classList.remove("active");
    formRegister.classList.remove("hidden");
    formLogin.classList.add("hidden");
  });

  window.fillAuthPreset = (email, password, role) => {
    document.getElementById("login-email").value = email;
    document.getElementById("login-password").value = password;
    document.getElementById("login-role").value = role;
  };

  // Login Submit
  formLogin.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    const role = document.getElementById("login-role").value;

    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        authToken = data.data.access_token;
        currentUser = {
          name: data.data.user.full_name || email.split("@")[0],
          email: email,
          role: role
        };
        updateHeaderUserBadge();
        authModal.classList.add("hidden");
        await startNewChatSession();
        alert(`Logged in successfully as ${currentUser.name} [${currentUser.role}]`);
      } else {
        alert(data.detail || "Invalid login credentials.");
      }
    } catch (err) {
      alert("Network error during login.");
    }
  });

  // Register Submit
  formRegister.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const role = document.getElementById("reg-role").value;
    const phone = document.getElementById("reg-phone").value.trim();

    try {
      const regRes = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: name, role, phone_number: phone })
      });
      const regData = await regRes.json();
      if (regRes.ok && regData.success) {
        // Log in
        const loginRes = await fetch("/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        });
        const loginData = await loginRes.json();
        authToken = loginData.data.access_token;
        currentUser = { name, email, role };
        updateHeaderUserBadge();
        authModal.classList.add("hidden");
        await startNewChatSession();
        alert(`Account created! Logged in as ${name} [${role}]`);
      } else {
        alert(regData.detail || "Registration failed.");
      }
    } catch (err) {
      alert("Network error during registration.");
    }
  });

  function updateHeaderUserBadge() {
    document.getElementById("display-user-role").textContent = `Role: ${currentUser.role}`;
    document.getElementById("display-user-name").textContent = `${currentUser.name}`;
  }

  // Chat Elements
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const btnSend = document.getElementById("btn-send");
  const btnSeed = document.getElementById("btn-seed-kb");
  const btnResetChat = document.getElementById("btn-reset-chat");

  async function startNewChatSession() {
    try {
      const startRes = await fetch("/api/v1/chat/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {})
        },
        body: JSON.stringify({ channel: "web" })
      });
      const startData = await startRes.json();
      if (startData.data) {
        conversationId = startData.data.conversation_id;
      }
    } catch (e) {
      console.warn("Start chat session fallback:", e);
    }
  }

  // Reset Chat Session
  btnResetChat.addEventListener("click", async () => {
    chatMessages.innerHTML = `
      <div class="message bot">
        <div class="message-content">
          👋 Welcome to NexBank Digital Banking! How may I assist you with your savings account, debit card, or transaction history today?
        </div>
        <span class="message-time">Just now</span>
      </div>
    `;
    await startNewChatSession();
  });

  // Auto-init Auth & Chat Session
  async function initSession() {
    try {
      // Auto login default demo user
      const loginRes = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "customer@nexbank.in", password: "Password123!" })
      });

      if (loginRes.ok) {
        const data = await loginRes.json();
        authToken = data.data.access_token;
      } else {
        await fetch("/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "customer@nexbank.in", password: "Password123!", full_name: "Sathvika Sharma", role: "CUSTOMER" })
        });
        const relogin = await fetch("/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "customer@nexbank.in", password: "Password123!" })
        });
        const reloginData = await relogin.json();
        authToken = reloginData.data.access_token;
      }

      await startNewChatSession();
    } catch (e) {
      console.warn("Session init fallback:", e);
    }
  }

  initSession();

  // Send Chat Turn
  async function sendMessage(text) {
    const userText = text || chatInput.value.trim();
    if (!userText) return;

    chatInput.value = "";
    appendMessage(userText, "user");

    try {
      const res = await fetch("/api/v1/chat/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {})
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: userText,
          customer_profile: bankProfile
        })
      });

      const data = await res.json();
      if (data.success && data.data) {
        if (data.data.conversation_id) {
          conversationId = data.data.conversation_id;
        }
        appendMessage(data.data.bot_response, "bot");
      } else {
        appendMessage(data.detail || "An error occurred processing your turn. Please try again.", "bot");
      }
    } catch (e) {
      appendMessage("Network timeout connecting to NexBank AI core.", "bot");
    }
  }

  function appendMessage(content, speaker) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${speaker}`;
    msgDiv.innerHTML = `
      <div class="message-content">${content}</div>
      <span class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  btnSend.addEventListener("click", () => sendMessage());
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  window.sendQuickMessage = (text) => sendMessage(text);

  // Seed Knowledge Base
  btnSeed.addEventListener("click", async () => {
    try {
      btnSeed.disabled = true;
      btnSeed.textContent = "⏳ Seeding KB...";
      const res = await fetch("/api/v1/knowledge/seed", { method: "POST" });
      const data = await res.json();
      alert(data.message || "Knowledge base seeded!");
    } catch (e) {
      alert("Knowledge base seeding completed.");
    } finally {
      btnSeed.disabled = false;
      btnSeed.textContent = "🌱 Seed Knowledge Base";
    }
  });

  // Load Escalations for Supervisor Dashboard
  async function loadEscalations() {
    const tbody = document.getElementById("escalations-table-body");
    try {
      const res = await fetch("/api/v1/governance/escalations", {
        headers: authToken ? { "Authorization": `Bearer ${authToken}` } : {}
      });
      const data = await res.json();

      if (data.success && data.data && data.data.length > 0) {
        tbody.innerHTML = data.data.map(e => `
          <tr>
            <td><code>${e.id.substring(0, 8)}</code></td>
            <td><code>${e.conversation_id.substring(0, 8)}</code></td>
            <td><span class="badge badge-warning">${e.trigger_code}</span></td>
            <td><strong class="text-danger">${e.priority}</strong></td>
            <td>${e.target_queue}</td>
            <td>${e.sla_minutes} min</td>
            <td><span class="status-sub">${e.status}</span></td>
            <td><button class="btn btn-sm btn-primary">Take Handoff</button></td>
          </tr>
        `).join("");
      } else {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center">No open escalations in queue.</td></tr>`;
      }
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center">Escalation queue empty.</td></tr>`;
    }
  }

  // Load Metrics for Analytics Dashboard
  async function loadMetrics() {
    try {
      const res = await fetch("/api/v1/governance/metrics");
      const data = await res.json();
      if (data.success && data.data) {
        document.getElementById("kpi-csat").textContent = `${data.data.average_csat} / 5.0`;
        document.getElementById("kpi-model").textContent = data.data.model_version;
      }
    } catch (e) {
      console.warn("Metrics load fallback:", e);
    }
  }
});
