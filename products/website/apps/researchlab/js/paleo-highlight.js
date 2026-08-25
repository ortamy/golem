/* Глобальная маркировка палео-знаков в динамическом тексте. */
(function() {
  'use strict';

  var PALEO_PATTERN = /[𐤀-𐤕]/u;
  var SKIP_TAGS = { SCRIPT: true, STYLE: true, TEXTAREA: true, INPUT: true, SELECT: true };

  function mark(root) {
    if (!root || !root.querySelectorAll) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    var nodes = [];
    var node;
    while ((node = walker.nextNode())) {
      if (!PALEO_PATTERN.test(node.nodeValue) || !node.parentElement ||
          SKIP_TAGS[node.parentElement.tagName] ||
          node.parentElement.closest('.paleo-highlight')) continue;
      nodes.push(node);
    }
    nodes.forEach(function(textNode) {
      var fragment = document.createDocumentFragment();
      var parts = textNode.nodeValue.split(/([𐤀-𐤕]+)/u);
      parts.forEach(function(part) {
        if (!part) return;
        if (PALEO_PATTERN.test(part)) {
          var span = document.createElement('span');
          span.className = 'paleo-highlight';
          span.textContent = part;
          fragment.appendChild(span);
        } else {
          fragment.appendChild(document.createTextNode(part));
        }
      });
      textNode.parentNode.replaceChild(fragment, textNode);
    });
  }

  function init() {
    var content = document.getElementById('labContent') || document.body;
    mark(content);
    if (!window.MutationObserver) return;
    new MutationObserver(function() { mark(content); }).observe(content, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());