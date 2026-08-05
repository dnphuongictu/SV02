// SPDX-License-Identifier: Apache-2.0

import test from "node:test";
import assert from "node:assert/strict";
import { evaluateBreak, RULE_VERSION } from "../src/js/ruleEngine.js";

test("khong nhac nghi khi phien ngan va chua met", () => {
  const result = evaluateBreak({ durationMinutes: 30, focusScore: 5, fatigueScore: 3 });
  assert.equal(result.suggested, false);
  assert.equal(result.ruleVersion, RULE_VERSION);
});

test("nhac nghi khi hoc 45 phut va met tu 6", () => {
  const result = evaluateBreak({ durationMinutes: 45, focusScore: 4, fatigueScore: 6 });
  assert.equal(result.suggested, true);
  assert.match(result.reason, /45 phut/);
});

test("nhac nghi khi hoc tu 60 phut", () => {
  assert.equal(evaluateBreak({ durationMinutes: 60, focusScore: 5, fatigueScore: 2 }).suggested, true);
});

test("nhac nghi khi rat met va mat tap trung", () => {
  assert.equal(evaluateBreak({ durationMinutes: 25, focusScore: 3, fatigueScore: 8 }).suggested, true);
});

test("cooldown 20 phut chan loi nhac lap lai", () => {
  const result = evaluateBreak({ durationMinutes: 70, focusScore: 2, fatigueScore: 9, minutesSinceRejection: 10 });
  assert.equal(result.suggested, false);
  assert.equal(result.cooldownActive, true);
  assert.match(result.reason, /cooldown/);
});

test("het cooldown thi co the nhac lai", () => {
  assert.equal(evaluateBreak({ durationMinutes: 70, focusScore: 2, fatigueScore: 9, minutesSinceRejection: 20 }).suggested, true);
});

test("tu choi du lieu ngoai mien hop le", () => {
  assert.throws(() => evaluateBreak({ durationMinutes: 0, focusScore: 3, fatigueScore: 5 }), RangeError);
  assert.throws(() => evaluateBreak({ durationMinutes: 30, focusScore: 6, fatigueScore: 5 }), RangeError);
});
