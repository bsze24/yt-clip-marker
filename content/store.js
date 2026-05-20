function formatTime(seconds) {
  const total = Math.max(0, Math.floor(seconds || 0));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  const pad = (n) => String(n).padStart(2, '0');
  return hours > 0
    ? `${hours}:${pad(minutes)}:${pad(secs)}`
    : `${minutes}:${pad(secs)}`;
}

const Store = {
  marks: [],
  pendingStart: null,

  setPendingStart(time) {
    this.pendingStart = Math.max(0, time);
  },

  hasPendingStart() {
    return this.pendingStart !== null;
  },

  clearPendingStart() {
    this.pendingStart = null;
  },

  finalizeMark(start, end, description) {
    const mark = {
      start: Math.max(0, start),
      end: Math.max(start, end),
      description: description ?? '',
    };
    this.marks.push(mark);
    this.marks.sort((a, b) => a.start - b.start);
    return mark;
  },

  list() {
    return [...this.marks];
  },
};
