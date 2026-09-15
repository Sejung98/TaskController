// Task Controller - Clean Client-Side Logic (English)

let state = {
  tasks: [],
  processes: [],
  currentTab: 'custom',
  searchQuery: '',
  statusFilter: 'all',
  isPolling: true,
  isActionPending: false
};

// DOM Elements
const statCustomCount = document.getElementById('statCustomCount');
const statRunningCount = document.getElementById('statRunningCount');
const statReadyCount = document.getElementById('statReadyCount');
const statDisabledCount = document.getElementById('statDisabledCount');
const statProcessCount = document.getElementById('statProcessCount');

const badgeCustom = document.getElementById('badgeCustom');
const badgeBatch = document.getElementById('badgeBatch');
const badgeProcesses = document.getElementById('badgeProcesses');
const badgeAll = document.getElementById('badgeAll');

const tasksView = document.getElementById('tasksView');
const processesView = document.getElementById('processesView');
const tasksList = document.getElementById('tasksList');
const emptyTasksNotice = document.getElementById('emptyTasksNotice');
const processTableBody = document.getElementById('processTableBody');
const emptyProcessNotice = document.getElementById('emptyProcessNotice');

const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const statusFilter = document.getElementById('statusFilter');
const refreshBtn = document.getElementById('refreshBtn');
const refreshProcBtn = document.getElementById('refreshProcBtn');
const toastContainer = document.getElementById('toastContainer');

const themeToggleBtn = document.getElementById('themeToggleBtn');
const themeLabel = document.getElementById('themeLabel');
const sunIcon = themeToggleBtn ? themeToggleBtn.querySelector('.sun-icon') : null;
const moonIcon = themeToggleBtn ? themeToggleBtn.querySelector('.moon-icon') : null;

// Theme Controller
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('task_controller_theme', theme);

  if (theme === 'light') {
    if (sunIcon) sunIcon.style.display = 'inline';
    if (moonIcon) moonIcon.style.display = 'none';
    if (themeLabel) themeLabel.textContent = 'Dark Mode';
  } else {
    if (sunIcon) sunIcon.style.display = 'none';
    if (moonIcon) moonIcon.style.display = 'inline';
    if (themeLabel) themeLabel.textContent = 'Light Mode';
  }
}

function initTheme() {
  const savedTheme = localStorage.getItem('task_controller_theme');
  if (savedTheme) {
    applyTheme(savedTheme);
  } else {
    const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    applyTheme(prefersLight ? 'light' : 'dark');
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      showToast(next === 'light' ? '☀️ Switched to Light Mode' : '🌙 Switched to Dark Mode', 'info');
    });
  }
}

// Toast Notification
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  let icon = 'ℹ️';
  if (type === 'success') icon = '✅';
  if (type === 'error') icon = '❌';

  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'toast-out 0.25s forwards';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// Fetch Tasks
async function fetchTasks() {
  try {
    const res = await fetch('/api/tasks');
    const data = await res.json();
    if (data.success) {
      state.tasks = data.tasks;
      updateStatsAndBadges();
      renderTasks();
    }
  } catch (err) {
    console.error('Failed to fetch tasks:', err);
  }
}

// Fetch Processes
async function fetchProcesses() {
  try {
    const res = await fetch('/api/processes');
    const data = await res.json();
    if (data.success) {
      state.processes = data.processes;
      updateStatsAndBadges();
      renderProcesses();
    }
  } catch (err) {
    console.error('Failed to fetch processes:', err);
  }
}

// Update Stats & Badges
function updateStatsAndBadges() {
  const customTasks = state.tasks.filter(t => t.is_custom);
  const batchTasks = state.tasks.filter(t => t.is_batch);
  const runningTasks = state.tasks.filter(t => t.state === 'Running');
  const readyTasks = state.tasks.filter(t => t.state === 'Ready');
  const disabledTasks = state.tasks.filter(t => t.state === 'Disabled');

  statCustomCount.textContent = customTasks.length;
  statRunningCount.textContent = runningTasks.length;
  statReadyCount.textContent = readyTasks.length;
  statDisabledCount.textContent = disabledTasks.length;
  statProcessCount.textContent = state.processes.length;

  badgeCustom.textContent = customTasks.length;
  badgeBatch.textContent = batchTasks.length;
  badgeProcesses.textContent = state.processes.length;
  badgeAll.textContent = state.tasks.length;
}

// Filter Tasks
function getFilteredTasks() {
  let list = [];
  if (state.currentTab === 'custom') {
    list = state.tasks.filter(t => t.is_custom);
  } else if (state.currentTab === 'batch') {
    list = state.tasks.filter(t => t.is_batch);
  } else if (state.currentTab === 'all') {
    list = [...state.tasks];
  } else {
    list = [];
  }

  // Status Filter
  if (state.statusFilter !== 'all') {
    list = list.filter(t => t.state === state.statusFilter);
  }

  // Search Query
  if (state.searchQuery.trim()) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(t =>
      t.name.toLowerCase().includes(q) ||
      (t.target_file && t.target_file.toLowerCase().includes(q)) ||
      (t.action && t.action.toLowerCase().includes(q))
    );
  }

  return list;
}

// Render Task Cards
function renderTasks() {
  if (state.currentTab === 'processes') return;

  const tasks = getFilteredTasks();
  tasksList.innerHTML = '';

  if (tasks.length === 0) {
    emptyTasksNotice.style.display = 'block';
    return;
  }
  emptyTasksNotice.style.display = 'none';

  tasks.forEach(t => {
    const isRunning = t.state === 'Running';
    const isReady = t.state === 'Ready';
    const isDisabled = t.state === 'Disabled';
    const isEnabled = !isDisabled;

    const stateClass = isRunning ? 'state-running' : (isReady ? 'state-ready' : 'state-disabled');
    const tagClass = isRunning ? 'running' : (isReady ? 'ready' : 'disabled');
    const tagText = isRunning ? 'Running' : (isReady ? 'Ready' : 'Disabled');

    const fileType = t.file_type ? t.file_type.toLowerCase() : 'other';
    const extClass = ['bat', 'cmd', 'py', 'ps1', 'vbs', 'exe'].includes(fileType) ? fileType : 'other';

    let outcomeClass = 'idle';
    if (t.last_result === 0) outcomeClass = 'success';
    else if (t.last_result > 0 && t.last_result !== 267011) outcomeClass = 'error';

    const card = document.createElement('div');
    card.className = `task-card ${stateClass}`;
    card.innerHTML = `
      <div class="card-head">
        <div class="card-title-box">
          <span class="ext-badge ${extClass}">${t.file_type || 'BAT'}</span>
          <h3 class="task-heading" title="${t.name}">${t.name}</h3>
        </div>
        <div class="card-head-right">
          <span class="state-tag ${tagClass}">
            <span class="tag-dot"></span>
            ${tagText}
          </span>
          <label class="ios-switch" title="${isEnabled ? 'Click to Disable (Turn Off)' : 'Click to Enable (Turn On)'}">
            <input type="checkbox" class="task-toggle" data-name="${t.name}" ${isEnabled ? 'checked' : ''}>
            <span class="ios-slider"></span>
          </label>
        </div>
      </div>

      <div class="card-content">
        <div class="path-preview" title="${t.action || t.target_file}">
          <span class="path-text">${t.target_file || t.action || 'No action command'}</span>
        </div>

        <div class="meta-row">
          <div class="meta-block">
            <span class="meta-caption">Last Run</span>
            <span class="meta-val">${t.last_run ? t.last_run.split(' ')[1] || t.last_run : 'Never'}</span>
            <span class="outcome-badge ${outcomeClass}">${t.last_result_desc}</span>
          </div>
          <div class="meta-block">
            <span class="meta-caption">Next Schedule</span>
            <span class="meta-val">${t.next_run ? t.next_run.split(' ')[1] || t.next_run : 'None'}</span>
            <span class="meta-caption" style="font-size: 10px;">${t.next_run ? t.next_run.split(' ')[0] : ''}</span>
          </div>
        </div>
      </div>

      <div class="card-footer">
        <button class="tool-btn run" data-action="run" data-name="${t.name}" title="Run Task Now">
          <svg class="btn-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          Run
        </button>
        <button class="tool-btn stop" data-action="stop" data-name="${t.name}" ${isRunning ? '' : 'disabled style="opacity: 0.35; cursor: not-allowed;"'} title="Force Stop Running Task">
          <svg class="btn-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="6" y="6" width="12" height="12"></rect>
          </svg>
          Stop
        </button>
        ${t.target_file ? `
          <button class="tool-btn" data-action="folder" data-path="${t.target_file}" title="Open File in Explorer">
            <svg class="btn-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
            Folder
          </button>
          <button class="tool-btn" data-action="edit" data-path="${t.target_file}" title="Edit Script in Notepad">
            <svg class="btn-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
            Edit
          </button>
        ` : ''}
        <button class="tool-btn delete" data-action="delete" data-name="${t.name}" data-path="${t.target_file || ''}" title="Permanently delete task from Windows Task Scheduler">
          <svg class="btn-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            <line x1="10" y1="11" x2="10" y2="17"></line>
            <line x1="14" y1="11" x2="14" y2="17"></line>
          </svg>
          Delete
        </button>
      </div>
    `;

    tasksList.appendChild(card);
  });
}

// Render Processes Table
function renderProcesses() {
  processTableBody.innerHTML = '';
  if (state.processes.length === 0) {
    emptyProcessNotice.style.display = 'block';
    return;
  }
  emptyProcessNotice.style.display = 'none';

  state.processes.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="pid-tag">${p.pid}</span></td>
      <td style="color: var(--text-sub); font-family: 'JetBrains Mono'; font-size: 12px;">${p.started || '-'}</td>
      <td><span class="cmd-pill" title="${p.cmdline}">${p.cmdline}</span></td>
      <td style="text-align: right;">
        <button class="btn-kill" data-action="kill-proc" data-pid="${p.pid}">
          Terminate
        </button>
      </td>
    `;
    processTableBody.appendChild(tr);
  });
}

// Action Handlers
async function handleToggleTask(taskName, enable) {
  state.isActionPending = true;
  try {
    const res = await fetch('/api/task/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ taskName, enable })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      await fetchTasks();
    } else {
      showToast(`Action failed: ${data.message}`, 'error');
      await fetchTasks();
    }
  } catch (err) {
    showToast(`Request error: ${err.message}`, 'error');
  } finally {
    state.isActionPending = false;
  }
}

async function handleRunTask(taskName) {
  try {
    showToast(`Starting '${taskName}'...`, 'info');
    const res = await fetch('/api/task/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ taskName })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      setTimeout(fetchTasks, 600);
    } else {
      showToast(`Execution failed: ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Request error: ${err.message}`, 'error');
  }
}

async function handleStopTask(taskName) {
  try {
    showToast(`Stopping '${taskName}'...`, 'info');
    const res = await fetch('/api/task/stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ taskName })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      setTimeout(fetchTasks, 600);
    } else {
      showToast(`Stop failed: ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Request error: ${err.message}`, 'error');
  }
}

async function handleOpenFolder(filePath) {
  try {
    const res = await fetch('/api/task/open-folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filePath })
    });
    const data = await res.json();
    if (data.success) showToast(data.message, 'success');
    else showToast(data.message, 'error');
  } catch (err) {
    showToast(`Failed: ${err.message}`, 'error');
  }
}

async function handleEditFile(filePath) {
  try {
    const res = await fetch('/api/task/edit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filePath })
    });
    const data = await res.json();
    if (data.success) showToast(data.message, 'success');
    else showToast(data.message, 'error');
  } catch (err) {
    showToast(`Failed: ${err.message}`, 'error');
  }
}

async function handleKillProcess(pid) {
  if (!confirm(`Are you sure you want to terminate process PID ${pid}?`)) return;
  try {
    const res = await fetch('/api/process/kill', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pid })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      await fetchProcesses();
    } else {
      showToast(data.message, 'error');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

async function handleDeleteTask(taskName, filePath) {
  const confirmMsg = `Are you sure you want to permanently delete '${taskName}' from Windows Task Scheduler?\n\n- OK: Permanently delete schedule\n- Cancel: Keep schedule`;
  if (!confirm(confirmMsg)) return;

  let deleteFile = false;
  if (filePath) {
    deleteFile = confirm(`[Optional File Deletion]\nDo you also want to permanently delete the script file on disk?\n\nFile Path:\n${filePath}\n\n- OK: Delete local file too\n- Cancel: Keep file safe, only unregister schedule`);
  }

  try {
    showToast(`Deleting '${taskName}'...`, 'info');
    const res = await fetch('/api/task/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ taskName, deleteFile, filePath })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      await fetchTasks();
    } else {
      showToast(`Delete failed: ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Request error: ${err.message}`, 'error');
  }
}

// Global Event Delegation for Dynamic Buttons
document.addEventListener('click', (e) => {
  const btn = e.target.closest('button');
  if (!btn) return;

  const action = btn.dataset.action;
  if (!action) return;

  if (action === 'run') {
    handleRunTask(btn.dataset.name);
  } else if (action === 'stop') {
    handleStopTask(btn.dataset.name);
  } else if (action === 'folder') {
    handleOpenFolder(btn.dataset.path);
  } else if (action === 'edit') {
    handleEditFile(btn.dataset.path);
  } else if (action === 'delete') {
    handleDeleteTask(btn.dataset.name, btn.dataset.path);
  } else if (action === 'kill-proc') {
    handleKillProcess(btn.dataset.pid);
  }
});

// Toggle Switch Listener
document.addEventListener('change', (e) => {
  if (e.target.classList.contains('task-toggle')) {
    const taskName = e.target.dataset.name;
    const isChecked = e.target.checked;
    handleToggleTask(taskName, isChecked);
  }
});

// Segmented Tab Controls
document.querySelectorAll('.segment-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    state.currentTab = btn.dataset.tab;

    if (state.currentTab === 'processes') {
      tasksView.classList.remove('active');
      processesView.classList.add('active');
      fetchProcesses();
    } else {
      processesView.classList.remove('active');
      tasksView.classList.add('active');
      renderTasks();
    }
  });
});

// Metric Cards Quick Filter
document.querySelectorAll('.metric-card').forEach(card => {
  card.addEventListener('click', () => {
    const filterType = card.dataset.filter;

    if (filterType === 'process') {
      const procTab = document.querySelector('.segment-btn[data-tab="processes"]');
      if (procTab) procTab.click();
      return;
    }

    if (filterType === 'custom') {
      const customTab = document.querySelector('.segment-btn[data-tab="custom"]');
      if (customTab) customTab.click();
      statusFilter.value = 'all';
      state.statusFilter = 'all';
      renderTasks();
      return;
    }

    // Filter by status (Running, Ready, Disabled)
    const allTab = document.querySelector('.segment-btn[data-tab="all"]');
    if (allTab) allTab.click();

    if (filterType === 'running') statusFilter.value = 'Running';
    else if (filterType === 'ready') statusFilter.value = 'Ready';
    else if (filterType === 'disabled') statusFilter.value = 'Disabled';

    state.statusFilter = statusFilter.value;
    renderTasks();
  });
});

// Search Input Listener
searchInput.addEventListener('input', (e) => {
  state.searchQuery = e.target.value;
  clearSearchBtn.style.display = state.searchQuery ? 'block' : 'none';
  renderTasks();
});

clearSearchBtn.addEventListener('click', () => {
  searchInput.value = '';
  state.searchQuery = '';
  clearSearchBtn.style.display = 'none';
  renderTasks();
});

// Status Dropdown Filter
statusFilter.addEventListener('change', (e) => {
  state.statusFilter = e.target.value;
  renderTasks();
});

// Manual Refresh Buttons
refreshBtn.addEventListener('click', async () => {
  refreshBtn.classList.add('loading');
  await Promise.all([fetchTasks(), fetchProcesses()]);
  refreshBtn.classList.remove('loading');
  showToast('Task status synchronized.', 'info');
});

refreshProcBtn.addEventListener('click', async () => {
  await fetchProcesses();
  showToast('Process list refreshed.', 'info');
});

// Auto Polling (every 5 seconds, paused when tab is hidden)
setInterval(() => {
  if (document.hidden) return;
  if (state.isPolling && !state.isActionPending) {
    fetchTasks();
    if (state.currentTab === 'processes') {
      fetchProcesses();
    }
  }
}, 5000);

document.addEventListener('visibilitychange', () => {
  if (!document.hidden) {
    fetchTasks();
    if (state.currentTab === 'processes') fetchProcesses();
  }
});

// Initial Load
initTheme();
fetchTasks();
fetchProcesses();
