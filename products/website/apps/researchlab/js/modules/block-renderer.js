/**
 * block-renderer.js — универсальный визуальный слой для Markdown-блоков.
 * Принимает нормализованные блоки и не зависит от конкретного раздела Lab.
 */
const BlockRenderer = (function() {
  'use strict';

  var uid = 0;
  var DEFAULTS = {
    shortListMax: 4,
    listType: 'auto',
    accent: 'gold',
    sanitize: true
  };

  function esc(value) {
    var node = document.createElement('div');
    node.textContent = value == null ? '' : String(value);
    return node.innerHTML;
  }

  function cleanHtml(html, options) {
    if (options.sanitize !== false && typeof DOMPurify !== 'undefined' && DOMPurify.sanitize) {
      return DOMPurify.sanitize(html);
    }
    return html;
  }

  function inline(value, options) {
    var text = value == null ? '' : String(value);
    if (typeof marked !== 'undefined' && marked.parseInline) {
      return cleanHtml(marked.parseInline(text), options);
    }
    // Без marked оставляем только безопасный простой текст.
    return esc(text).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>');
  }

  function tokenise(text) {
    if (typeof marked !== 'undefined' && marked.lexer) return marked.lexer(String(text || ''));
    var source = String(text || '').trim();
    return source ? [{ type: 'paragraph', text: source }] : [];
  }

  function itemText(item, options) {
    if (item && item.tokens && typeof marked !== 'undefined' && marked.parser) {
      return cleanHtml(marked.parser(item.tokens), options);
    }
    return inline(item && (item.text || item.raw) || '', options);
  }

  function renderList(token, options) {
    var items = token.items || [];
    var forced = options.type === 'timeline' || options.type === 'accordion' || options.type === 'cards';
    var type = forced ? options.type : (token.ordered ? 'timeline' :
      (options.listType !== 'auto' ? options.listType : (items.length <= options.shortListMax ? 'cards' : 'accordion')));

    if (type === 'timeline') {
      return '<div class="br-timeline" role="list">' + items.map(function(item, index) {
        return '<article class="br-timeline-step" role="listitem"><span class="br-timeline-number" aria-hidden="true">' +
          (index + 1) + '</span><div class="br-timeline-content">' + itemText(item, options) + '</div></article>';
      }).join('') + '</div>';
    }

    if (type === 'accordion') {
      return '<div class="br-accordion" data-br-accordion>' + items.map(function(item, index) {
        var id = 'br-panel-' + (++uid);
        return '<div class="br-accordion-item"><h3 class="br-accordion-heading"><button type="button" class="br-accordion-trigger"' +
          ' aria-expanded="' + (index === 0 ? 'true' : 'false') + '" aria-controls="' + id + '">' +
          '<span class="br-accordion-marker" aria-hidden="true">' + (index + 1) + '</span>' +
          '<span>' + inline(item.text || ('Пункт ' + (index + 1)), options) + '</span><span class="br-accordion-chevron" aria-hidden="true">+</span></button></h3>' +
          '<div class="br-accordion-panel" id="' + id + '"' + (index === 0 ? '' : ' hidden') + '>' + itemText(item, options) + '</div></div>';
      }).join('') + '</div>';
    }

    return '<div class="br-cards" role="list">' + items.map(function(item, index) {
      return '<article class="br-card" role="listitem"><span class="br-card-icon" aria-hidden="true">' +
        (options.icon || ['◆', '◇', '◈', '○'][index % 4]) + '</span><div>' + itemText(item, options) + '</div></article>';
    }).join('') + '</div>';
  }

  function renderQuote(token, options) {
    var text = token.text || '';
    return '<aside class="br-callout" role="note"><span class="br-callout-mark" aria-hidden="true">“</span><div>' +
      inline(text.replace(/^>\s?/gm, ''), options) + '</div></aside>';
  }

  function renderImage(token, options) {
    var href = String(token.href || '');
    // DOMPurify дополнительно проверит ссылку; запрещаем опасные схемы до него.
    if (/^\s*(javascript|vbscript|data:text)\s*:/i.test(href)) href = '';
    if (!href) return '<p class="br-note">' + esc(token.text || '') + '</p>';
    var caption = token.title || token.text || '';
    return '<figure class="br-figure ' + (options.type === 'cover' ? 'br-figure-cover' : '') + '">' +
      '<img src="' + esc(href) + '" alt="' + esc(token.text || '') + '" loading="lazy">' +
      (caption ? '<figcaption>' + esc(caption) + '</figcaption>' : '') + '</figure>';
  }

  function renderTokens(tokens, options) {
    var html = '';
    (tokens || []).forEach(function(token, index) {
      if (token.type === 'space' || token.type === 'hr') return;
      if (token.type === 'heading') {
        var next = tokens[index + 1];
        if (next && next.type === 'paragraph') {
          html += '<article class="br-text-card"><h' + Math.min(token.depth + 2, 6) + ' class="br-subheading">' +
            inline(token.text, options) + '</h' + Math.min(token.depth + 2, 6) + '><div class="br-text-card-body">' +
            inline(next.text, options) + '</div></article>';
          tokens[index + 1]._brConsumed = true;
        } else {
          html += '<h' + Math.min((token.depth || 3) + 1, 6) + ' class="br-subheading">' + inline(token.text, options) + '</h' + Math.min((token.depth || 3) + 1, 6) + '>';
        }
      } else if (token._brConsumed) {
        return;
      } else if (token.type === 'paragraph' || token.type === 'text') {
        html += '<p class="br-paragraph' + (String(token.text || '').length < 180 ? ' br-note' : '') + '">' + inline(token.text, options) + '</p>';
      } else if (token.type === 'list') {
        html += renderList(token, options);
      } else if (token.type === 'blockquote') {
        html += renderQuote(token, options);
      } else if (token.type === 'image') {
        html += renderImage(token, options);
      } else if (token.type === 'html') {
        html += cleanHtml(token.raw || token.text || '', options);
      } else if (token.raw) {
        html += '<p class="br-paragraph">' + inline(token.text || token.raw, options) + '</p>';
      }
    });
    return html;
  }

  function render(blocks, config) {
    var options = Object.assign({}, DEFAULTS, config || {});
    var list = Array.isArray(blocks) ? blocks : (blocks ? [blocks] : []);
    return list.map(function(block) { return renderSection(block, options); }).join('');
  }

  function renderSection(block, config) {
    var options = Object.assign({}, DEFAULTS, config || {}, block && block.options || {});
    var type = block && block.type;
    var content;
    if (block && block.bodyHtml != null) {
      content = cleanHtml(String(block.bodyHtml), options);
    } else if (type === 'html') {
      content = cleanHtml(String(block.body || ''), options);
    } else {
      content = renderTokens(tokenise(block && block.body || ''), options);
    }
    if (!content) return '';
    return '<div class="block-renderer br-accent-' + esc(options.accent) + (type ? ' br-type-' + esc(type) : '') + '">' + content + '</div>';
  }

  function bind(container) {
    if (!container || container.getAttribute('data-br-bound') === 'true') return;
    container.setAttribute('data-br-bound', 'true');
    container.querySelectorAll('[data-br-accordion] .br-accordion-trigger').forEach(function(button) {
      button.addEventListener('click', function() {
        var expanded = button.getAttribute('aria-expanded') === 'true';
        var panel = document.getElementById(button.getAttribute('aria-controls'));
        button.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        if (panel) panel.hidden = expanded;
      });
    });
  }

  return { render: render, renderSection: renderSection, bind: bind, esc: esc, tokenise: tokenise };
})();