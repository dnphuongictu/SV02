// SPDX-License-Identifier: Apache-2.0

import { evaluateBreak } from "./ruleEngine.js";
import { validateAndNormalizeCsv } from "./csv.js";
import { compareBaselines } from "./metrics.js";
import {
  clearActiveTimer,
  clearPendingSession,
  clearSessions,
  loadActiveTimer,
  loadPendingSession,
  loadSessions,
  saveActiveTimer,
  savePendingSession,
  saveSessions
} from "./storage.js";
import {
  TIMER_STATUS,
  elapsedMs,
  finishTimer,
  formatElapsed,
  pauseTimer,
  resumeTimer,
  startTimer
} from "./timer.js";

const $ = (id) => document.getElementById(id);
let sessions = loadSessions();
let activeTimer = loadActiveTimer();
let pendingSession = loadPendingSession();
let lastDecisionSessionId = null;
let installPrompt = null;

const demoSessions = [
  { sessionId: "DEMO01", timestamp: "2026-07-10T08:00:00", startTime: "2026-07-10T08:00:00", endTime: "2026-07-10T08:45:00", studentCode: "SV01", subject: "Android", taskType: "coding", durationMinutes: 45, focusScore: 4, fatigueScore: 5, needBreak: false, accepted: null, note: "Du lieu synthetic" },
  { sessionId: "DEMO02", timestamp: "2026-07-10T09:00:00", startTime: "2026-07-10T09:00:00", endTime: "2026-07-10T10:05:00", studentCode: "SV01", subject: "Android", taskType: "debugging", durationMinutes: 65, focusScore: 3, fatigueScore: 7, needBreak: true, accepted: true, note: "Du lieu synthetic" },
  { sessionId: "DEMO03", timestamp: "2026-07-11T14:00:00", startTime: "2026-07-11T14:00:00", endTime: "2026-07-11T14:30:00", studentCode: "SV02", subject: "AI", taskType: "reading", durationMinutes: 30, focusScore: 5, fatigueScore: 3, needBreak: false, accepted: null, note: "Du lieu synthetic" },
  { sessionId: "DEMO04", timestamp: "2026-07-11T14:35:00", startTime: "2026-07-11T14:35:00", endTime: "2026-07-11T15:40:00", studentCode: "SV02", subject: "AI", taskType: "writing", durationMinutes: 65, focusScore: 2, fatigueScore: 8, needBreak: true, accepted: false, note: "Du lieu synthetic" }
].map(withDecision);

function withDecision(session) {
  return { ...session, ...evaluateBreak(session) };
}

function boolLabel(value) {
  return value === true ? "Có" : value === false ? "Không" : "-";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function lastRejectedMinutes(studentCode) {
  const rejected = sessions.find((item) => item.studentCode === studentCode && item.accepted === false);
  if (!rejected) return null;
  const rejectionTime = rejected.responseTimestamp || rejected.endTime || rejected.timestamp;
  return Math.max(0, (Date.now() - new Date(rejectionTime).getTime()) / 60000);
}

function renderSessions() {
  $("totalSessions").textContent = sessions.length;
  $("totalMinutes").textContent = `${sessions.reduce((sum, item) => sum + item.durationMinutes, 0)} phút`;
  const suggested = sessions.filter((item) => item.suggested);
  $("suggestionRate").textContent = sessions.length ? `${Math.round(suggested.length / sessions.length * 100)}%` : "0%";
  const answered = suggested.filter((item) => item.accepted !== null);
  $("acceptanceRate").textContent = answered.length ? `${Math.round(answered.filter((item) => item.accepted).length / answered.length * 100)}%` : "Chưa có";

  $("sessionRows").innerHTML = sessions.map((item) => `<tr>
    <td>${escapeHtml(new Date(item.timestamp).toLocaleString("vi-VN"))}</td>
    <td>${escapeHtml(item.studentCode)}</td><td>${escapeHtml(item.subject)}</td>
    <td>${item.durationMinutes}</td><td>${item.focusScore}</td><td>${item.fatigueScore}</td>
    <td>${boolLabel(item.needBreak)}</td><td>${item.suggested ? "Nên nghỉ" : "Tiếp tục"}</td>
    <td>${boolLabel(item.accepted)}</td><td title="${escapeHtml(item.reason)}">${escapeHtml(item.reason)}</td>
  </tr>`).join("");
  $("emptyState").hidden = sessions.length > 0;
  renderEvaluation();
}

function percent(value) {
  return value === null ? "-" : `${Math.round(value * 100)}%`;
}

function renderEvaluation() {
  $("evaluationPanel").hidden = sessions.length === 0;
  if (!sessions.length) return;
  const comparison = compareBaselines(sessions);
  const synthetic = sessions.every((session) => session.sessionId.startsWith("DEMO") || /synthetic/i.test(session.note || ""));
  $("evaluationDataNote").textContent = synthetic
    ? `Đang dùng ${sessions.length} phiên synthetic: chỉ kiểm tra phép tính, không phải kết quả thực tế.`
    : `Đang đánh giá ${sessions.length} phiên. Hãy xác minh consent, chất lượng và cách chia dữ liệu trước khi công bố.`;

  for (const [prefix, metrics] of [["fixed", comparison.fixed45], ["rule", comparison.ruleV1]]) {
    $(`${prefix}Precision`).textContent = percent(metrics.precision);
    $(`${prefix}Recall`).textContent = percent(metrics.recall);
    $(`${prefix}F1`).textContent = percent(metrics.f1);
    $(`${prefix}Balanced`).textContent = percent(metrics.balancedAccuracy);
    $(`${prefix}Tp`).textContent = metrics.tp;
    $(`${prefix}Fp`).textContent = metrics.fp;
    $(`${prefix}Tn`).textContent = metrics.tn;
    $(`${prefix}Fn`).textContent = metrics.fn;
    $(`${prefix}Suggestions`).textContent = metrics.suggestions;
  }
}

function renderTimer() {
  const hasTimer = Boolean(activeTimer);
  $("timerSetupForm").hidden = hasTimer || Boolean(pendingSession);
  $("timerWorkspace").hidden = !hasTimer;
  $("feedbackPanel").hidden = !pendingSession;
  if (!hasTimer) return;

  $("timerDisplay").textContent = formatElapsed(elapsedMs(activeTimer));
  $("activeSessionMeta").textContent = `${activeTimer.metadata.subject} · ${activeTimer.metadata.studentCode} · ${activeTimer.metadata.taskType}`;
  const paused = activeTimer.status === TIMER_STATUS.PAUSED;
  $("timerStatus").textContent = paused ? "Đang tạm dừng" : "Đang tập trung";
  $("timerStatus").classList.toggle("paused", paused);
  $("pauseButton").hidden = paused;
  $("resumeButton").hidden = !paused;
}

function showDecision(result) {
  const box = $("decision");
  box.className = `decision ${result.suggested ? "break" : "continue"}`;
  box.innerHTML = `<strong>${result.suggested ? "Nên nghỉ 5-10 phút" : "Có thể tiếp tục học"}</strong><p>${escapeHtml(result.reason)}. Điểm rủi ro: ${result.riskScore}/100.</p>`;
  $("decisionActions").hidden = !result.suggested;

  if (result.suggested && "Notification" in window && Notification.permission === "granted") {
    new Notification("FocusMate: đến lúc nghỉ ngắn", { body: result.reason, icon: "icons/focusmate.svg" });
  }
}

function updateAccepted(value) {
  if (!lastDecisionSessionId) return;
  sessions = sessions.map((session) => session.sessionId === lastDecisionSessionId
    ? { ...session, accepted: value, responseTimestamp: new Date().toISOString() }
    : session);
  saveSessions(sessions);
  renderSessions();
  $("decisionActions").hidden = true;
  const response = value ? "Đã ghi nhận: bạn chấp nhận nghỉ." : "Đã ghi nhận: lời nhắc được hoãn và cooldown 20 phút được kích hoạt.";
  $("decision").insertAdjacentHTML("beforeend", `<p><strong>${escapeHtml(response)}</strong></p>`);
}

function resetToNewSession() {
  activeTimer = null;
  pendingSession = null;
  clearActiveTimer();
  clearPendingSession();
  $("feedbackForm").reset();
  $("focusScore").value = "3";
  $("fatigueScore").value = "6";
  renderTimer();
}

$("timerSetupForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const metadata = {
    studentCode: $("studentCode").value.trim(),
    subject: $("subject").value.trim(),
    taskType: $("taskType").value,
    goal: $("sessionGoal").value.trim()
  };
  activeTimer = startTimer(metadata);
  saveActiveTimer(activeTimer);
  renderTimer();

  if ("Notification" in window && Notification.permission === "default") {
    try { await Notification.requestPermission(); } catch { /* Trinh duyet co the khong ho tro prompt. */ }
  }
});

$("pauseButton").addEventListener("click", () => {
  activeTimer = pauseTimer(activeTimer);
  saveActiveTimer(activeTimer);
  renderTimer();
});

$("resumeButton").addEventListener("click", () => {
  activeTimer = resumeTimer(activeTimer);
  saveActiveTimer(activeTimer);
  renderTimer();
});

$("finishButton").addEventListener("click", () => {
  const finished = finishTimer(activeTimer);
  if (finished.durationMinutes < 5) {
    alert("Phiên cần kéo dài ít nhất 5 phút để được ghi vào dữ liệu nghiên cứu.");
    return;
  }
  pendingSession = finished;
  savePendingSession(pendingSession);
  activeTimer = null;
  clearActiveTimer();
  $("duration").value = String(pendingSession.durationMinutes);
  renderTimer();
});

$("feedbackForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const metadata = pendingSession.metadata;
  const session = {
    sessionId: `FM-${Date.now()}`,
    timestamp: new Date(pendingSession.startedAt).toISOString(),
    startTime: new Date(pendingSession.startedAt).toISOString(),
    endTime: new Date(pendingSession.endedAt).toISOString(),
    studentCode: metadata.studentCode,
    subject: metadata.subject,
    taskType: metadata.taskType,
    goal: metadata.goal,
    durationMinutes: pendingSession.durationMinutes,
    focusScore: Number($("focusScore").value),
    fatigueScore: Number($("fatigueScore").value),
    needBreak: $("needBreak").value === "true",
    accepted: null,
    note: $("note").value.trim(),
    minutesSinceRejection: lastRejectedMinutes(metadata.studentCode)
  };
  const completed = withDecision(session);
  sessions.unshift(completed);
  lastDecisionSessionId = completed.sessionId;
  saveSessions(sessions);
  showDecision(completed);
  renderSessions();
  resetToNewSession();
});

$("acceptSuggestion").addEventListener("click", () => updateAccepted(true));
$("rejectSuggestion").addEventListener("click", () => updateAccepted(false));

$("seedButton").addEventListener("click", () => {
  if (sessions.length && !confirm("Thay dữ liệu hiện tại bằng 4 phiên synthetic?")) return;
  sessions = structuredClone(demoSessions);
  saveSessions(sessions);
  renderSessions();
});

$("importButton").addEventListener("click", () => $("importFile").click());

$("importFile").addEventListener("change", async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  const status = $("importStatus");
  try {
    const result = validateAndNormalizeCsv(await file.text());
    status.hidden = false;
    if (result.errors.length) {
      status.className = "import-status error";
      status.textContent = `Không nhập dữ liệu: ${result.errors.slice(0, 5).join(" · ")}`;
      return;
    }
    if (!result.sessions.length) {
      status.className = "import-status error";
      status.textContent = "CSV không có phiên dữ liệu.";
      return;
    }
    if (sessions.length && !confirm(`Thay ${sessions.length} phiên hiện tại bằng ${result.sessions.length} phiên hợp lệ từ CSV?`)) return;
    sessions = result.sessions.sort((a, b) => Date.parse(b.startTime) - Date.parse(a.startTime));
    saveSessions(sessions);
    renderSessions();
    status.className = result.warnings.length ? "import-status warning" : "import-status success";
    status.textContent = `Đã nhập ${sessions.length}/${result.rowCount} dòng hợp lệ.${result.warnings.length ? ` Cảnh báo: ${result.warnings.slice(0, 3).join(" · ")}` : ""}`;
  } catch (error) {
    status.hidden = false;
    status.className = "import-status error";
    status.textContent = `Không thể đọc CSV: ${error.message}`;
  } finally {
    event.target.value = "";
  }
});

$("clearButton").addEventListener("click", () => {
  if ((!sessions.length && !activeTimer && !pendingSession) || !confirm("Xóa toàn bộ dữ liệu và phiên đang chạy trên trình duyệt này?")) return;
  sessions = [];
  clearSessions();
  resetToNewSession();
  renderSessions();
});

$("exportButton").addEventListener("click", () => {
  if (!sessions.length) return alert("Chưa có dữ liệu để xuất.");
  const fields = [
    ["session_id", "sessionId"], ["start_time", "startTime"], ["end_time", "endTime"],
    ["student_code", "studentCode"], ["subject", "subject"], ["task_type", "taskType"],
    ["goal", "goal"], ["duration_minutes", "durationMinutes"], ["focus_score", "focusScore"],
    ["fatigue_score", "fatigueScore"], ["need_break", "needBreak"],
    ["break_suggested", "suggested"], ["accepted", "accepted"], ["risk_score", "riskScore"],
    ["response_time", "responseTimestamp"],
    ["rule_version", "ruleVersion"], ["decision_reason", "reason"], ["note", "note"]
  ];
  const quote = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const csv = [fields.map(([header]) => header).join(","), ...sessions.map((row) => fields.map(([, key]) => quote(row[key])).join(","))].join("\n");
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" }));
  link.download = `focusmate-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
});

function updateNetworkStatus() {
  $("networkStatus").textContent = navigator.onLine ? "Trực tuyến" : "Đang chạy offline";
}

window.addEventListener("online", updateNetworkStatus);
window.addEventListener("offline", updateNetworkStatus);
window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  installPrompt = event;
  $("installButton").hidden = false;
});

$("installButton").addEventListener("click", async () => {
  if (!installPrompt) return;
  installPrompt.prompt();
  await installPrompt.userChoice;
  installPrompt = null;
  $("installButton").hidden = true;
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("./sw.js").catch(() => {}));
}

if (pendingSession) $("duration").value = String(pendingSession.durationMinutes);
updateNetworkStatus();
renderSessions();
renderTimer();
setInterval(renderTimer, 1000);
