const STORAGE_KEY = "focusmate_sessions_v1";

export function loadSessions() {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

export function saveSessions(sessions) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

export function clearSessions() {
  localStorage.removeItem(STORAGE_KEY);
}
