/* Memoire's Restaurant & Event Center — site script */
(function () {
  "use strict";

  /* Where form inquiries go. Set this to the restaurant's inbox
     (e.g. "events@yourdomain.com") and every form will open the
     visitor's email app pre-filled and addressed to it. */
  var INQUIRY_EMAIL = "";
  var PHONE = "612.223.3679";

  var body = document.body;
  var head = document.querySelector(".site-head");

  /* Header shade on scroll */
  function onScroll() { if (head) head.classList.toggle("scrolled", window.scrollY > 30); }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* Mobile nav */
  var toggle = document.querySelector(".menu-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  document.querySelectorAll(".has-sub > .sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.parentElement;
      var open = li.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.querySelectorAll(".nav a").forEach(function (a) {
    a.addEventListener("click", function () { body.classList.remove("nav-open"); });
  });

  /* Reveal on scroll */
  var els = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add("in"); }); }

  /* Modals */
  var lastFocus = null;
  function openModal(m) {
    if (!m) return;
    lastFocus = document.activeElement;
    m.classList.add("open");
    m.setAttribute("aria-hidden", "false");
    var x = m.querySelector(".modal-x");
    if (x) setTimeout(function () { x.focus(); }, 50);
  }
  function closeModal(m) {
    m.classList.remove("open");
    m.setAttribute("aria-hidden", "true");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  document.querySelectorAll(".modal").forEach(function (m) {
    m.addEventListener("click", function (e) {
      if (e.target === m || e.target.closest(".modal-x") || e.target.closest("[data-close]")) closeModal(m);
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") document.querySelectorAll(".modal.open").forEach(closeModal);
  });

  /* Grand Opening pop-up (home page), once per visit */
  var promo = document.getElementById("promo");
  if (promo) {
    var seen = false;
    try { seen = sessionStorage.getItem("memoires-promo") === "1"; } catch (e) {}
    if (!seen) {
      setTimeout(function () { openModal(promo); }, 1200);
      try { sessionStorage.setItem("memoires-promo", "1"); } catch (e) {}
    }
  }
  document.querySelectorAll("[data-open-promo]").forEach(function (b) {
    b.addEventListener("click", function (e) { e.preventDefault(); openModal(promo); });
  });

  /* Flyer viewer */
  var viewer = document.getElementById("flyer");
  document.querySelectorAll("[data-flyer]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      if (!viewer) return;
      var img = viewer.querySelector("img");
      img.src = b.getAttribute("data-flyer");
      img.alt = b.getAttribute("data-alt") || "Flyer";
      openModal(viewer);
    });
  });

  /* Forms */
  document.querySelectorAll("form[data-inquiry]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.querySelector(".hp input") && form.querySelector(".hp input").value) return;
      if (!form.reportValidity()) return;

      var subject = form.getAttribute("data-inquiry");
      var lines = [];
      var data = new FormData(form);
      var grouped = {};
      data.forEach(function (v, k) {
        if (k === "website") return;
        if (grouped[k]) grouped[k] += ", " + v; else grouped[k] = v;
      });
      Object.keys(grouped).forEach(function (k) {
        if (String(grouped[k]).trim()) lines.push(k + ": " + grouped[k]);
      });
      var text = lines.join("\n");
      var msg = form.querySelector(".form-msg");

      if (INQUIRY_EMAIL) {
        window.location.href = "mailto:" + INQUIRY_EMAIL +
          "?subject=" + encodeURIComponent(subject + " — " + (grouped["Name"] || "Website")) +
          "&body=" + encodeURIComponent(text);
        if (msg) {
          msg.innerHTML = "<strong>Almost done.</strong> Your email app should open with your request filled in — just press send. Prefer to talk? Call <a href=\"tel:6122233679\">" + PHONE + "</a>.";
          msg.classList.add("show");
        }
      } else if (msg) {
        msg.innerHTML = "<strong>Thank you, " + escapeHtml(grouped["Name"] || "friend") + ".</strong> To lock in your date, please call us at <a href=\"tel:6122233679\">" + PHONE + "</a> and mention your request below.<pre style=\"white-space:pre-wrap;margin:12px 0 0;font-family:inherit;color:#bbb;font-size:.9rem\">" + escapeHtml(text) + "</pre>";
        msg.classList.add("show");
      }
      if (msg) msg.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* Footer year */
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
