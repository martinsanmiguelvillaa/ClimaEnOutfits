/* =====================
   CONFIG & STATE
   ===================== */
const API = "https://climaenoutfits.up.railway.app";


const state = {
  currentUser: null,
  token: null,
};

/* =====================
   API MODULE
   ===================== */
const api = {
  _handleError(err, status) {
    if (Array.isArray(err.detail)) {
      throw new Error(err.detail.map(e => e.msg).join(', '));
    }
    throw new Error(err.detail || `Error ${status}`);
  },

  _authHeaders() {
    const token = state.token || sessionStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  },

  _handle401() {
    state.token = null;
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    state.currentUser = null;
    document.getElementById('dash-login').classList.remove('hidden');
    document.getElementById('dash-content').classList.add('hidden');
    showView('dashboard');
    toast('Sesión expirada, ingresá de nuevo', 'error');
  },

  async get(path) {
    const res = await fetch(`${API}${path}`, { headers: this._authHeaders() });
    if (res.status === 401) { this._handle401(); throw new Error('No autenticado'); }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error desconocido' }));
      this._handleError(err, res.status);
    }
    return res.json();
  },

  async post(path, body) {
    const res = await fetch(`${API}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...this._authHeaders() },
      body: JSON.stringify(body),
    });
    if (res.status === 401) { this._handle401(); throw new Error('No autenticado'); }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error desconocido' }));
      this._handleError(err, res.status);
    }
    return res.json();
  },

  async patch(path, body) {
    const res = await fetch(`${API}${path}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...this._authHeaders() },
      body: JSON.stringify(body),
    });
    if (res.status === 401) { this._handle401(); throw new Error('No autenticado'); }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error desconocido' }));
      this._handleError(err, res.status);
    }
    return res.json();
  },

  async put(path, body) {
    const res = await fetch(`${API}${path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...this._authHeaders() },
      body: JSON.stringify(body),
    });
    if (res.status === 401) { this._handle401(); throw new Error('No autenticado'); }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error desconocido' }));
      this._handleError(err, res.status);
    }
    return res.json();
  },

  async delete(path) {
    const res = await fetch(`${API}${path}`, { method: 'DELETE', headers: this._authHeaders() });
    if (res.status === 401) { this._handle401(); throw new Error('No autenticado'); }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error desconocido' }));
      this._handleError(err, res.status);
    }
    return res.json();
  },
};

/* =====================
   UI UTILITIES
   ===================== */
let toastTimer = null;

function toast(msg, type = 'info') {
  const el = document.getElementById('toast');
  const icon = type === 'success' ? 'fa-circle-check' : type === 'error' ? 'fa-circle-xmark' : 'fa-circle-info';
  el.innerHTML = `<i class="fa-solid ${icon}"></i><span>${msg}</span>`;
  el.className = `toast toast-${type} show`;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 3500);
}

function showLoading(msg = 'Cargando...') {
  document.getElementById('loading-msg').textContent = msg;
  document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
  document.getElementById('loading-overlay').classList.add('hidden');
}

function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`view-${name}`).classList.add('active');
  const navBtn = document.querySelector(`[data-view="${name}"]`);
  if (navBtn) navBtn.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* =====================
   WEATHER & OUTFIT ICONS
   ===================== */
function weatherIcon(description) {
  const d = (description || '').toLowerCase();
  if (d.includes('clear') || d.includes('despejado') || d.includes('sun')) return '☀️';
  if (d.includes('few clouds') || d.includes('partly')) return '⛅';
  if (d.includes('cloud') || d.includes('overcast') || d.includes('nublado')) return '☁️';
  if (d.includes('drizzle') || d.includes('llovizna')) return '🌦️';
  if (d.includes('thunder') || d.includes('storm') || d.includes('tormenta')) return '⛈️';
  if (d.includes('snow') || d.includes('nieve')) return '❄️';
  if (d.includes('mist') || d.includes('fog') || d.includes('haze') || d.includes('niebla')) return '🌫️';
  if (d.includes('rain') || d.includes('lluvia')) return '🌧️';
  return '🌤️';
}

function formatSunset(unix) {
  if (!unix) return '-';
  const date = new Date(unix * 1000);
  return date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
}

function formatDate() {
  return new Date().toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long' });
}

/* =====================
   RENDER: WEATHER
   ===================== */
function renderWeather(weather, cityName, containerId) {
  const container = document.getElementById(containerId);
  const city = cityName || weather.city || '';
  const desc = weather.description || '';
  const pop = Math.round((weather.pop || 0) * 100);
  const uv = weather.max_uv_index != null ? weather.max_uv_index.toFixed(1) : '-';
  const sunset = formatSunset(weather.sunset);

  container.innerHTML = `
    <div class="fade-in">
      <div class="weather-header">
        <div>
          <div class="weather-city"><i class="fa-solid fa-location-dot" style="color:var(--accent-light);margin-right:6px;font-size:0.85rem"></i>${city}</div>
          <div class="weather-date">${formatDate()}</div>
        </div>
        <div class="weather-icon-wrap">${weatherIcon(desc)}</div>
      </div>
      <div class="weather-temp">${Math.round(weather.temperature || 0)}°C</div>
      <div class="weather-feels">Sensación térmica: ${Math.round(weather.feels_like || 0)}°C</div>
      <div class="weather-desc">${desc}</div>
      <div class="weather-stats">
        <div class="stat">
          <div class="stat-icon">💧</div>
          <div class="stat-val">${weather.humidity || 0}%</div>
          <div class="stat-lbl">Humedad</div>
        </div>
        <div class="stat">
          <div class="stat-icon">💨</div>
          <div class="stat-val">${Math.round(weather.wind_speed || 0)}<small style="font-size:0.6rem"> km/h</small></div>
          <div class="stat-lbl">Viento</div>
        </div>
        <div class="stat">
          <div class="stat-icon">🌂</div>
          <div class="stat-val">${pop}%</div>
          <div class="stat-lbl">Lluvia</div>
        </div>
        <div class="stat">
          <div class="stat-icon">☁️</div>
          <div class="stat-val">${weather.cloudiness || 0}%</div>
          <div class="stat-lbl">Nubosidad</div>
        </div>
        <div class="stat">
          <div class="stat-icon">🔆</div>
          <div class="stat-val">${uv}</div>
          <div class="stat-lbl">Índice UV</div>
        </div>
        <div class="stat">
          <div class="stat-icon">🌅</div>
          <div class="stat-val sunset-time">${sunset}</div>
          <div class="stat-lbl">Atardecer</div>
        </div>
      </div>
    </div>
  `;
}

/* =====================
   RENDER: OUTFIT
   ===================== */
function renderOutfit(outfit, containerId) {
  const container = document.getElementById(containerId);
  const extras = Array.isArray(outfit.extras) ? outfit.extras : [];

  container.innerHTML = `
    <div class="fade-in">
      <div class="outfit-title"><i class="fa-solid fa-shirt" style="color:var(--accent-light)"></i> Tu outfit de hoy</div>
      <div class="outfit-item">
        <div class="outfit-item-icon">👕</div>
        <div>
          <div class="outfit-item-label">Parte superior</div>
          <div class="outfit-item-val">${outfit.upper_body || '-'}</div>
        </div>
      </div>
      <div class="outfit-item">
        <div class="outfit-item-icon">👖</div>
        <div>
          <div class="outfit-item-label">Parte inferior</div>
          <div class="outfit-item-val">${outfit.lower_body || '-'}</div>
        </div>
      </div>
      <div class="outfit-item">
        <div class="outfit-item-icon">👟</div>
        <div>
          <div class="outfit-item-label">Calzado</div>
          <div class="outfit-item-val">${outfit.footwear || '-'}</div>
        </div>
      </div>
      ${extras.length ? `
        <div class="outfit-extras">
          ${extras.map(e => `<span class="extra-chip">${e}</span>`).join('')}
        </div>` : ''}
      ${outfit.summary ? `<div class="outfit-summary">${outfit.summary}</div>` : ''}
    </div>
  `;
}

/* =====================
   RENDER: USER INFO
   ===================== */
function renderUserInfo(user, containerId = 'user-info-card') {
  const container = document.getElementById(containerId);
  const initial = ((user.name || user.mail || '?')[0]).toUpperCase();
  const fullName = [user.name, user.last_name].filter(Boolean).join(' ') || user.mail;
  const channelLabel = { mail: '📧 Email', whatsapp: '💬 WhatsApp', both: '📧💬 Ambos' };
  const notifLabel = user.notifications_enabled
    ? `🔔 ${user.notification_time || ''}`
    : '🔕 Sin notificaciones';

  container.innerHTML = `
    <div class="user-header fade-in">
      <div class="user-avatar">${initial}</div>
      <div style="flex:1">
        <div class="user-name">${fullName}</div>
        <div class="user-meta">
          <span><i class="fa-solid fa-location-dot"></i> ${user.city || '-'}</span>
          <span><i class="fa-solid fa-envelope"></i> ${user.mail || '-'}</span>
          <span><i class="fa-solid fa-phone"></i> ${user.phone_number || '-'}</span>
        </div>
      </div>
      <div class="user-badges">
        <span class="badge badge-accent">${channelLabel[user.preferred_channel] || user.preferred_channel}</span>
        <span class="badge ${user.notifications_enabled ? 'badge-success' : 'badge-muted'}">${notifLabel}</span>
        <span class="badge badge-muted">ID: ${user.id}</span>
      </div>
    </div>
    <div style="margin-top:16px;display:flex;justify-content:flex-end">
      <button class="btn btn-ghost btn-sm" id="edit-profile-btn">
        <i class="fa-solid fa-pen-to-square"></i> Editar información
      </button>
    </div>
  `;

  document.getElementById('edit-profile-btn').addEventListener('click', showEditView);
}

/* =====================
   EDIT PROFILE
   ===================== */
function showEditView() {
  const user = state.currentUser;
  document.getElementById('edit-name').value = user.name || '';
  document.getElementById('edit-lastname').value = user.last_name || '';
  document.getElementById('edit-gender').value = user.gender || 'prefiero no decirlo';
  document.getElementById('edit-email').value = user.mail || '';
  document.getElementById('edit-phone').value = user.phone_number || '';
  document.getElementById('edit-city').value = user.city || '';
  document.getElementById('edit-whatsapp').checked = user.whatsapp_opt_in || false;
  showView('edit');
}

async function handleEditSubmit(e) {
  e.preventDefault();

  const body = {
    name: document.getElementById('edit-name').value.trim() || null,
    last_name: document.getElementById('edit-lastname').value.trim() || null,
    gender: document.getElementById('edit-gender').value || null,
    mail: document.getElementById('edit-email').value.trim() || null,
    phone_number: document.getElementById('edit-phone').value.trim() || null,
    city: document.getElementById('edit-city').value.trim() || null,
    whatsapp_opt_in: document.getElementById('edit-whatsapp').checked,
  };

  showLoading('Guardando cambios...');

  try {
    const updated = await api.patch(`/users/${state.currentUser.id}`, body);
    state.currentUser = updated;
    toast('Información actualizada', 'success');
    showView('dashboard');
    renderUserInfo(updated);
    renderNotifSettings(updated);
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    hideLoading();
  }
}

/* =====================
   RENDER: PREFERENCES
   ===================== */
function renderPreferences(prefs) {
  const container = document.getElementById('pref-list');
  if (!prefs || prefs.length === 0) {
    container.innerHTML = `<div class="pref-empty"><i class="fa-regular fa-face-meh"></i> Sin preferencias guardadas</div>`;
    return;
  }
  container.innerHTML = prefs.map(p => `
    <div class="pref-item fade-in" id="pref-item-${p.id}">
      <span class="pref-text">
        <i class="fa-solid fa-check" style="color:var(--accent-light);margin-right:8px;font-size:0.75rem"></i>${p.preference}
      </span>
      <div style="display:flex;gap:4px;flex-shrink:0">
        <button class="pref-delete" onclick="startEditPreference(${p.id}, \`${p.preference.replace(/`/g, '\\`')}\`)" title="Editar">
          <i class="fa-solid fa-pen"></i>
        </button>
        <button class="pref-delete" onclick="deletePreference(${p.id})" title="Eliminar">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    </div>
  `).join('');
}

function startEditPreference(id, currentText) {
  const item = document.getElementById(`pref-item-${id}`);
  item.innerHTML = `
    <input type="text" class="pref-edit-input" value="${currentText.replace(/"/g, '&quot;')}" style="flex:1;padding:6px 10px;background:rgba(255,255,255,0.08);border:1px solid var(--accent);border-radius:var(--radius-xs);color:var(--text);font-size:0.9rem;font-family:inherit;outline:none">
    <div style="display:flex;gap:4px;flex-shrink:0">
      <button class="btn btn-primary btn-sm" onclick="confirmEditPreference(${id})">
        <i class="fa-solid fa-check"></i>
      </button>
      <button class="btn btn-ghost btn-sm" onclick="cancelEditPreference(${id}, \`${currentText.replace(/`/g, '\\`')}\`)">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  `;
  item.querySelector('input').focus();
  item.querySelector('input').addEventListener('keydown', e => {
    if (e.key === 'Enter') confirmEditPreference(id);
    if (e.key === 'Escape') cancelEditPreference(id, currentText);
  });
}

async function confirmEditPreference(id) {
  const item = document.getElementById(`pref-item-${id}`);
  const newText = item.querySelector('input').value.trim();
  if (!newText) { toast('La preferencia no puede estar vacía', 'error'); return; }

  try {
    await api.patch(`/preferences/${state.currentUser.id}/preference/${id}`, { preferences: newText });
    toast('Preferencia actualizada', 'success');
    const data = await api.get(`/preferences/${state.currentUser.id}/preferences`);
    renderPreferences(data.preferences);
  } catch (err) {
    toast(err.message, 'error');
  }
}

function cancelEditPreference(id, originalText) {
  const item = document.getElementById(`pref-item-${id}`);
  item.innerHTML = `
    <span class="pref-text">
      <i class="fa-solid fa-check" style="color:var(--accent-light);margin-right:8px;font-size:0.75rem"></i>${originalText}
    </span>
    <div style="display:flex;gap:4px;flex-shrink:0">
      <button class="pref-delete" onclick="startEditPreference(${id}, \`${originalText.replace(/`/g, '\\`')}\`)" title="Editar">
        <i class="fa-solid fa-pen"></i>
      </button>
      <button class="pref-delete" onclick="deletePreference(${id})" title="Eliminar">
        <i class="fa-solid fa-trash"></i>
      </button>
    </div>
  `;
}

/* =====================
   RENDER: NOTIFICATION SETTINGS
   ===================== */
function renderNotifSettings(user) {
  const container = document.getElementById('notif-settings');
  const enabled = user.notifications_enabled;
  const time = user.notification_time ? user.notification_time.substring(0, 5) : '';

  container.innerHTML = `
    <div class="form-group" style="margin-bottom:16px">
      <label>Canal de notificación</label>
      <select id="notif-channel-select">
        <option value="mail"      ${user.preferred_channel === 'mail'      ? 'selected' : ''}>📧 Email</option>
        <option value="whatsapp"  ${user.preferred_channel === 'whatsapp'  ? 'selected' : ''}>💬 WhatsApp</option>
        <option value="both"      ${user.preferred_channel === 'both'      ? 'selected' : ''}>📧💬 Ambos</option>
      </select>
    </div>
    <div class="notif-toggle-row">
      <div class="toggle-label">
        <span>Notificaciones diarias</span>
        <small>Recibí tu outfit todos los días</small>
      </div>
      <label class="toggle">
        <input type="checkbox" id="notif-toggle" ${enabled ? 'checked' : ''}>
        <span class="slider"></span>
      </label>
    </div>
    <div id="notif-time-wrap" class="${enabled ? '' : 'hidden'}" style="margin-top:12px">
      <div class="form-group" style="margin-bottom:0">
        <label>Hora de envío</label>
        <input type="time" id="notif-time-input" value="${time}">
      </div>
    </div>
    <button class="btn btn-primary btn-sm" id="save-notif-btn" style="margin-top:16px">
      <i class="fa-solid fa-floppy-disk"></i> Guardar cambios
    </button>
  `;

  document.getElementById('notif-toggle').addEventListener('change', (e) => {
    document.getElementById('notif-time-wrap').classList.toggle('hidden', !e.target.checked);
  });

  document.getElementById('save-notif-btn').addEventListener('click', saveNotifications);
}

/* =====================
   HOME: SEARCH
   ===================== */
async function handleSearch() {
  const city = document.getElementById('city-input').value.trim();
  if (!city) {
    toast('Ingresá una ciudad', 'error');
    return;
  }

  showLoading('Consultando el clima...');

  try {
    const [weatherData, outfitData] = await Promise.all([
      api.get(`/weather/${encodeURIComponent(city)}`),
      api.get(`/outfit/${encodeURIComponent(city)}`),
    ]);

    document.getElementById('home-results').classList.remove('hidden');
    renderWeather(weatherData, city, 'weather-card');
    renderOutfit(outfitData, 'outfit-card');

    document.getElementById('home-results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    hideLoading();
  }
}

/* =====================
   REGISTER
   ===================== */
async function handleRegister(e) {
  e.preventDefault();

  const notifEnabled = document.getElementById('reg-notif-enabled').checked;
  const notifTime = document.getElementById('reg-notif-time').value;

  if (notifEnabled && !notifTime) {
    toast('Indicá la hora de notificación', 'error');
    return;
  }

  const password = document.getElementById('reg-password').value;
  if (password.length < 8) {
    toast('La contraseña debe tener al menos 8 caracteres', 'error');
    return;
  }

  const body = {
    name: document.getElementById('reg-name').value.trim() || null,
    last_name: document.getElementById('reg-lastname').value.trim() || null,
    gender: document.getElementById('reg-gender').value || null,
    mail: document.getElementById('reg-email').value.trim(),
    phone_number: document.getElementById('reg-phone').value.trim(),
    password,
    city: document.getElementById('reg-city').value.trim(),
    preferred_channel: document.getElementById('reg-channel').value,
    whatsapp_opt_in: document.getElementById('reg-whatsapp').checked,
    notifications_enabled: notifEnabled,
    notification_time: notifEnabled ? notifTime : null,
  };

  showLoading('Creando tu cuenta...');

  try {
    await api.post('/users', body);
    const loginData = await api.post('/auth/login', { mail: body.mail, password: body.password });
    state.token = loginData.access_token;
    sessionStorage.setItem('token', loginData.access_token);
    sessionStorage.setItem('user', JSON.stringify(loginData.user));
    state.currentUser = loginData.user;
    toast('¡Cuenta creada! Bienvenido/a', 'success');

    document.getElementById('register-form').reset();
    document.getElementById('reg-time-wrap').classList.add('hidden');

    showView('dashboard');
    loadDashboard(user);
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    hideLoading();
  }
}

/* =====================
   DASHBOARD: LOGIN
   ===================== */
async function handleLogin(e) {
  e.preventDefault();
  const mail = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  if (!mail || !password) {
    toast('Completá email y contraseña', 'error');
    return;
  }

  showLoading('Iniciando sesión...');

  try {
    const loginData = await api.post('/auth/login', { mail, password });
    state.token = loginData.access_token;
    sessionStorage.setItem('token', loginData.access_token);
    sessionStorage.setItem('user', JSON.stringify(loginData.user));
    state.currentUser = loginData.user;
    loadDashboard(loginData.user);
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    hideLoading();
  }
}

async function loadDashboard(user) {
  document.getElementById('dash-login').classList.add('hidden');
  document.getElementById('dash-content').classList.remove('hidden');

  renderUserInfo(user);
  renderNotifSettings(user);

  try {
    const token = state.token || sessionStorage.getItem('token');
    const res = await fetch(`${API}/preferences/${user.id}/preferences`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    if (res.ok) {
      const data = await res.json();
      renderPreferences(data.preferences);
    } else {
      renderPreferences([]);
    }
  } catch {
    renderPreferences([]);
  }

  document.getElementById('dash-results').classList.add('hidden');
}

function handleLogout() {
  state.currentUser = null;
  state.token = null;
  sessionStorage.removeItem('token');
  sessionStorage.removeItem('user');
  document.getElementById('dash-login').classList.remove('hidden');
  document.getElementById('dash-content').classList.add('hidden');
  document.getElementById('login-email').value = '';
  document.getElementById('login-password').value = '';
  document.getElementById('dash-results').classList.add('hidden');
}

/* =====================
   DASHBOARD: OUTFIT
   ===================== */
async function handleGetMyOutfit() {
  if (!state.currentUser) return;

  showLoading('Generando tu outfit personalizado...');

  try {
    // /users/{id}/outfit ya incluye el clima en la respuesta,
    // así que no hace falta llamar a /weather por separado.
    const data = await api.get(`/users/${state.currentUser.id}/outfit`);
    const weather = data.weather;
    const outfit = data.outfit;
    const city = state.currentUser.city;

    document.getElementById('dash-results').classList.remove('hidden');
    renderWeather(weather, city, 'dash-weather-card');
    renderOutfit(outfit, 'dash-outfit-card');

    document.getElementById('dash-results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    hideLoading();
  }
}

/* =====================
   PREFERENCES
   ===================== */
function toggleAddPrefForm(show) {
  document.getElementById('add-pref-form').classList.toggle('hidden', !show);
  if (show) document.getElementById('new-pref-input').focus();
}

async function savePreference() {
  const pref = document.getElementById('new-pref-input').value.trim();
  if (!pref) {
    toast('Escribí una preferencia', 'error');
    return;
  }

  try {
    await api.post(`/preferences/${state.currentUser.id}/outfit_preferences`, { preferences: pref });
    toast('Preferencia guardada', 'success');
    document.getElementById('new-pref-input').value = '';
    toggleAddPrefForm(false);

    const data = await api.get(`/preferences/${state.currentUser.id}/preferences`);
    renderPreferences(data.preferences);
  } catch (err) {
    toast(err.message, 'error');
  }
}

async function deletePreference(prefId) {
  try {
    await api.delete(`/preferences/${state.currentUser.id}/preference/${prefId}`);
    toast('Preferencia eliminada', 'success');
    const data = await api.get(`/preferences/${state.currentUser.id}/preferences`);
    renderPreferences(data.preferences);
  } catch (err) {
    toast(err.message, 'error');
  }
}

/* =====================
   NOTIFICATIONS
   ===================== */
async function saveNotifications() {
  const enabled = document.getElementById('notif-toggle').checked;
  const time = document.getElementById('notif-time-input')?.value || null;
  const channel = document.getElementById('notif-channel-select').value;

  if (enabled && !time) {
    toast('Indicá la hora de notificación', 'error');
    return;
  }

  if ((channel === 'whatsapp' || channel === 'both') && !state.currentUser.whatsapp_opt_in) {
    toast('Para usar WhatsApp necesitás tener el opt-in activado', 'error');
    return;
  }

  showLoading('Guardando...');

  try {
    // Guardar canal via PATCH /users/{id}
    await api.patch(`/users/${state.currentUser.id}`, { preferred_channel: channel });

    // Guardar horario/estado de notificaciones
    const updated = await api.put(`/preferences/${state.currentUser.id}/notifications_moment`, {
      notifications_enabled: enabled,
      notification_time: enabled ? time : null,
    });

    updated.preferred_channel = channel;
    state.currentUser = updated;
    renderUserInfo(updated);
    renderNotifSettings(updated);
    toast('Cambios guardados', 'success');
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    hideLoading();
  }
}

/* =====================
   DELETE USER
   ===================== */
function showDeleteModal() {
  const user = state.currentUser;
  const fullName = [user.name, user.last_name].filter(Boolean).join(' ') || '—';
  document.getElementById('modal-user-info').innerHTML = `
    <span>${fullName}</span>
    <span style="font-weight:400">${user.mail}</span>
    <span style="font-weight:400">ID: ${user.id}</span>
  `;
  document.getElementById('delete-modal').classList.remove('hidden');
}

function hideDeleteModal() {
  document.getElementById('delete-modal').classList.add('hidden');
}

async function confirmDeleteUser() {
  showLoading('Eliminando cuenta...');
  hideDeleteModal();

  try {
    await api.delete(`/users/${state.currentUser.id}`);
    toast('Cuenta eliminada', 'success');
    handleLogout();
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    hideLoading();
  }
}

async function sendNotificationNow() {
  if (!state.currentUser) return;

  showLoading('Enviando notificación...');

  try {
    await api.post(`/notifications/notify/${state.currentUser.id}`, {});
    toast('¡Notificación enviada!', 'success');
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    hideLoading();
  }
}

/* =====================
   GEOLOCATION
   ===================== */
async function detectLocation() {
  if (!navigator.geolocation) return;

  showLoading('Detectando tu ubicación...');

  try {
    const position = await new Promise((resolve, reject) =>
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000 })
    );

    const { latitude, longitude } = position.coords;

    const [weatherData, outfitData] = await Promise.all([
      api.get(`/weather/location?lat=${latitude}&lon=${longitude}`),
      api.get(`/outfit/location?lat=${latitude}&lon=${longitude}`),
    ]);

    const city = weatherData.city || 'Tu ubicación';
    document.getElementById('city-input').value = city;
    document.getElementById('home-results').classList.remove('hidden');
    renderWeather(weatherData, city, 'weather-card');
    renderOutfit(outfitData, 'outfit-card');
    document.getElementById('home-results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch {
    // Permiso denegado o error: el usuario puede buscar manualmente
  } finally {
    hideLoading();
  }
}

/* =====================
   EVENT LISTENERS
   ===================== */
function init() {
  // Nav
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => showView(btn.dataset.view));
  });

  // Home search
  document.getElementById('search-btn').addEventListener('click', handleSearch);
  document.getElementById('city-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') handleSearch();
  });

  // Register form
  document.getElementById('register-form').addEventListener('submit', handleRegister);
  document.getElementById('reg-notif-enabled').addEventListener('change', e => {
    document.getElementById('reg-time-wrap').classList.toggle('hidden', !e.target.checked);
  });

  // Dashboard login
  document.getElementById('login-form').addEventListener('submit', handleLogin);

  // Dashboard outfit
  document.getElementById('get-outfit-btn').addEventListener('click', handleGetMyOutfit);

  // Dashboard logout
  document.getElementById('logout-btn').addEventListener('click', handleLogout);

  // Preferences
  document.getElementById('add-pref-btn').addEventListener('click', () => toggleAddPrefForm(true));
  document.getElementById('cancel-pref-btn').addEventListener('click', () => toggleAddPrefForm(false));
  document.getElementById('save-pref-btn').addEventListener('click', savePreference);
  document.getElementById('new-pref-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') savePreference();
  });

  // Notifications
  document.getElementById('send-notif-btn').addEventListener('click', sendNotificationNow);

  // Edit profile
  document.getElementById('edit-form').addEventListener('submit', handleEditSubmit);
  document.getElementById('edit-back-btn').addEventListener('click', () => showView('dashboard'));

  // Delete user
  document.getElementById('delete-user-btn').addEventListener('click', showDeleteModal);
  document.getElementById('modal-cancel-btn').addEventListener('click', hideDeleteModal);
  document.getElementById('modal-confirm-btn').addEventListener('click', confirmDeleteUser);
  document.getElementById('delete-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) hideDeleteModal();
  });

  // Restaurar sesión desde sessionStorage
  const savedToken = sessionStorage.getItem('token');
  const savedUser = sessionStorage.getItem('user');
  if (savedToken && savedUser) {
    try {
      state.token = savedToken;
      state.currentUser = JSON.parse(savedUser);
      loadDashboard(state.currentUser);
      showView('dashboard');
    } catch {
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
    }
  }

  // Geolocation al cargar
  detectLocation();
}

init();
