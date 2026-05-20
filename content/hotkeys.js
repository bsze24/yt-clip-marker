const BACKDATE_SECONDS = 5;

const Hotkeys = {
  init() {
    document.addEventListener('keydown', (e) => this.handle(e));
  },

  handle(e) {
    if (e.repeat) return;
    if (e.isComposing) return;
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const target = e.composedPath()[0];
    if (this.isTypingTarget(target)) return;

    if (e.key === '[') {
      this.markStart();
    } else if (e.key === ']') {
      this.markEnd();
    }
  },

  isTypingTarget(el) {
    if (!el) return false;
    const tag = el.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return true;
    if (el.isContentEditable) return true;
    return false;
  },

  getCurrentTime() {
    const v = document.querySelector('video');
    return v ? v.currentTime : null;
  },

  markStart() {
    const currentTime = this.getCurrentTime();
    if (currentTime === null) return;
    const backdated = Math.max(0, currentTime - BACKDATE_SECONDS);
    Store.setPendingStart(backdated);
    Panel.showToast(`Start at ${formatTime(backdated)}`);
  },

  markEnd() {
    const start = Store.pendingStart;
    if (start === null) return;
    const end = this.getCurrentTime();
    if (end === null) return;
    Store.clearPendingStart();
    Panel.showDescriptionInput(start, end, (description) => {
      Store.finalizeMark(start, end, description.trim());
      Panel.render();
    });
  },
};
