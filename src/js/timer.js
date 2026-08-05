// SPDX-License-Identifier: Apache-2.0

export const TIMER_STATUS = Object.freeze({
  RUNNING: "running",
  PAUSED: "paused"
});

function requireTimestamp(value, field) {
  const timestamp = Number(value);
  if (!Number.isFinite(timestamp) || timestamp < 0) {
    throw new TypeError(`${field} phai la timestamp hop le`);
  }
  return timestamp;
}

function requireTimer(timer) {
  if (!timer || !Object.values(TIMER_STATUS).includes(timer.status)) {
    throw new TypeError("Trang thai phien hoc khong hop le");
  }
  return timer;
}

export function startTimer(metadata, now = Date.now()) {
  const timestamp = requireTimestamp(now, "now");
  return {
    status: TIMER_STATUS.RUNNING,
    startedAt: timestamp,
    lastResumedAt: timestamp,
    accumulatedMs: 0,
    metadata: { ...metadata }
  };
}

export function elapsedMs(timer, now = Date.now()) {
  requireTimer(timer);
  const timestamp = requireTimestamp(now, "now");
  const runningMs = timer.status === TIMER_STATUS.RUNNING
    ? Math.max(0, timestamp - timer.lastResumedAt)
    : 0;
  return Math.max(0, timer.accumulatedMs + runningMs);
}

export function pauseTimer(timer, now = Date.now()) {
  requireTimer(timer);
  if (timer.status === TIMER_STATUS.PAUSED) return { ...timer };
  return {
    ...timer,
    status: TIMER_STATUS.PAUSED,
    accumulatedMs: elapsedMs(timer, now),
    lastResumedAt: null
  };
}

export function resumeTimer(timer, now = Date.now()) {
  requireTimer(timer);
  if (timer.status === TIMER_STATUS.RUNNING) return { ...timer };
  const timestamp = requireTimestamp(now, "now");
  return { ...timer, status: TIMER_STATUS.RUNNING, lastResumedAt: timestamp };
}

export function finishTimer(timer, now = Date.now()) {
  const endedAt = requireTimestamp(now, "now");
  const durationMs = elapsedMs(timer, endedAt);
  return {
    metadata: { ...timer.metadata },
    startedAt: timer.startedAt,
    endedAt,
    durationMs,
    durationMinutes: Math.max(1, Math.round(durationMs / 60000))
  };
}

export function formatElapsed(milliseconds) {
  const totalSeconds = Math.max(0, Math.floor(Number(milliseconds) / 1000) || 0);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return [hours, minutes, seconds].map((part) => String(part).padStart(2, "0")).join(":");
}
