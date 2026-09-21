/* SelfLearn site script: client-side filtering only. No network calls, no trackers. */
(function () {
  "use strict";

  function normalise(value) {
    return (value || "").toString().toLowerCase();
  }

  document.querySelectorAll("[data-filter-target]").forEach(function (input) {
    var target = document.querySelector(input.getAttribute("data-filter-target"));
    if (!target) return;
    var rows = Array.prototype.slice.call(target.querySelectorAll("[data-row]"));
    var count = document.querySelector(input.getAttribute("data-count-target"));
    function apply() {
      var needle = normalise(input.value);
      var select = input.getAttribute("data-filter-select");
      var chosen = select ? normalise((document.querySelector(select) || {}).value) : "";
      var visible = 0;
      rows.forEach(function (row) {
        var haystack = normalise(row.getAttribute("data-search") || row.textContent);
        var kind = normalise(row.getAttribute("data-kind"));
        var match = (!needle || haystack.indexOf(needle) !== -1) && (!chosen || kind === chosen);
        row.hidden = !match;
        if (match) visible += 1;
      });
      if (count) count.textContent = visible + " of " + rows.length + " shown";
    }
    input.addEventListener("input", apply);
    var select = input.getAttribute("data-filter-select");
    if (select) {
      var el = document.querySelector(select);
      if (el) el.addEventListener("change", apply);
    }
    apply();
  });

  document.querySelectorAll("table[data-sortable]").forEach(function (table) {
    table.querySelectorAll("thead th").forEach(function (th, index) {
      th.style.cursor = "pointer";
      th.title = "Sort by this column";
      th.addEventListener("click", function () {
        var body = table.tBodies[0];
        var rows = Array.prototype.slice.call(body.rows);
        var ascending = th.getAttribute("data-sort-dir") !== "asc";
        rows.sort(function (a, b) {
          var left = a.cells[index] ? a.cells[index].innerText.trim() : "";
          var right = b.cells[index] ? b.cells[index].innerText.trim() : "";
          var leftNum = parseFloat(left.replace(/[,%]/g, ""));
          var rightNum = parseFloat(right.replace(/[,%]/g, ""));
          var numeric = !isNaN(leftNum) && !isNaN(rightNum);
          var result = numeric ? leftNum - rightNum : left.localeCompare(right);
          return ascending ? result : -result;
        });
        rows.forEach(function (row) { body.appendChild(row); });
        th.setAttribute("data-sort-dir", ascending ? "asc" : "desc");
      });
    });
  });

  document.querySelectorAll("[data-copy]").forEach(function (button) {
    button.addEventListener("click", function () {
      var text = button.getAttribute("data-copy");
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function () {
          button.textContent = "Copied";
          setTimeout(function () { button.textContent = "Copy"; }, 1500);
        });
      }
    });
  });

  var toggle = document.querySelector("[data-theme-toggle]");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var root = document.documentElement;
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("selflearn-theme", next); } catch (e) {}
    });
  }
})();
