/* reveal.js — IntersectionObserver для stagger-появления элементов с классом .reveal.
   Стили .reveal/.is-visible в lab.css (opacity+translateY, stagger через --i). */
(function () {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('is-visible'); });
    return;
  }
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  function scan(root) {
    var nodes = (root || document).querySelectorAll('.reveal:not(.is-visible)');
    nodes.forEach(function (el) { if (reduced) el.classList.add('is-visible'); else io.observe(el); });
  }
  if (reduced) { scan(); return; }
  document.addEventListener('DOMContentLoaded', function () { scan(); });
  window.RevealObserver = { scan: scan, io: io };
})();
