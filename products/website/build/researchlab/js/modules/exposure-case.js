/**
 * exposure-case.js — единый рендерер «дела» разоблачения.
 * renderCard/renderCase/renderPreview работают на одной схеме (data/exposures/index.json)
 * и используются и в каталоге (#researches), и в детальном просмотре, и в форме создания.
 */
const ExposureCase = (function() {
  'use strict';

  var CONFIDENCE_META = {
    verified: { label: 'Проверено', className: 'exposure-badge-verified' },
    'needs-review': { label: 'Требует проверки', className: 'exposure-badge-review' },
    hypothesis: { label: 'Гипотеза', className: 'exposure-badge-hypothesis' },
    disputed: { label: 'Спорно', className: 'exposure-badge-disputed' }
  };

  var STATUS_LABELS = {
    draft: 'Черновик',
    review: 'На проверке',
    published: 'Опубликовано'
  };

  function esc(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  function renderMd(text) {
    if (!text) return '';
    var raw = (typeof marked !== 'undefined' && marked.parse) ? marked.parse(String(text)) : esc(String(text));
    if (typeof DOMPurify !== 'undefined' && DOMPurify.sanitize) return DOMPurify.sanitize(raw);
    return esc(String(text));
  }

  function confidenceMeta(value) {
    return CONFIDENCE_META[value] || CONFIDENCE_META['needs-review'];
  }

  function confidenceBadge(value) {
    var meta = confidenceMeta(value);
    return '<span class="exposure-badge ' + meta.className + '">' + esc(meta.label) + '</span>';
  }

  // ===== КАРТОЧКА (каталог) =====
  function renderCard(item) {
    var tags = (item.tags || []).slice(0, 4).map(function(tag) {
      return '<span class="exposure-card-tag">' + esc(tag) + '</span>';
    }).join('');
    var sourcesCount = (item.sources || []).length;
    return '<a class="exposure-card" href="#researches/case/' + encodeURIComponent(item.slug) + '" data-slug="' + esc(item.slug) + '">' +
      '<div class="exposure-card-top">' +
        confidenceBadge(item.confidence) +
        '<span class="exposure-card-category">' + esc(item.category || '') + '</span>' +
      '</div>' +
      '<div class="exposure-card-title">' + esc(item.title || '') + '</div>' +
      '<div class="exposure-card-summary">' + esc(item.summary || '') + '</div>' +
      '<div class="exposure-card-tags">' + tags + '</div>' +
      '<div class="exposure-card-foot">' +
        '<span>' + sourcesCount + ' источник' + (sourcesCount === 1 ? '' : (sourcesCount >= 2 && sourcesCount <= 4 ? 'а' : 'ов')) + '</span>' +
        '<span>' + esc(item.updatedAt || '') + '</span>' +
      '</div>' +
    '</a>';
  }

  // ===== ДОСЬЕ: вспомогательные блоки =====
  function sectionId(idx) { return 'exposure-section-' + idx; }

  function buildSections(item) {
    var s = item.sections || {};
    var blocks = [];
    if (s.thesis) blocks.push({ heading: 'Тезис', body: s.thesis });
    if (s.original) {
      var o = s.original;
      var originalHtml = '<div class="exposure-original">' +
        (o.hebrew ? '<div class="exposure-original-hebrew" dir="rtl" lang="he">' + esc(o.hebrew) + '</div>' : '') +
        (o.translit ? '<div class="exposure-original-translit">' + esc(o.translit) + '</div>' : '') +
        (o.root ? '<div class="exposure-original-root">Корень: ' + esc(o.root) + '</div>' : '') +
        (o.paleo && o.paleo.length ? '<div class="exposure-original-paleo" dir="rtl">' + esc(o.paleo.join(' ')) + '</div>' : '') +
      '</div>';
      blocks.push({ heading: 'Оригинал', bodyHtml: originalHtml });
    }
    if (s.shift) blocks.push({ heading: 'Сдвиг', body: s.shift });
    if (s.transmissionChain && s.transmissionChain.length) {
      var chainHtml = '<div class="substitution-chain">' + s.transmissionChain.map(function(step, i) {
        return '<div class="substitution-step"><span class="substitution-step-number">' + (i + 1) + '</span>' +
          '<strong>' + esc(step.layer || '') + '</strong>' +
          '<span class="substitution-word">' + esc(step.word || '') + '</span>' +
          (step.meaning ? '<span class="substitution-meaning">' + esc(step.meaning) + '</span>' : '') +
        '</div>';
      }).join('') + '</div>';
      blocks.push({ heading: 'Цепочка передачи', bodyHtml: chainHtml });
    }
    (s.content || []).forEach(function(c) {
      blocks.push({ heading: c.heading || '', body: c.body || '' });
    });
    if (s.evidence && s.evidence.length) {
      var evHtml = '<div class="exposure-evidence-table">' + s.evidence.map(function(e) {
        return '<div class="exposure-evidence-row"><span class="exposure-evidence-type">' + esc(e.type || '') + '</span>' +
          '<span class="exposure-evidence-ref">' + esc(e.ref || '') + '</span>' +
          (e.hebrew ? '<span class="exposure-evidence-hebrew" dir="rtl" lang="he">' + esc(e.hebrew) + '</span>' : '') +
          (e.note ? '<span class="exposure-evidence-note">' + esc(e.note) + '</span>' : '') +
        '</div>';
      }).join('') + '</div>';
      blocks.push({ heading: 'Свидетельства', bodyHtml: evHtml });
    }
    if (s.reconstruction) blocks.push({ heading: 'Реконструкция', body: s.reconstruction });
    if (s.caveats && s.caveats.length) {
      var cavHtml = '<ul class="exposure-caveats">' + s.caveats.map(function(c) {
        return '<li><span class="exposure-caveat-kind">' + esc(c.kind || '') + '</span> ' + esc(c.text || '') + '</li>';
      }).join('') + '</ul>';
      blocks.push({ heading: 'Оговорки', bodyHtml: cavHtml });
    }
    return blocks;
  }

  // ===== ДОСЬЕ (полный детальный просмотр) =====
  function renderCase(item, opts) {
    opts = opts || {};
    var blocks = buildSections(item);
    var toc = blocks.map(function(b, i) {
      return '<a href="#' + sectionId(i) + '" data-section-link data-index="' + i + '">' + esc(b.heading) + '</a>';
    }).join('');
    var sectionsHtml = blocks.map(function(b, i) {
      var body = b.bodyHtml != null ? b.bodyHtml : renderMd(b.body);
      return '<article class="exposure-section" id="' + sectionId(i) + '" data-section-index="' + i + '">' +
        '<h2>' + esc(b.heading) + '</h2>' +
        '<div class="exposure-section-body">' + body + '</div>' +
      '</article>';
    }).join('');

    var breadcrumb = '<nav class="exposure-breadcrumb" aria-label="Хлебные крошки">' +
      '<a href="#researches">Разоблачения</a> / ' +
      '<span>' + esc(item.category || '') + '</span> / ' +
      '<span>' + esc(item.title || '') + '</span>' +
    '</nav>';

    var tags = (item.tags || []).map(function(t) { return '<span class="exposure-card-tag">' + esc(t) + '</span>'; }).join('');
    var related = (item.related || []).map(function(id) {
      return '<a href="#researches/case/' + encodeURIComponent(id) + '">' + esc(id) + '</a>';
    }).join('');
    var sources = (item.sources || []).map(function(s) {
      return '<li>' + (s.url ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.type || s.ref || 'источник') + '</a>' : esc(s.type || '') + ' ' + esc(s.ref || '')) + '</li>';
    }).join('');

    return '<div class="exposure-case-page">' +
      '<div class="exposure-case-topbar"><a class="research-back-link" href="#researches" data-exposure-back>← Назад к архиву</a></div>' +
      breadcrumb +
      '<div class="research-detail-layout exposure-case-layout">' +
        '<aside class="research-toc exposure-case-toc" data-exposure-toc>' +
          '<h2>Содержание</h2>' + toc +
        '</aside>' +
        '<main class="research-detail-content">' +
          '<header class="research-detail-header">' +
            confidenceBadge(item.confidence) +
            '<h1>' + esc(item.title || '') + '</h1>' +
            '<div class="research-detail-tags">' + tags + '</div>' +
            '<p class="research-detail-summary">' + esc(item.summary || '') + '</p>' +
            '<div class="exposure-progress-wrap"><div class="exposure-progress-track"><div class="exposure-progress-bar" data-exposure-progress></div></div>' +
              '<span class="exposure-progress-label" data-exposure-progress-label">0 из ' + blocks.length + ' секций</span></div>' +
          '</header>' +
          sectionsHtml +
        '</main>' +
        '<aside class="research-infobox exposure-case-infobox">' +
          '<h2>Информация</h2>' +
          '<dl>' +
            '<dt>Статус</dt><dd>' + esc(STATUS_LABELS[item.status] || item.status || '') + '</dd>' +
            '<dt>Обновлено</dt><dd>' + esc(item.updatedAt || '') + '</dd>' +
            (item.author ? '<dt>Автор</dt><dd>' + esc(item.author) + '</dd>' : '') +
          '</dl>' +
          (sources ? '<h3>Источники</h3><ul class="exposure-sources-list">' + sources + '</ul>' : '') +
          (related ? '<h3>Связанные дела</h3><div class="research-related">' + related + '</div>' : '') +
          '<div class="exposure-case-actions">' +
            '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" data-exposure-copy-link>Скопировать ссылку</button>' +
            '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" data-exposure-download-md>Скачать Markdown</button>' +
            (opts.showAskAi === false ? '' : '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" data-exposure-ask-ai data-slug="' + esc(item.slug) + '">Попросить AI дополнить</button>') +
          '</div>' +
        '</aside>' +
      '</div>' +
    '</div>';
  }

  // ===== ЭКСПОРТ =====
  function toMarkdown(item) {
    var blocks = buildSections(item);
    var lines = ['# ' + (item.title || ''), '', item.summary || '', ''];
    blocks.forEach(function(b) {
      lines.push('## ' + b.heading, '', (b.body || (b.bodyHtml ? '(структурированный блок)' : '')), '');
    });
    return lines.join('\n');
  }

  // ===== БИНДИНГ (используется в детальном просмотре) =====
  function bindCase(container, item) {
    var toc = container.querySelector('[data-exposure-toc]');
    var progressBar = container.querySelector('[data-exposure-progress]');
    var progressLabel = container.querySelector('[data-exposure-progress-label]');
    var sections = container.querySelectorAll('.exposure-section');
    var total = sections.length;

    function setActive(idx) {
      if (toc) toc.querySelectorAll('a').forEach(function(a, i) {
        a.classList.toggle('active', i === idx);
      });
      if (progressBar) progressBar.style.width = (total ? Math.round(((idx + 1) / total) * 100) : 0) + '%';
      if (progressLabel) progressLabel.textContent = (idx + 1) + ' из ' + total + ' секций';
    }

    if (total && typeof IntersectionObserver !== 'undefined') {
      var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            var idx = parseInt(entry.target.getAttribute('data-section-index'), 10);
            setActive(idx);
          }
        });
      }, { rootMargin: '-20% 0px -70% 0px' });
      sections.forEach(function(s) { observer.observe(s); });
    }

    var copyBtn = container.querySelector('[data-exposure-copy-link]');
    if (copyBtn) copyBtn.addEventListener('click', function() {
      var url = window.location.origin + window.location.pathname + '#researches/case/' + encodeURIComponent(item.slug);
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function() { if (window.LabToast) LabToast.show('Ссылка скопирована'); });
      }
    });

    var downloadBtn = container.querySelector('[data-exposure-download-md]');
    if (downloadBtn) downloadBtn.addEventListener('click', function() {
      var blob = new Blob([toMarkdown(item)], { type: 'text/markdown;charset=utf-8' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = item.slug + '.md';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });

    var askAiBtn = container.querySelector('[data-exposure-ask-ai]');
    if (askAiBtn) askAiBtn.addEventListener('click', function() {
      item.changelog = item.changelog || [];
      item.changelog.push({ date: new Date().toISOString().slice(0, 10), note: 'Запрошено дополнение от AI-агента (Exposer)' });
      if (window.LabToast) LabToast.show('Запрос добавлен в журнал изменений. Реальный вызов агента ещё не подключён.');
    });

    if (toc) toc.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', function(e) {
        e.preventDefault();
        var target = document.getElementById(this.getAttribute('href').slice(1));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  // ===== ЖИВОЕ ПРЕВЬЮ (в форме создания) =====
  function renderPreview(item) {
    if (!item.title && !item.summary) {
      return '<div class="exposure-preview-empty">Заполните форму — здесь появится страница дела в точности как её увидит читатель</div>';
    }
    return '<div class="exposure-preview-frame">' + renderCase(item, { showAskAi: false }) + '</div>';
  }

  return {
    esc: esc,
    renderMd: renderMd,
    confidenceMeta: confidenceMeta,
    confidenceBadge: confidenceBadge,
    renderCard: renderCard,
    renderCase: renderCase,
    renderPreview: renderPreview,
    bindCase: bindCase,
    toMarkdown: toMarkdown,
    buildSections: buildSections,
    sectionId: sectionId,
    CONFIDENCE_META: CONFIDENCE_META,
    STATUS_LABELS: STATUS_LABELS
  };
})();
