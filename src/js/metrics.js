// SPDX-License-Identifier: Apache-2.0

import { evaluateBreak } from "./ruleEngine.js";

export function fixed45Prediction(session) {
  return Number(session.durationMinutes) >= 45;
}

export function ruleV1Prediction(session) {
  return evaluateBreak({
    durationMinutes: session.durationMinutes,
    focusScore: session.focusScore,
    fatigueScore: session.fatigueScore
  }).suggested;
}

function safeDivide(numerator, denominator) {
  return denominator ? numerator / denominator : null;
}

export function classificationMetrics(sessions, predictor) {
  const matrix = { tp: 0, fp: 0, tn: 0, fn: 0 };
  sessions.forEach((session) => {
    const truth = session.needBreak === true;
    const prediction = predictor(session) === true;
    if (truth && prediction) matrix.tp += 1;
    else if (!truth && prediction) matrix.fp += 1;
    else if (!truth && !prediction) matrix.tn += 1;
    else matrix.fn += 1;
  });

  const precision = safeDivide(matrix.tp, matrix.tp + matrix.fp);
  const recall = safeDivide(matrix.tp, matrix.tp + matrix.fn);
  const specificity = safeDivide(matrix.tn, matrix.tn + matrix.fp);
  const f1 = precision !== null && recall !== null && precision + recall > 0
    ? 2 * precision * recall / (precision + recall)
    : null;
  const accuracy = safeDivide(matrix.tp + matrix.tn, sessions.length);
  const balancedAccuracy = recall !== null && specificity !== null ? (recall + specificity) / 2 : null;
  const suggestions = matrix.tp + matrix.fp;

  return {
    ...matrix,
    total: sessions.length,
    suggestions,
    suggestionRate: safeDivide(suggestions, sessions.length),
    precision,
    recall,
    specificity,
    f1,
    accuracy,
    balancedAccuracy
  };
}

export function compareBaselines(sessions) {
  return {
    fixed45: classificationMetrics(sessions, fixed45Prediction),
    ruleV1: classificationMetrics(sessions, ruleV1Prediction)
  };
}
