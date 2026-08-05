// SPDX-License-Identifier: Apache-2.0

const REQUIRED_HEADERS = [
  "session_id", "start_time", "end_time", "student_code", "subject",
  "task_type", "duration_minutes", "focus_score", "fatigue_score",
  "need_break", "break_suggested", "rule_version"
];

const TASK_TYPES = new Set(["reading", "coding", "debugging", "writing", "exercise"]);
const FORBIDDEN_PII_HEADERS = new Set([
  "name", "full_name", "student_name", "email", "phone", "phone_number",
  "address", "student_id", "real_student_id"
]);

export function parseCsv(text) {
  const input = String(text ?? "").replace(/^\uFEFF/, "");
  const matrix = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < input.length; index += 1) {
    const char = input[index];
    if (char === '"') {
      if (quoted && input[index + 1] === '"') {
        field += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if (char === "\n" && !quoted) {
      row.push(field.replace(/\r$/, ""));
      if (row.some((value) => value !== "")) matrix.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  if (quoted) throw new SyntaxError("CSV co o du lieu chua dong dau ngoac kep");
  row.push(field.replace(/\r$/, ""));
  if (row.some((value) => value !== "")) matrix.push(row);
  if (!matrix.length) return { headers: [], records: [], rowWidths: [] };

  const headers = matrix[0].map((header) => header.trim());
  const records = matrix.slice(1).map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
  return { headers, records, rowWidths: matrix.slice(1).map((values) => values.length) };
}

function parseBoolean(value, field, rowNumber, nullable = false) {
  const normalized = String(value ?? "").trim().toLowerCase();
  if (nullable && normalized === "") return null;
  if (normalized === "true") return true;
  if (normalized === "false") return false;
  throw new TypeError(`Dong ${rowNumber}: ${field} phai la true/false${nullable ? " hoac trong" : ""}`);
}

function parseInteger(value, field, min, max, rowNumber, nullable = false) {
  const normalized = String(value ?? "").trim();
  if (nullable && normalized === "") return null;
  const number = Number(normalized);
  if (!Number.isInteger(number) || number < min || number > max) {
    throw new RangeError(`Dong ${rowNumber}: ${field} phai la so nguyen ${min}-${max}`);
  }
  return number;
}

function parseDate(value, field, rowNumber, nullable = false) {
  const normalized = String(value ?? "").trim();
  if (nullable && normalized === "") return null;
  const timestamp = Date.parse(normalized);
  if (!normalized || Number.isNaN(timestamp)) throw new TypeError(`Dong ${rowNumber}: ${field} khong phai ISO date-time hop le`);
  return { iso: new Date(timestamp).toISOString(), timestamp };
}

function normalizeRecord(record, rowNumber) {
  const start = parseDate(record.start_time, "start_time", rowNumber);
  const end = parseDate(record.end_time, "end_time", rowNumber);
  if (end.timestamp <= start.timestamp) throw new RangeError(`Dong ${rowNumber}: end_time phai sau start_time`);

  const studentCode = String(record.student_code ?? "").trim();
  if (!/^[A-Za-z0-9_-]+$/.test(studentCode)) throw new TypeError(`Dong ${rowNumber}: student_code khong hop le`);
  const subject = String(record.subject ?? "").trim();
  if (!subject) throw new TypeError(`Dong ${rowNumber}: subject khong duoc trong`);
  const taskType = String(record.task_type ?? "").trim();
  if (!TASK_TYPES.has(taskType)) throw new TypeError(`Dong ${rowNumber}: task_type khong duoc ho tro`);

  const response = parseDate(record.response_time, "response_time", rowNumber, true);
  return {
    sessionId: String(record.session_id ?? "").trim(),
    timestamp: start.iso,
    startTime: start.iso,
    endTime: end.iso,
    studentCode,
    subject,
    taskType,
    goal: String(record.goal ?? "").trim(),
    durationMinutes: parseInteger(record.duration_minutes, "duration_minutes", 5, 240, rowNumber),
    focusScore: parseInteger(record.focus_score, "focus_score", 1, 5, rowNumber),
    fatigueScore: parseInteger(record.fatigue_score, "fatigue_score", 1, 10, rowNumber),
    needBreak: parseBoolean(record.need_break, "need_break", rowNumber),
    suggested: parseBoolean(record.break_suggested, "break_suggested", rowNumber),
    accepted: parseBoolean(record.accepted, "accepted", rowNumber, true),
    responseTimestamp: response?.iso ?? null,
    riskScore: parseInteger(record.risk_score, "risk_score", 0, 100, rowNumber, true),
    ruleVersion: String(record.rule_version ?? "").trim(),
    reason: String(record.decision_reason ?? "").trim(),
    note: String(record.note ?? "").trim()
  };
}

export function validateAndNormalizeCsv(text) {
  const errors = [];
  const warnings = [];
  let parsed;
  try {
    parsed = parseCsv(text);
  } catch (error) {
    return { sessions: [], errors: [error.message], warnings, rowCount: 0 };
  }

  if (!parsed.headers.length) return { sessions: [], errors: ["CSV rong hoac khong co header"], warnings, rowCount: 0 };
  const duplicates = parsed.headers.filter((header, index) => parsed.headers.indexOf(header) !== index);
  if (duplicates.length) errors.push(`Header trung: ${[...new Set(duplicates)].join(", ")}`);
  const missing = REQUIRED_HEADERS.filter((header) => !parsed.headers.includes(header));
  if (missing.length) errors.push(`Thieu cot bat buoc: ${missing.join(", ")}`);
  const piiHeaders = parsed.headers.filter((header) => FORBIDDEN_PII_HEADERS.has(header.toLowerCase()));
  if (piiHeaders.length) errors.push(`Phat hien cot PII khong duoc phep: ${piiHeaders.join(", ")}`);

  parsed.rowWidths.forEach((width, index) => {
    if (width !== parsed.headers.length) errors.push(`Dong ${index + 2}: co ${width} cot, can ${parsed.headers.length}`);
  });
  if (errors.length) return { sessions: [], errors, warnings, rowCount: parsed.records.length };

  const sessions = [];
  const ids = new Set();
  parsed.records.forEach((record, index) => {
    const rowNumber = index + 2;
    try {
      const session = normalizeRecord(record, rowNumber);
      if (!session.sessionId) throw new TypeError(`Dong ${rowNumber}: session_id khong duoc trong`);
      if (ids.has(session.sessionId)) throw new TypeError(`Dong ${rowNumber}: session_id bi trung (${session.sessionId})`);
      ids.add(session.sessionId);
      if (session.accepted !== null && !session.suggested) warnings.push(`Dong ${rowNumber}: accepted co gia tri khi break_suggested=false`);
      const measuredMinutes = Math.round((Date.parse(session.endTime) - Date.parse(session.startTime)) / 60000);
      if (Math.abs(measuredMinutes - session.durationMinutes) > 1) warnings.push(`Dong ${rowNumber}: duration_minutes lech thoi gian bat dau/ket thuc`);
      sessions.push(session);
    } catch (error) {
      errors.push(error.message);
    }
  });

  return { sessions: errors.length ? [] : sessions, errors, warnings, rowCount: parsed.records.length };
}
