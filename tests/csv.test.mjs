// SPDX-License-Identifier: Apache-2.0

import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { parseCsv, validateAndNormalizeCsv } from "../src/js/csv.js";

const HEADER = "session_id,start_time,end_time,student_code,subject,task_type,duration_minutes,focus_score,fatigue_score,need_break,break_suggested,accepted,rule_version,decision_reason,note";
const VALID_ROW = "FM1,2026-08-05T08:00:00Z,2026-08-05T09:00:00Z,P001,AI,coding,60,3,7,true,true,true,1.0,duration,synthetic";

test("parse CSV ho tro dau phay va ngoac kep", () => {
  const parsed = parseCsv('a,b\n1,"noi dung, co dau phay"');
  assert.equal(parsed.records[0].b, "noi dung, co dau phay");
});

test("validator chuyen CSV hop le thanh session noi bo", () => {
  const result = validateAndNormalizeCsv(`${HEADER}\n${VALID_ROW}`);
  assert.deepEqual(result.errors, []);
  assert.equal(result.sessions[0].studentCode, "P001");
  assert.equal(result.sessions[0].durationMinutes, 60);
  assert.equal(result.sessions[0].needBreak, true);
});

test("validator tu choi thieu cot bat buoc", () => {
  const result = validateAndNormalizeCsv("session_id,student_code\nFM1,P001");
  assert.match(result.errors.join(" "), /Thieu cot bat buoc/);
});

test("validator tu choi PII header", () => {
  const result = validateAndNormalizeCsv(`${HEADER},email\n${VALID_ROW},a@example.com`);
  assert.match(result.errors.join(" "), /PII/);
});

test("validator tu choi gia tri ngoai mien", () => {
  const bad = VALID_ROW.replace(",60,3,7,", ",60,8,7,");
  const result = validateAndNormalizeCsv(`${HEADER}\n${bad}`);
  assert.match(result.errors.join(" "), /focus_score/);
});

test("validator tu choi phien ngan hon 5 phut theo schema", () => {
  const bad = VALID_ROW.replace(",60,3,7,", ",1,3,7,");
  const result = validateAndNormalizeCsv(`${HEADER}\n${bad}`);
  assert.match(result.errors.join(" "), /duration_minutes/);
});

test("validator tu choi session_id trung", () => {
  const result = validateAndNormalizeCsv(`${HEADER}\n${VALID_ROW}\n${VALID_ROW}`);
  assert.match(result.errors.join(" "), /session_id bi trung/);
});

test("du lieu synthetic mau vuot qua validator", async () => {
  const csv = await readFile(new URL("../data/sample_study_sessions.csv", import.meta.url), "utf8");
  const result = validateAndNormalizeCsv(csv);
  assert.deepEqual(result.errors, []);
  assert.equal(result.sessions.length, 4);
});
