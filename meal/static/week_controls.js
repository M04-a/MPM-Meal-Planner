(function () {
  const body = document.body;
  if (!body.dataset.week || !body.dataset.year) return;

  const curWeek = parseInt(body.dataset.week, 10);
  const curYear = parseInt(body.dataset.year, 10);

  const resetBtn = document.getElementById("resetWeek");
  const randomBtn = document.getElementById("randomizeWeek");
  const exportBtn = document.getElementById("exportPDF");
  const todayBtn = document.getElementById("todayWeek");

  // Reset week
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      if (confirm("Are you sure you want to reset this week?")) {
        window.location.href = `/reset_week?week=${curWeek}&year=${curYear}`;
      }
    });
  }

  // Randomize week
  if (randomBtn) {
    randomBtn.addEventListener("click", () => {
      if (confirm("Are you sure you want to randomize this week?")) {
        window.location.href = `/randomize_week?week=${curWeek}&year=${curYear}`;
      }
    });
  }

  // Export PDF
  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      if (confirm("Do you want to export this week to PDF?")) {
        window.location.href = `/export_pdf?week=${curWeek}&year=${curYear}`;
      }
    });
  }

  if (todayBtn) {
  todayBtn.addEventListener("click", () => {

    const today = new Date();
    const tmp = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()));
    const dayNum = tmp.getUTCDay() || 7;
    tmp.setUTCDate(tmp.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(), 0, 1));
    const weekNo = Math.ceil((((tmp - yearStart) / 86400000) + 1) / 7);
    const isoYear = tmp.getUTCFullYear();


    window.location.href = `/?week=${weekNo}&year=${isoYear}`;
  });
}
})();
