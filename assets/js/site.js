/* Antarctic Ice — shared behaviors: mobile nav, fade-in, filter chips, fake forms, copy buttons, toast, TOC highlight. */
(function () {
  "use strict";
  var doc = document;
  var $$ = function (sel, root) { return [].slice.call((root || doc).querySelectorAll(sel)); };

  /* mobile nav */
  var nav = doc.getElementById("x-nav"), btn = doc.getElementById("x-menu");
  if (nav && btn) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "关闭菜单" : "打开菜单");
    });
    $$("#x-links a").forEach(function (a) {
      a.addEventListener("click", function () { nav.classList.remove("is-open"); btn.setAttribute("aria-expanded", "false"); });
    });
  }

  /* fade-in on scroll */
  var els = $$(".x-fade");
  if (!("IntersectionObserver" in window)) {
    els.forEach(function (e) { e.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* toast */
  var toastEl, toastTimer;
  function toast(msg, ms) {
    if (!toastEl) {
      toastEl = doc.createElement("div");
      toastEl.className = "x-toast";
      toastEl.setAttribute("role", "status");
      toastEl.setAttribute("aria-live", "polite");
      doc.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.classList.add("is-shown");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-shown"); }, ms || 3200);
  }
  window.xToast = toast;

  /* elements with data-toast show a joke instead of navigating */
  $$("[data-toast]").forEach(function (el) {
    el.addEventListener("click", function (e) { e.preventDefault(); toast(el.getAttribute("data-toast")); });
  });

  /* filter chips: <div class="x-chips" data-filter="group"> <button class="x-chip" data-value="all|tag">
     items: <li data-filter-item="group" data-tags="tag1 tag2"> */
  $$(".x-chips[data-filter]").forEach(function (bar) {
    var group = bar.getAttribute("data-filter");
    var chips = $$(".x-chip", bar);
    var items = $$('[data-filter-item="' + group + '"]');
    var empty = doc.querySelector('[data-filter-empty="' + group + '"]');
    chips.forEach(function (chip) {
      chip.setAttribute("type", "button");
      chip.addEventListener("click", function () {
        var v = chip.getAttribute("data-value");
        chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
        var shown = 0;
        items.forEach(function (it) {
          var tags = (it.getAttribute("data-tags") || "").split(/\s+/);
          var ok = v === "all" || tags.indexOf(v) !== -1;
          it.hidden = !ok;
          if (ok) shown++;
        });
        if (empty) empty.hidden = shown !== 0;
      });
    });
  });

  /* fake forms: <form data-fake data-result="#id"> — nothing is sent anywhere.
     The result element may contain [data-echo="fieldName"] spans that receive the typed value. */
  $$("form[data-fake]").forEach(function (form) {
    form.setAttribute("novalidate", "");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var firstBad = null, seenRadio = {};
      $$("[aria-invalid]", form).forEach(function (f) { f.removeAttribute("aria-invalid"); });
      $$(".x-err[data-auto]", form).forEach(function (m) { m.parentNode.removeChild(m); });
      $$("input, select, textarea", form).forEach(function (f) {
        if (!f.willValidate || f.checkValidity()) return;
        if (f.type === "radio") {
          if (seenRadio[f.name]) return;
          seenRadio[f.name] = true;
        }
        f.setAttribute("aria-invalid", "true");
        var msg = doc.createElement("p");
        msg.className = "x-err";
        msg.setAttribute("data-auto", "");
        msg.textContent = f.getAttribute("data-err") || "这里还空着，像一片没人踩过的雪地。";
        var host = f.closest("fieldset") || f.closest(".x-field") || f.parentNode;
        host.appendChild(msg);
        if (!firstBad) firstBad = f;
      });
      if (firstBad) { firstBad.focus(); return; }
      var data = new FormData(form);
      var target = doc.querySelector(form.getAttribute("data-result"));
      if (target) {
        $$("[data-echo]", target).forEach(function (s) {
          var v = data.get(s.getAttribute("data-echo"));
          if (v) s.textContent = v;
        });
        if (form.hasAttribute("data-hide")) form.hidden = true;
        target.classList.add("is-shown");
        target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
        target.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      if (form.getAttribute("data-fake")) toast(form.getAttribute("data-fake"));
      form.dispatchEvent(new CustomEvent("x:submitted", { detail: data }));
    });
  });

  /* copy buttons: <button class="x-copy" data-copy="#pre-id"> */
  $$("[data-copy]").forEach(function (b) {
    b.setAttribute("type", "button");
    b.addEventListener("click", function () {
      var src = doc.querySelector(b.getAttribute("data-copy"));
      var text = src ? src.innerText.replace(/^\$ /gm, "") : "";
      var done = function () { var t = b.textContent; b.textContent = "已冻结 ✓"; setTimeout(function () { b.textContent = t; }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { toast("剪贴板结冰了，请手动复制。"); });
      else toast("剪贴板结冰了，请手动复制。");
    });
  });

  /* TOC: highlight the section in view */
  var toc = doc.querySelector(".x-toc");
  if (toc && "IntersectionObserver" in window) {
    var links = $$("a[href^='#']", toc);
    var map = {};
    links.forEach(function (a) { var t = doc.getElementById(decodeURIComponent(a.getAttribute("href").slice(1))); if (t) map[t.id] = a; });
    var tio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove("is-active"); });
        var a = map[en.target.id]; if (a) a.classList.add("is-active");
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) { tio.observe(doc.getElementById(id)); });
  }
})();
