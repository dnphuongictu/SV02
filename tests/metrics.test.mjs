// SPDX-License-Identifier: Apache-2.0

import test from "node:test";
import assert from "node:assert/strict";
import { classificationMetrics, compareBaselines } from "../src/js/metrics.js";

const sessions = [
  { durationMinutes: 45, focusScore: 4, fatigueScore: 5, needBreak: false },
  { durationMinutes: 65, focusScore: 3, fatigueScore: 7, needBreak: true },
  { durationMinutes: 30, focusScore: 5, fatigueScore: 3, needBreak: false },
  { durationMinutes: 65, focusScore: 2, fatigueScore: 8, needBreak: true }
];

test("classification metrics tinh confusion matrix dung", () => {
  const metrics = classificationMetrics(sessions, (session) => session.durationMinutes >= 45);
  assert.deepEqual({ tp: metrics.tp, fp: metrics.fp, tn: metrics.tn, fn: metrics.fn }, { tp: 2, fp: 1, tn: 1, fn: 0 });
  assert.equal(metrics.precision, 2 / 3);
  assert.equal(metrics.recall, 1);
  assert.equal(metrics.f1, 0.8);
  assert.equal(metrics.balancedAccuracy, 0.75);
});

test("so sanh baseline dung cung mot tap session", () => {
  const comparison = compareBaselines(sessions);
  assert.equal(comparison.fixed45.total, 4);
  assert.equal(comparison.ruleV1.total, 4);
  assert.equal(comparison.ruleV1.f1, 1);
  assert.equal(comparison.ruleV1.fp, 0);
});

test("metric khong chia cho 0", () => {
  const metrics = classificationMetrics([{ needBreak: false }], () => false);
  assert.equal(metrics.precision, null);
  assert.equal(metrics.recall, null);
  assert.equal(metrics.accuracy, 1);
});
