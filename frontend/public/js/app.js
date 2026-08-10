document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initChat();
    pollSystemHealth();
    setInterval(pollSystemHealth, 10000);
});

// Tab Switching Controller
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        });
    });
}

// System Health Polling
async function pollSystemHealth() {
    const statusBadge = document.getElementById('systemStatusBadge');
    const latencyElem = document.getElementById('systemLatency');

    const startTime = performance.now();
    try {
        const response = await fetch('/health');
        const latency = Math.round(performance.now() - startTime);
        
        if (response.ok) {
            const data = await response.json();
            if (statusBadge) {
                statusBadge.querySelector('.status-dot').className = `status-dot ${data.status}`;
                statusBadge.querySelector('.status-text').textContent = `System ${data.status.toUpperCase()}`;
            }
            if (latencyElem) {
                latencyElem.textContent = `${latency}ms`;
            }
        }
    } catch (err) {
        if (statusBadge) {
            statusBadge.querySelector('.status-dot').className = 'status-dot degraded';
            statusBadge.querySelector('.status-text').textContent = 'Local Standalone Mode';
        }
        if (latencyElem) {
            latencyElem.textContent = '0ms';
        }
    }
}

// Chat Engine Simulator
function initChat() {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const resetChatBtn = document.getElementById('resetChatBtn');

    if (sendBtn && userInput) {
        sendBtn.addEventListener('click', handleSend);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSend();
        });
    }

    if (resetChatBtn) {
        resetChatBtn.addEventListener('click', resetChat);
    }
}

function sendQuickMessage(text) {
    const input = document.getElementById('userInput');
    if (input) {
        input.value = text;
        handleSend();
    }
}

async function handleSend() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;

    appendMessage('user', text);
    input.value = '';

    // Show Typing Indicator
    const typingId = showTypingIndicator();

    // Simulate Agent processing with state update
    setTimeout(() => {
        removeTypingIndicator(typingId);
        processAgentResponse(text);
    }, 800);
}

function appendMessage(sender, text) {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender === 'user' ? 'user-msg' : 'bot-msg'}`;

    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

    if (sender === 'user') {
        msgDiv.innerHTML = `
            <div class="msg-bubble">
                <p>${escapeHtml(text)}</p>
                <span class="msg-time">${timeStr}</span>
            </div>
        `;
    } else {
        msgDiv.innerHTML = `
            <div class="msg-avatar">🤖</div>
            <div class="msg-bubble">
                <p>${text}</p>
                <span class="msg-time">${timeStr}</span>
            </div>
        `;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const id = 'typing_' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message bot-msg';
    div.innerHTML = `
        <div class="msg-avatar">🤖</div>
        <div class="msg-bubble" style="color: var(--text-muted);">
            <i>NexBank Agent is reasoning & running guardrail scans...</i>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const elem = document.getElementById(id);
    if (elem) elem.remove();
}

function processAgentResponse(input) {
    const lower = input.toLowerCase();

    // Guardrail Trigger Test: Financial Advice
    if (lower.includes('invest') || lower.includes('should i put')) {
        updateState('PRD-005', 0.88, 'Financial Advice Guardrail ACTIVE');
        appendMessage('bot', `That's a great question about putting your savings to work! I can share factual information about our Fixed Deposits (rates from 6.0% to 7.25%) and partner Mutual Funds. However, choosing between them depends on your personal financial situation and goals — which requires a certified financial advisor.<br><br><em>[GUARDRAIL ENFORCED: Personalised investment recommendation blocked under SEBI Robo-Advisory Guidelines]</em><br><br>Would you like me to connect you with a SEBI-registered NexBank wealth advisor for a free 30-minute consultation?`);
        return;
    }

    // Guardrail Trigger Test: Prompt Injection
    if (lower.includes('ignore previous') || lower.includes('admin data')) {
        updateState('SEC-004', 0.96, 'ADVERSARIAL INJECTION DETECTED');
        appendMessage('bot', `🛡️ <strong>SECURITY ALERT:</strong> Malicious instruction sequence detected and neutralised. I am NexBank's AI Assistant, designed strictly to assist customers with authorized banking queries.<br><br>This incident has been logged with Correlation ID for Security Operations audit.`);
        return;
    }

    // Fraud / Dispute Flow
    if (lower.includes('unauthorized') || lower.includes('charge') || lower.includes('dispute')) {
        updateState('SEC-001', 0.91, 'P0 Escalation Initiated');
        appendMessage('bot', `I understand your concern regarding this unexpected charge of ₹15,000. Let me help right away.<br><br>I am taking two immediate protective actions:<br>1. Initiating a temporary security block on your card ending in 4521 to prevent any further charges.<br>2. Escalating this issue directly to our Fraud Investigation Team with Priority 0.<br><br>NexBank's zero-liability policy protects you against unauthorized transactions. Connecting to specialist now...`);
        return;
    }

    // Default Balance Query
    updateState('ACC-001', 0.94, 'OTP-Verified Required');
    appendMessage('bot', `I'd be happy to help check your account balance. For your protection under PCI DSS & RBI rules, please verify your identity.<br><br>I've sent a 6-digit OTP to your registered mobile number ending in <strong>3210</strong>. Please enter the OTP to proceed.`);
}

function updateState(intent, conf, extra) {
    const intentElem = document.getElementById('currentIntent');
    const confFill = document.getElementById('intentConfFill');
    const confScore = document.getElementById('intentConfScore');

    if (intentElem) intentElem.textContent = `${intent}`;
    if (confFill) confFill.style.width = `${Math.round(conf * 100)}%`;
    if (confScore) confScore.textContent = `${conf} (${extra})`;
}

function resetChat() {
    const container = document.getElementById('chatMessages');
    if (container) {
        container.innerHTML = `
            <div class="message system-msg">
                <div class="msg-content">
                    🔒 <strong>Secure Session Reset.</strong> New dialogue state initialized.
                </div>
            </div>
            <div class="message bot-msg">
                <div class="msg-avatar">🤖</div>
                <div class="msg-bubble">
                    <p>Hello! Welcome to NexBank. I'm your AI banking assistant. How can I help you today with your accounts, payments, or banking services?</p>
                    <span class="msg-time">18:15</span>
                </div>
            </div>
        `;
    }
}

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
