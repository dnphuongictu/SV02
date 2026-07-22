import { evaluateBreak } from "./ruleEngine.js";
import { clearSessions, loadSessions, saveSessions } from "./storage.js";

const $ = (id) => document.getElementById(id);
let sessions = loadSessions();

const demoSessions = [
  { sessionId: "DEMO01", timestamp: "2026-07-10T08:45:00", studentCode: "SV01", subject: "Android", taskType: "coding", durationMinutes: 45, focusScore: 4, fatigueScore: 5, needBreak: false, accepted: null },
  { sessionId: "DEMO02", timestamp: "2026-07-10T10:10:00", studentCode: "SV01", subject: "Android", taskType: "debugging", durationMinutes: 65, focusScore: 3, fatigueScore: 7, needBreak: true, accepted: true },
  { sessionId: "DEMO03", timestamp: "2026-07-11T14:30:00", studentCode: "SV02", subject: "AI", taskType: "reading", durationMinutes: 30, focusScore: 5, fatigueScore: 3, needBreak: false, accepted: null },
  { sessionId: "DEMO04", timestamp: "2026-07-11T16:00:00", studentCode: "SV02", subject: "AI", taskType: "writing", durationMinutes: 55, focusScore: 2, fatigueScore: 8, needBreak: true, accepted: false }
].map(withDecision);

function withDecision(session) {
  return { ...session, ...evaluateBreak(session) };
}

function boolLabel(value) {
  return value === true ? "Co" : value === false ? "Khong" : "-";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function lastRejectedMinutes(studentCode) {
  const rejected = sessions.find((item) => item.studentCode === studentCode && item.accepted === false);
  if (!rejected) return null;
  return (Date.now() - new Date(rejected.timestamp).getTime()) / 60000;
}

function render() {
  $("totalSessions").textContent = sessions.length;
  $("totalMinutes").textContent = `${sessions.reduce((sum, item) => sum + item.durationMinutes, 0)} phut`;
  const suggested = sessions.filter((item) => item.suggested);
  $("suggestionRate").textContent = sessions.length ? `${Math.round(suggested.length / sessions.length * 100)}%` : "0%";
  const answered = suggested.filter((item) => item.accepted !== null);
  $("acceptanceRate").textContent = answered.length ? `${Math.round(answered.filter((item) => item.accepted).length / answered.length * 100)}%` : "Chua co";

  $("sessionRows").innerHTML = sessions.map((item) => `<tr>
    <td>${escapeHtml(new Date(item.timestamp).toLocaleString("vi-VN"))}</td>
    <td>${escapeHtml(item.studentCode)}</td><td>${escapeHtml(item.subject)}</td>
    <td>${item.durationMinutes}</td><td>${item.focusScore}</td><td>${item.fatigueScore}</td>
    <td>${boolLabel(item.needBreak)}</td><td>${item.suggested ? "Nen nghi" : "Tiep tuc"}</td>
    <td>${boolLabel(item.accepted)}</td><td title="${escapeHtml(item.reason)}">${escapeHtml(item.reason)}</td>
  </tr>`).join("");
  $("emptyState").hidden = sessions.length > 0;
}

function showDecision(result) {
  const box = $("decision");
  box.className = `decision ${result.suggested ? "break" : "continue"}`;
  box.innerHTML = `<strong>${result.suggested ? "Nen nghi 5-10 phut" : "Co the tiep tuc hoc"}</strong><p>${escapeHtml(result.reason)}. Diem rui ro: ${result.riskScore}/100.</p>`;
}

$("sessionForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const studentCode = $("studentCode").value.trim();
  const session = {
    sessionId: `FM-${Date.now()}`,
    timestamp: new Date().toISOString(),
    studentCode,
    subject: $("subject").value.trim(),
    taskType: $("taskType").value,
    durationMinutes: Number($("duration").value),
    focusScore: Number($("focusScore").value),
    fatigueScore: Number($("fatigueScore").value),
    needBreak: $("needBreak").value === "true",
    accepted: $("accepted").value === "" ? null : $("accepted").value === "true",
    minutesSinceRejection: lastRejectedMinutes(studentCode)
  };
  const completed = withDecision(session);
  sessions.unshift(completed);
  saveSessions(sessions);
  showDecision(completed);
  render();
});

$("seedButton").addEventListener("click", () => {
  if (sessions.length && !confirm("Thay du lieu hien tai bang 4 phien mau?")) return;
  sessions = structuredClone(demoSessions);
  saveSessions(sessions);
  render();
});

$("clearButton").addEventListener("click", () => {
  if (!sessions.length || !confirm("Xoa toan bo du lieu tren trinh duyet nay?")) return;
  sessions = [];
  clearSessions();
  render();
});

$("exportButton").addEventListener("click", () => {
  if (!sessions.length) return alert("Chua co du lieu de xuat.");
  const fields = ["sessionId", "timestamp", "studentCode", "subject", "taskType", "durationMinutes", "focusScore", "fatigueScore", "needBreak", "suggested", "accepted", "riskScore", "ruleVersion", "reason"];
  const quote = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const csv = [fields.join(","), ...sessions.map((row) => fields.map((field) => quote(row[field])).join(","))].join("\n");
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" }));
  link.download = `focusmate-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
});

render();
