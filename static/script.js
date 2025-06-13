// Auto-scroll history panel
document.addEventListener("DOMContentLoaded", function () {
  const historyPanel = document.querySelector('.history-panel');
  if (historyPanel && historyPanel.scrollHeight > historyPanel.clientHeight) {
    historyPanel.scrollTop = historyPanel.scrollHeight;
  }
});