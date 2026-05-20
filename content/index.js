(() => {
  if (!Panel.mount()) return;
  Panel.render();
  Hotkeys.init();
})();
