// SPDX-License-Identifier: Apache-2.0

import test from "node:test";
import assert from "node:assert/strict";
import {
  TIMER_STATUS,
  elapsedMs,
  finishTimer,
  formatElapsed,
  pauseTimer,
  resumeTimer,
  startTimer
} from "../src/js/timer.js";

test("bat dau phien voi metadata va moc thoi gian", () => {
  const timer = startTimer({ studentCode: "SV01", subject: "AI" }, 1_000);
  assert.equal(timer.status, TIMER_STATUS.RUNNING);
  assert.equal(timer.metadata.studentCode, "SV01");
  assert.equal(elapsedMs(timer, 4_000), 3_000);
});

test("tam dung khong tinh them thoi gian", () => {
  const paused = pauseTimer(startTimer({}, 1_000), 6_000);
  assert.equal(paused.status, TIMER_STATUS.PAUSED);
  assert.equal(elapsedMs(paused, 20_000), 5_000);
});

test("tiep tuc cong don dung thoi gian da hoc", () => {
  const paused = pauseTimer(startTimer({}, 1_000), 6_000);
  const resumed = resumeTimer(paused, 10_000);
  assert.equal(elapsedMs(resumed, 14_000), 9_000);
});

test("ket thuc tao thoi luong phut va giu metadata", () => {
  const timer = startTimer({ taskType: "coding" }, 1_000);
  const result = finishTimer(timer, 3_601_000);
  assert.equal(result.durationMinutes, 60);
  assert.equal(result.metadata.taskType, "coding");
});

test("phien duoi mot phut van duoc ghi la mot phut", () => {
  assert.equal(finishTimer(startTimer({}, 0), 12_000).durationMinutes, 1);
});

test("dinh dang bo dem HH:MM:SS", () => {
  assert.equal(formatElapsed(3_661_000), "01:01:01");
  assert.equal(formatElapsed(-1), "00:00:00");
});
