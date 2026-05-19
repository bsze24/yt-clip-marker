(() => {
  const HOST_ID = 'yt-clip-marker-host';

  if (document.getElementById(HOST_ID)) return;

  const host = document.createElement('div');
  host.id = HOST_ID;
  document.body.appendChild(host);

  const shadow = host.attachShadow({ mode: 'open' });

  const style = document.createElement('style');
  style.textContent = `
    .panel {
      position: fixed;
      top: 80px;
      right: 20px;
      width: 280px;
      box-sizing: border-box;
      padding: 16px 18px;
      background: #ffffff;
      color: #1f1f1f;
      border: 1px solid rgba(0, 0, 0, 0.08);
      border-radius: 8px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 16px;
      font-weight: 600;
      line-height: 1.4;
      z-index: 999999;
    }
  `;
  shadow.appendChild(style);

  const panel = document.createElement('div');
  panel.className = 'panel';
  panel.textContent = 'Clip Marker';
  shadow.appendChild(panel);
})();
