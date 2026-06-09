"use strict";
const STORAGE_KEY = 'ai_tracker_db_v2';
const TOTALS = { c1: 8, c2: 6, c3: 8, cap: 4 };
// ── In-memory state (source of truth for the UI) ──────────────────────────
let currentData = {};
let isDirty = false;
// ── SQLite ────────────────────────────────────────────────────────────────
let sqlDb = null;
function uint8ToBase64(data) {
    let str = '';
    for (let i = 0; i < data.length; i++)
        str += String.fromCharCode(data[i]);
    return btoa(str);
}
function persistDb() {
    if (!sqlDb)
        return;
    localStorage.setItem(STORAGE_KEY, uint8ToBase64(sqlDb.export()));
}
async function initDb() {
    const SQL = await initSqlJs({
        locateFile: (file) => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/${file}`,
    });
    const saved = localStorage.getItem(STORAGE_KEY);
    // Detect old JSON format and migrate
    let legacy = null;
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
                legacy = parsed;
            }
        }
        catch { /* base64 SQLite binary — not JSON */ }
    }
    if (saved && !legacy) {
        try {
            const buf = Uint8Array.from(atob(saved), c => c.charCodeAt(0));
            sqlDb = new SQL.Database(buf);
        }
        catch {
            sqlDb = new SQL.Database();
        }
    }
    else {
        sqlDb = new SQL.Database();
    }
    sqlDb.run(`
    CREATE TABLE IF NOT EXISTS progress (
      module_id  TEXT    PRIMARY KEY,
      completed  INTEGER NOT NULL DEFAULT 0,
      updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
    )
  `);
    if (legacy) {
        for (const [id, completed] of Object.entries(legacy)) {
            sqlDb.run(`INSERT OR REPLACE INTO progress (module_id, completed) VALUES (?, ?)`, [id, completed ? 1 : 0]);
        }
        localStorage.removeItem('ai_tracker_v1');
        persistDb();
    }
}
function dbLoadAll() {
    if (!sqlDb)
        return {};
    const result = {};
    const rows = sqlDb.exec('SELECT module_id, completed FROM progress');
    if (rows.length > 0) {
        for (const [id, done] of rows[0].values) {
            result[id] = done === 1;
        }
    }
    return result;
}
function dbFlushAll(data) {
    if (!sqlDb)
        return;
    sqlDb.run('DELETE FROM progress');
    for (const [id, completed] of Object.entries(data)) {
        sqlDb.run(`INSERT INTO progress (module_id, completed, updated_at)
       VALUES (?, ?, datetime('now'))`, [id, completed ? 1 : 0]);
    }
    persistDb();
}
function dbClear() {
    if (!sqlDb)
        return;
    sqlDb.run('DELETE FROM progress');
    persistDb();
}
// ── Dirty state indicator ─────────────────────────────────────────────────
function setDirty(dirty) {
    isDirty = dirty;
    const btn = document.getElementById('save-btn');
    const indicator = document.getElementById('unsaved-indicator');
    if (btn)
        btn.classList.toggle('has-changes', dirty);
    if (indicator)
        indicator.style.display = dirty ? 'inline' : 'none';
}
// ── UI ────────────────────────────────────────────────────────────────────
function applyProgress(data) {
    document.querySelectorAll('.module').forEach((module) => {
        const checked = !!data[module.id];
        module.classList.toggle('completed', checked);
        const cb = module.querySelector('input[type="checkbox"]');
        if (cb)
            cb.checked = checked;
    });
    Object.keys(TOTALS).forEach(course => updateProgress(course, data));
}
function updateProgress(course, data) {
    const d = data ?? currentData;
    const done = Object.entries(d)
        .filter(([key, val]) => key.startsWith(`mod-${course}-`) && val).length;
    const fill = document.getElementById(`prog-fill-${course}`);
    const count = document.getElementById(`prog-done-${course}`);
    if (fill)
        fill.style.width = `${Math.round((done / TOTALS[course]) * 100)}%`;
    if (count)
        count.textContent = String(done);
}
function toggleDone(id, checked, course) {
    currentData[id] = checked;
    document.getElementById(id)?.classList.toggle('completed', checked);
    updateProgress(course);
    setDirty(true);
}
function toggleModule(id) {
    document.getElementById(id)?.classList.toggle('open');
}
function switchMainTab(id) {
    if (!id)
        return;
    document.querySelectorAll('.main-tab').forEach((tab) => {
        const el = tab;
        el.classList.toggle('active', el.dataset.tab === id);
    });
    document.querySelectorAll('.main-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`tab-${id}`)?.classList.add('active');
}
function switchCourse(id) {
    if (!id)
        return;
    document.querySelectorAll('.course-tab').forEach((tab) => {
        const el = tab;
        el.classList.toggle('active', el.dataset.course === id);
    });
    document.querySelectorAll('.course-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`course-${id}`)?.classList.add('active');
}
window.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.main-tab-nav')?.addEventListener('click', (event) => {
        const tab = event.target.closest('.main-tab');
        if (!tab)
            return;
        event.preventDefault();
        switchMainTab(tab.dataset.tab || '');
    });
    document.querySelector('.course-nav')?.addEventListener('click', (event) => {
        const tab = event.target.closest('.course-tab');
        if (!tab)
            return;
        event.preventDefault();
        switchCourse(tab.dataset.course || tab.getAttribute('data-course') || '');
    });
    // Warn before leaving with unsaved changes
    window.addEventListener('beforeunload', (e) => {
        if (isDirty)
            e.preventDefault();
    });
});
function saveAll() {
    dbFlushAll(currentData);
    setDirty(false);
    const btn = document.getElementById('save-btn');
    if (btn) {
        const orig = btn.textContent || 'Save Progress';
        btn.textContent = '✓ Saved';
        btn.setAttribute('disabled', 'true');
        setTimeout(() => {
            btn.textContent = orig;
            btn.removeAttribute('disabled');
        }, 2000);
    }
}
function clearAll() {
    if (!confirm('Clear all progress? This cannot be undone.'))
        return;
    currentData = {};
    dbClear();
    document.querySelectorAll('.module').forEach((module) => {
        module.classList.remove('completed', 'open');
        const cb = module.querySelector('input[type="checkbox"]');
        if (cb)
            cb.checked = false;
    });
    Object.keys(TOTALS).forEach(course => updateProgress(course));
    setDirty(false);
}
async function init() {
    await initDb();
    currentData = dbLoadAll();
    applyProgress(currentData);
}
init();
window.toggleDone = toggleDone;
window.toggleModule = toggleModule;
window.saveAll = saveAll;
window.clearAll = clearAll;
window.switchMainTab = switchMainTab;
window.switchCourse = switchCourse;
