(() => {
  if (!Panel.mount()) {
    console.warn('[yt-clip-marker] Panel already mounted; skipping init');
    return;
  }
  Panel.render();
  Hotkeys.init();
})();
