// SPDX-License-Identifier: Apache-2.0

export const RULE_VERSION = "1.0";
export const COOLDOWN_MINUTES = 20;

function inRange(value, min, max, field) {
  const number = Number(value);
  if (!Number.isFinite(number) || number < min || number > max) {
    throw new RangeError(`${field} phai nam trong khoang ${min}-${max}`);
  }
  return number;
}

export function evaluateBreak(input) {
  const duration = inRange(input.durationMinutes, 5, 240, "durationMinutes");
  const focus = inRange(input.focusScore, 1, 5, "focusScore");
  const fatigue = inRange(input.fatigueScore, 1, 10, "fatigueScore");
  const minutesSinceRejection = input.minutesSinceRejection == null
    ? null
    : Math.max(0, Number(input.minutesSinceRejection));

  const matched = [];
  if (duration >= 45 && fatigue >= 6) matched.push("hoc >= 45 phut va met >= 6");
  if (duration >= 60) matched.push("hoc lien tuc >= 60 phut");
  if (fatigue >= 8 && focus <= 3) matched.push("met >= 8 va tap trung <= 3");

  const cooldownActive = minutesSinceRejection !== null && minutesSinceRejection < COOLDOWN_MINUTES;
  const suggested = matched.length > 0 && !cooldownActive;
  const riskScore = Math.min(100, Math.round(duration / 1.2 + fatigue * 5 + (6 - focus) * 4));

  let reason = "Chua cham nguong cua bo luat v1.0";
  if (matched.length) reason = matched.join("; ");
  if (cooldownActive) reason = `Tam hoan: nguoi dung vua tu choi, con ${Math.ceil(COOLDOWN_MINUTES - minutesSinceRejection)} phut cooldown`;

  return { suggested, reason, matchedRules: matched, cooldownActive, riskScore, ruleVersion: RULE_VERSION };
}
