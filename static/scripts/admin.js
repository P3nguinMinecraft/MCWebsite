// ── Tab switching ─────────────────────────────────────────────────────────────
function switchTab(tabId) {
    document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.admin-tab-pane').forEach(p => p.classList.remove('active'));
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
    history.replaceState(null, '', `#${tabId}`);
}

// ── Notifications ─────────────────────────────────────────────────────────────
function showNotification(message, type) {
    const n = document.createElement('div');
    n.className = `notification notification-${type}`;
    n.textContent = message;
    document.body.appendChild(n);
    setTimeout(() => n.classList.add('show'), 10);
    setTimeout(() => { n.classList.remove('show'); setTimeout(() => n.remove(), 300); }, 3000);
}

// ── Generic save helper ───────────────────────────────────────────────────────
async function apiPost(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 1 — Server Details
// ═══════════════════════════════════════════════════════════════════════════════
function createDetailRow(label, value) {
    const row = document.createElement('div');
    row.className = 'info-row-editor';
    row.innerHTML = `
        <input type="text" class="editor-input label-input" placeholder="Label" value="${escAttr(label)}">
        <input type="text" class="editor-input value-input" placeholder="Value  —  use {ip} or {name}" value="${escAttr(value)}">
        <button class="icon-btn delete-row-btn" title="Remove row" onclick="this.closest('.info-row-editor').remove()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>`;
    return row;
}

function addDetailRow() {
    document.getElementById('detailRows').appendChild(createDetailRow('', ''));
}

async function loadDetails() {
    const data = await (await fetch('/admin/api/details')).json();
    const container = document.getElementById('detailRows');
    container.innerHTML = '';
    (data.info_rows || []).forEach(r => container.appendChild(createDetailRow(r.label, r.value)));
}

async function saveDetails() {
    const rows = [...document.querySelectorAll('#detailRows .info-row-editor')].map(row => ({
        label: row.querySelector('.label-input').value,
        value: row.querySelector('.value-input').value
    }));
    const result = await apiPost('/admin/api/details', { info_rows: rows });
    showNotification(result.success ? 'Server details saved!' : 'Save failed', result.success ? 'success' : 'error');
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 2 — Mods
// ═══════════════════════════════════════════════════════════════════════════════
async function loadMods() {
    const data = await (await fetch('/admin/api/mods')).json();
    document.getElementById('modsTextarea').value = data.content || '';
}

async function saveMods() {
    const content = document.getElementById('modsTextarea').value;
    const result  = await apiPost('/admin/api/mods', { content });
    showNotification(result.success ? 'Mods saved!' : 'Save failed', result.success ? 'success' : 'error');
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 3 — Additional Info
// ═══════════════════════════════════════════════════════════════════════════════
function createCustomRow(label, value) {
    const row = document.createElement('div');
    row.className = 'info-row-editor';
    row.innerHTML = `
        <input type="text" class="editor-input label-input" placeholder="Label" value="${escAttr(label)}">
        <input type="text" class="editor-input value-input" placeholder="Value" value="${escAttr(value)}">
        <button class="icon-btn delete-row-btn" title="Remove row" onclick="this.closest('.info-row-editor').remove()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>`;
    return row;
}

function createSection(name, rows) {
    const section = document.createElement('div');
    section.className = 'custom-section';
    section.innerHTML = `
        <div class="custom-section-header">
            <input type="text" class="editor-input section-name-input" placeholder="Section name" value="${escAttr(name)}">
            <button class="icon-btn delete-section-btn" title="Delete section" onclick="deleteSection(this)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
            </button>
        </div>
        <div class="custom-section-rows"></div>
        <button class="add-row-btn" onclick="addCustomRow(this)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Add Row
        </button>`;

    const rowContainer = section.querySelector('.custom-section-rows');
    (rows || []).forEach(r => rowContainer.appendChild(createCustomRow(r.label, r.value)));
    return section;
}

function deleteSection(btn) {
    btn.closest('.custom-section').remove();
}

function addCustomRow(btn) {
    btn.previousElementSibling.appendChild(createCustomRow('', ''));
}

function addSection() {
    document.getElementById('customSections').appendChild(createSection('New Section', []));
}

async function loadCustom() {
    const data = await (await fetch('/admin/api/custom')).json();
    const container = document.getElementById('customSections');
    container.innerHTML = '';
    (data.sections || []).forEach(s => container.appendChild(createSection(s.name, s.rows)));
}

async function saveCustom() {
    const sections = [...document.querySelectorAll('#customSections .custom-section')].map(sec => ({
        name: sec.querySelector('.section-name-input').value,
        rows: [...sec.querySelectorAll('.info-row-editor')].map(row => ({
            label: row.querySelector('.label-input').value,
            value: row.querySelector('.value-input').value
        }))
    }));
    const result = await apiPost('/admin/api/custom', { sections });
    showNotification(result.success ? 'Additional info saved!' : 'Save failed', result.success ? 'success' : 'error');
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 4 — Config
// ═══════════════════════════════════════════════════════════════════════════════
function createExtRow(ext) {
    const row = document.createElement('div');
    row.className = 'ext-row';
    row.innerHTML = `
        <input type="text" class="editor-input ext-input" value="${escAttr(ext)}" placeholder="e.g. png">
        <button class="icon-btn delete-row-btn" title="Remove" onclick="this.closest('.ext-row').remove()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>`;
    return row;
}

function addExtRow() {
    document.getElementById('extensionsList').appendChild(createExtRow(''));
}

async function loadConfig() {
    const data = await (await fetch('/admin/api/config')).json();

    document.getElementById('cfgName').value      = data.server_name    || '';
    document.getElementById('cfgIp').value        = data.server_ip      || '';
    document.getElementById('cfgDiscord').value   = data.discord_invite || '';
    document.getElementById('cfgFileSize').value  = data.max_file_size  || 20;
    document.getElementById('cfgSizeUnit').value  = (data.file_size_unit || 'MB').toUpperCase();

    const list = document.getElementById('extensionsList');
    list.innerHTML = '';
    (data.allowed_extensions || []).forEach(e => list.appendChild(createExtRow(e)));
}

async function saveConfig() {
    const extensions = [...document.querySelectorAll('#extensionsList .ext-input')]
        .map(i => i.value.trim().toLowerCase())
        .filter(Boolean);

    const payload = {
        server_name:       document.getElementById('cfgName').value,
        server_ip:         document.getElementById('cfgIp').value,
        discord_invite:    document.getElementById('cfgDiscord').value,
        max_file_size:     parseInt(document.getElementById('cfgFileSize').value, 10) || 20,
        file_size_unit:    document.getElementById('cfgSizeUnit').value,
        allowed_extensions: extensions
    };

    const result = await apiPost('/admin/api/config', payload);
    showNotification(result.success ? 'Config saved!' : 'Save failed', result.success ? 'success' : 'error');
}

// ── Escape helpers ────────────────────────────────────────────────────────────
function escAttr(str) {
    return String(str || '')
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadDetails();
    loadMods();
    loadCustom();
    loadConfig();

    // Restore tab from URL hash
    const hash = location.hash.replace('#', '');
    if (hash && document.getElementById(hash)) {
        switchTab(hash);
    }
});
