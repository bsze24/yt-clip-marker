const Panel = {
  HOST_ID: 'yt-clip-marker-host',

  host: null,
  shadowRoot: null,
  headerEl: null,
  marksListEl: null,
  emptyStateEl: null,
  descriptionInputContainerEl: null,
  descriptionInputEl: null,
  descriptionRangeLabelEl: null,
  toastEl: null,
  currentOnSubmit: null,
  toastTimerId: null,

  mount() {
    if (document.getElementById(this.HOST_ID)) return false;

    this.host = document.createElement('div');
    this.host.id = this.HOST_ID;
    document.body.appendChild(this.host);

    this.shadowRoot = this.host.attachShadow({ mode: 'open' });

    const style = document.createElement('style');
    style.textContent = `
      .panel,
      .desc-input,
      .toast {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: normal;
        letter-spacing: normal;
        text-transform: none;
      }

      .panel {
        position: fixed;
        top: 80px;
        right: 20px;
        width: 280px;
        box-sizing: border-box;
        padding: 14px 16px;
        background: #ffffff;
        color: #1f1f1f;
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        font-size: 14px;
        line-height: 1.4;
        z-index: 999999;
        max-height: calc(100vh - 160px);
        overflow-y: auto;
      }

      .panel-header {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
      }

      .panel-empty {
        font-size: 13px;
        color: #888;
        text-align: center;
        padding: 12px 4px;
      }

      .panel-empty[hidden],
      .panel-marks[hidden] {
        display: none;
      }

      .panel-marks {
        display: flex;
        flex-direction: column;
      }

      .mark-row {
        padding: 8px 0;
        border-top: 1px solid rgba(0, 0, 0, 0.06);
        display: flex;
        flex-direction: column;
        gap: 2px;
      }

      .mark-row:first-child {
        border-top: none;
      }

      .mark-time {
        font-size: 12px;
        color: #666;
        font-variant-numeric: tabular-nums;
      }

      .mark-desc {
        font-size: 13px;
        color: #1f1f1f;
        word-wrap: break-word;
      }

      .desc-input {
        position: fixed;
        bottom: 120px;
        left: 50%;
        transform: translateX(-50%);
        width: 480px;
        box-sizing: border-box;
        padding: 16px 18px;
        background: #ffffff;
        color: #1f1f1f;
        border-radius: 10px;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
        z-index: 999999;
      }

      .desc-input[hidden] {
        display: none;
      }

      .desc-range {
        font-size: 13px;
        color: #666;
        font-variant-numeric: tabular-nums;
        margin-bottom: 8px;
      }

      .desc-field {
        width: 100%;
        box-sizing: border-box;
        padding: 10px 12px;
        font-size: 15px;
        font-family: inherit;
        color: #1f1f1f;
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.15);
        border-radius: 6px;
        outline: none;
        -webkit-appearance: none;
        appearance: none;
      }

      .desc-field:focus {
        border-color: #0070f3;
      }

      .desc-hint {
        font-size: 12px;
        color: #888;
        margin-top: 8px;
      }

      .toast {
        position: fixed;
        top: 24px;
        left: 50%;
        transform: translateX(-50%);
        padding: 10px 18px;
        background: rgba(31, 31, 31, 0.92);
        color: #ffffff;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        font-variant-numeric: tabular-nums;
        z-index: 1000000;
        opacity: 0;
        transition: opacity 200ms ease;
        pointer-events: none;
      }

      .toast.visible {
        opacity: 1;
      }
    `;
    this.shadowRoot.appendChild(style);

    this._buildPanel();
    this._buildDescriptionInput();
    this._buildToast();

    return true;
  },

  _buildPanel() {
    const panel = document.createElement('div');
    panel.className = 'panel';

    this.headerEl = document.createElement('div');
    this.headerEl.className = 'panel-header';
    panel.appendChild(this.headerEl);

    this.emptyStateEl = document.createElement('div');
    this.emptyStateEl.className = 'panel-empty';
    this.emptyStateEl.textContent = 'No marks yet. Hit [ to mark a start, ] to mark an end.';
    panel.appendChild(this.emptyStateEl);

    this.marksListEl = document.createElement('div');
    this.marksListEl.className = 'panel-marks';
    panel.appendChild(this.marksListEl);

    this.shadowRoot.appendChild(panel);
  },

  _buildDescriptionInput() {
    this.descriptionInputContainerEl = document.createElement('div');
    this.descriptionInputContainerEl.className = 'desc-input';
    this.descriptionInputContainerEl.hidden = true;

    this.descriptionRangeLabelEl = document.createElement('div');
    this.descriptionRangeLabelEl.className = 'desc-range';
    this.descriptionInputContainerEl.appendChild(this.descriptionRangeLabelEl);

    this.descriptionInputEl = document.createElement('input');
    this.descriptionInputEl.type = 'text';
    this.descriptionInputEl.className = 'desc-field';
    this.descriptionInputContainerEl.appendChild(this.descriptionInputEl);

    const hint = document.createElement('div');
    hint.className = 'desc-hint';
    hint.textContent = 'Enter to save · Escape to skip';
    this.descriptionInputContainerEl.appendChild(hint);

    // Persistent keydown listener — attached once, reads currentOnSubmit at fire time.
    // Re-attaching on each showDescriptionInput would accumulate listeners and replay
    // every prior onSubmit per keystroke.
    this.descriptionInputEl.addEventListener('keydown', (e) => {
      if (!this.currentOnSubmit) return;
      if (e.key === 'Enter') {
        const submit = this.currentOnSubmit;
        const value = this.descriptionInputEl.value;
        this.hideDescriptionInput();
        submit(value);
      } else if (e.key === 'Escape') {
        const submit = this.currentOnSubmit;
        this.hideDescriptionInput();
        submit('');
      }
    });

    this.shadowRoot.appendChild(this.descriptionInputContainerEl);
  },

  _buildToast() {
    this.toastEl = document.createElement('div');
    this.toastEl.className = 'toast';
    this.shadowRoot.appendChild(this.toastEl);
  },

  render() {
    const marks = Store.list();
    const n = marks.length;

    if (n === 0) {
      this.headerEl.textContent = 'Clip Marker';
    } else if (n === 1) {
      this.headerEl.textContent = 'Clip Marker · 1 mark';
    } else {
      this.headerEl.textContent = `Clip Marker · ${n} marks`;
    }

    this.emptyStateEl.hidden = n > 0;
    this.marksListEl.hidden = n === 0;
    this.marksListEl.replaceChildren();

    for (const mark of marks) {
      const row = document.createElement('div');
      row.className = 'mark-row';

      const time = document.createElement('span');
      time.className = 'mark-time';
      time.textContent = `${formatTime(mark.start)} – ${formatTime(mark.end)}`;
      row.appendChild(time);

      if (mark.description) {
        const desc = document.createElement('span');
        desc.className = 'mark-desc';
        desc.textContent = mark.description;
        row.appendChild(desc);
      }

      this.marksListEl.appendChild(row);
    }
  },

  showToast(text) {
    if (this.toastTimerId !== null) {
      clearTimeout(this.toastTimerId);
    }
    this.toastEl.textContent = text;
    this.toastEl.classList.add('visible');
    this.toastTimerId = setTimeout(() => {
      this.toastEl.classList.remove('visible');
      this.toastTimerId = null;
    }, 1500);
  },

  showDescriptionInput(start, end, onSubmit) {
    // Reachable via [ ] [ ] sequence with focus drift: user marks a range, clicks out
    // of the input, then starts a new range before dismissing the first input. Save
    // the prior mark with empty description before taking over. Discarding typed-but-
    // not-committed text is intentional — clicking out then pressing [ is a stronger
    // abandonment signal than Escape, so we treat the prior input as Escape-like.
    if (this.currentOnSubmit) {
      const priorSubmit = this.currentOnSubmit;
      this.currentOnSubmit = null;
      priorSubmit('');
    }
    this.currentOnSubmit = onSubmit;
    this.descriptionRangeLabelEl.textContent = `${formatTime(start)} – ${formatTime(end)}`;
    this.descriptionInputEl.value = '';
    this.descriptionInputContainerEl.hidden = false;
    this.descriptionInputEl.focus();
  },

  hideDescriptionInput() {
    this.currentOnSubmit = null;
    this.descriptionInputContainerEl.hidden = true;
  },
};
