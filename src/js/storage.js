// SPDX-License-Identifier: Apache-2.0

const STORAGE_KEY = "focusmate_sessions_v1";
const ACTIVE_TIMER_KEY = "focusmate_active_timer_v1";
const PENDING_SESSION_KEY = "focusmate_pending_session_v1";

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

export function loadActiveTimer() {
  try {
    const value = JSON.parse(localStorage.getItem(ACTIVE_TIMER_KEY) || "null");
    return value && typeof value === "object" ? value : null;
  } catch {
    return null;
  }
}

export function saveActiveTimer(timer) {
  localStorage.setItem(ACTIVE_TIMER_KEY, JSON.stringify(timer));
}

export function clearActiveTimer() {
  localStorage.removeItem(ACTIVE_TIMER_KEY);
}

export function loadPendingSession() {
  try {
    const value = JSON.parse(localStorage.getItem(PENDING_SESSION_KEY) || "null");
    return value && typeof value === "object" ? value : null;
  } catch {
    return null;
  }
}

export function savePendingSession(session) {
  localStorage.setItem(PENDING_SESSION_KEY, JSON.stringify(session));
}

export function clearPendingSession() {
  localStorage.removeItem(PENDING_SESSION_KEY);
}
