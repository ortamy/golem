/**
 * vision.js — Визуальный анализатор на базе SmolVLM-256M
 * 
 * Поддерживает:
 * - Hugging Face Inference API (бесплатно)
 * - Локальный сервер (FastAPI / transformers.js)
 * - Drag & drop загрузку изображений
 * - Историю анализов (localStorage)
 */

const Vision = (function() {
  'use strict';

  // ===== КОНСТАНТЫ =====
  const HF_API_URL = 'https://api-inference.huggingface.co/models/HuggingFaceTB/SmolVLM-256M-Instruct';
  const LOCAL_API_URL = 'http://localhost:8000/describe';
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
  const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
  const STORAGE_KEY = 'golem_vision_history';
  const API_KEY_STORAGE = 'golem_hf_api_key';

  // ===== СОСТОЯНИЕ =====
  let state = {
    mode: 'huggingface',   // 'huggingface' | 'local'
    currentFile: null,
    currentBase64: null,
    isAnalyzing: false,
    history: []
  };

  // ===== DOM ССЫЛКИ =====
  let els = {};

  // ===== ИНИЦИАЛИЗАЦИЯ =====
  function init() {
    // Кэшируем DOM элементы
    els = {
      uploadZone: document.getElementById('uploadZone'),
      fileInput: document.getElementById('fileInput'),
      uploadPlaceholder: document.getElementById('uploadPlaceholder'),
      imagePreview: document.getElementById('imagePreview'),
      previewImg: document.getElementById('previewImg'),
      analyzeBtn: document.getElementById('analyzeBtn'),
      spinner: document.getElementById('spinner'),
      resultCard: document.getElementById('resultCard'),
      resultBody: document.getElementById('resultBody'),
      resultModel: document.getElementById('resultModel'),
      resultTimestamp: document.getElementById('resultTimestamp'),
      errorCard: document.getElementById('errorCard'),
      errorBody: document.getElementById('errorBody'),
      historyList: document.getElementById('historyList'),
      apiKeyInput: document.getElementById('api-key'),
      apiSection: document.getElementById('api-section')
    };

    // Загружаем API ключ из localStorage
    const savedKey = localStorage.getItem(API_KEY_STORAGE);
    if (savedKey) {
      els.apiKeyInput.value = savedKey;
    }

    // Загружаем историю
    loadHistory();

    // Настраиваем drag & drop
    setupDragDrop();

    // Восстанавливаем режим
    const savedMode = localStorage.getItem('golem_vision_mode');
    if (savedMode) {
      setMode(savedMode);
    }

    console.log('[Vision] Модуль инициализирован');
  }

  // ===== DRAG & DROP =====
  function setupDragDrop() {
    const zone = els.uploadZone;

    zone.addEventListener('dragover', function(e) {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.add('drag-over');
    });

    zone.addEventListener('dragleave', function(e) {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.remove('drag-over');
    });

    zone.addEventListener('drop', function(e) {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.remove('drag-over');

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleFileEvent(files[0]);
      }
    });
  }

  // ===== ЗАГРУЗКА ФАЙЛА =====
  function handleFileEvent(file) {
    // Валидация
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      showError('Неподдерживаемый формат. Используйте PNG, JPG или WEBP.');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      showError('Файл слишком большой. Максимальный размер — 10 МБ.');
      return;
    }

    state.currentFile = file;

    // Читаем файл как DataURL (base64)
    const reader = new FileReader();
    reader.onload = function(e) {
      state.currentBase64 = e.target.result;
      showPreview(state.currentBase64);
      els.analyzeBtn.disabled = false;
    };
    reader.onerror = function() {
      showError('Ошибка чтения файла.');
    };
    reader.readAsDataURL(file);
  }

  // ===== ПРЕДПРОСМОТР =====
  function showPreview(src) {
    els.previewImg.src = src;
    els.imagePreview.classList.add('show');
    els.uploadPlaceholder.style.display = 'none';
    els.uploadZone.classList.add('has-image');
  }

  function removeImage() {
    state.currentFile = null;
    state.currentBase64 = null;
    els.previewImg.src = '';
    els.imagePreview.classList.remove('show');
    els.uploadPlaceholder.style.display = '';
    els.uploadZone.classList.remove('has-image');
    els.fileInput.value = '';
    els.analyzeBtn.disabled = true;
    hideError();
  }

  // ===== РЕЖИМ =====
  function setMode(mode) {
    state.mode = mode;
    localStorage.setItem('golem_vision_mode', mode);

    // Обновляем UI кнопок
    document.querySelectorAll('.mode-btn').forEach(function(btn) {
      btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Обновляем подсказку в API секции
    const label = els.apiSection.querySelector('label');
    const hint = els.apiSection.querySelector('.api-hint');

    if (mode === 'huggingface') {
      label.textContent = '🔑 API ключ Hugging Face';
      hint.innerHTML = 'Получите бесплатный ключ на <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noopener" style="color:#b8860b;">huggingface.co/settings/tokens</a>';
      els.apiKeyInput.placeholder = 'hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
    } else {
      label.textContent = '💻 Локальный сервер';
      hint.textContent = 'Убедитесь, что локальный сервер запущен на http://localhost:8000';
      els.apiKeyInput.placeholder = 'API ключ не требуется для локального режима';
    }
  }

  // ===== API КЛЮЧ =====
  function saveApiKey() {
    const key = els.apiKeyInput.value.trim();
    if (key) {
      localStorage.setItem(API_KEY_STORAGE, key);
      showToast('API ключ сохранён');
    } else {
      localStorage.removeItem(API_KEY_STORAGE);
      showToast('API ключ удалён');
    }
  }

  // ===== АНАЛИЗ =====
  async function analyze() {
    if (state.isAnalyzing) return;
    if (!state.currentBase64) {
      showError('Сначала загрузите изображение.');
      return;
    }

    // Проверяем ключ для HF режима
    if (state.mode === 'huggingface') {
      const key = els.apiKeyInput.value.trim();
      if (!key) {
        showError('Введите API ключ Hugging Face в настройках выше.');
        return;
      }
    }

    state.isAnalyzing = true;
    els.analyzeBtn.disabled = true;
    els.analyzeBtn.textContent = '⏳ Анализ…';
    showSpinner();
    hideResult();
    hideError();

    try {
      let description;

      if (state.mode === 'huggingface') {
        description = await analyzeViaHuggingFace();
      } else {
        description = await analyzeViaLocal();
      }

      showResult(description);
      addToHistory(description);

    } catch (err) {
      showError(err.message || 'Произошла ошибка при анализе изображения.');
      console.error('[Vision] Ошибка анализа:', err);
    } finally {
      state.isAnalyzing = false;
      els.analyzeBtn.disabled = false;
      els.analyzeBtn.textContent = '🔍 Проанализировать изображение';
      hideSpinner();
    }
  }

  // ===== АНАЛИЗ ЧЕРЕЗ HUGGING FACE =====
  async function analyzeViaHuggingFace() {
    const apiKey = els.apiKeyInput.value.trim();

    // Извлекаем чистые base64 данные (без префикса data:image/...)
    const base64Data = state.currentBase64.split(',')[1];

    const response = await fetch(HF_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        inputs: {
          image: base64Data,
          prompt: 'Опиши подробно, что изображено на этой картинке. Обрати внимание на текст, символы, знаки, объекты и их расположение. Если видишь древние письмена, символы или подозрительные элементы — укажи их.'
        },
        parameters: {
          max_new_tokens: 500,
          temperature: 0.2,
          top_p: 0.95
        }
      })
    });

    if (!response.ok) {
      let errorMsg = 'Ошибка API: ' + response.status;
      try {
        const errData = await response.json();
        if (errData.error) {
          errorMsg += ' — ' + errData.error;
        }
      } catch (e) {
        // ignore
      }
      throw new Error(errorMsg);
    }

    const data = await response.json();

    // Hugging Face может вернуть массив или объект
    if (Array.isArray(data) && data.length > 0) {
      return data[0].generated_text || JSON.stringify(data[0]);
    } else if (data.generated_text) {
      return data.generated_text;
    } else if (typeof data === 'string') {
      return data;
    } else {
      return JSON.stringify(data, null, 2);
    }
  }

  // ===== АНАЛИЗ ЧЕРЕЗ ЛОКАЛЬНЫЙ СЕРВЕР =====
  async function analyzeViaLocal() {
    const response = await fetch(LOCAL_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image: state.currentBase64,
        prompt: 'Опиши подробно, что изображено на этой картинке. Обрати внимание на текст, символы, знаки, объекты и их расположение. Если видишь древние письмена, символы или подозрительные элементы — укажи их.'
      })
    });

    if (!response.ok) {
      let errorMsg = 'Ошибка локального сервера: ' + response.status;
      try {
        const errData = await response.json();
        if (errData.detail) {
          errorMsg += ' — ' + errData.detail;
        }
      } catch (e) {
        // ignore
      }
      throw new Error(errorMsg);
    }

    const data = await response.json();
    return data.description || data.text || data.result || JSON.stringify(data);
  }

  // ===== ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА =====
  function showResult(text) {
    els.resultBody.textContent = text;
    els.resultModel.textContent = state.mode === 'huggingface' ? 'SmolVLM-256M (HF)' : 'SmolVLM-256M (Local)';
    els.resultTimestamp.textContent = new Date().toLocaleString('ru-RU');
    els.resultCard.classList.add('show');
    els.resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function hideResult() {
    els.resultCard.classList.remove('show');
  }

  // ===== ОТОБРАЖЕНИЕ ОШИБКИ =====
  function showError(message) {
    els.errorBody.textContent = message;
    els.errorCard.classList.add('show');
    els.errorCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function hideError() {
    els.errorCard.classList.remove('show');
  }

  // ===== СПИННЕР =====
  function showSpinner() {
    els.spinner.classList.add('show');
  }

  function hideSpinner() {
    els.spinner.classList.remove('show');
  }

  // ===== ИСТОРИЯ =====
  function loadHistory() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        state.history = JSON.parse(stored);
      }
    } catch (e) {
      state.history = [];
    }
    renderHistory();
  }

  function saveHistory() {
    try {
      // Храним только последние 20 записей
      if (state.history.length > 20) {
        state.history = state.history.slice(-20);
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.history));
    } catch (e) {
      console.warn('[Vision] Не удалось сохранить историю:', e);
    }
  }

  function addToHistory(description) {
    const entry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      imageData: state.currentBase64, // сохраняем миниатюру
      description: description.substring(0, 200) + (description.length > 200 ? '…' : ''),
      mode: state.mode
    };

    state.history.push(entry);
    saveHistory();
    renderHistory();
  }

  function renderHistory() {
    if (state.history.length === 0) {
      els.historyList.innerHTML = '<div class="history-empty">Пока нет выполненных анализов.</div>';
      return;
    }

    let html = '';
    // Показываем от новых к старым
    const items = state.history.slice().reverse();

    items.forEach(function(entry) {
      const date = new Date(entry.timestamp);
      const dateStr = date.toLocaleString('ru-RU');
      const modeLabel = entry.mode === 'huggingface' ? '🤗 HF' : '💻 Local';

      html += '<div class="history-item" onclick="Vision.loadHistoryItem(' + entry.id + ')">';
      html += '  <img class="thumb" src="' + entry.imageData + '" alt="thumb" />';
      html += '  <div class="info">';
      html += '    <div class="preview-text">' + escapeHtml(entry.description) + '</div>';
      html += '    <div class="timestamp">' + dateStr + ' · ' + modeLabel + '</div>';
      html += '  </div>';
      html += '</div>';
    });

    els.historyList.innerHTML = html;
  }

  function loadHistoryItem(id) {
    const entry = state.history.find(function(e) { return e.id === id; });
    if (!entry) return;

    // Восстанавливаем изображение
    state.currentBase64 = entry.imageData;
    showPreview(entry.imageData);
    els.analyzeBtn.disabled = false;

    // Показываем результат
    els.resultBody.textContent = entry.description;
    els.resultModel.textContent = entry.mode === 'huggingface' ? 'SmolVLM-256M (HF)' : 'SmolVLM-256M (Local)';
    els.resultTimestamp.textContent = new Date(entry.timestamp).toLocaleString('ru-RU');
    els.resultCard.classList.add('show');

    // Прокрутка к результату
    els.resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ===== TOAST =====
  function showToast(message) {
    let toast = document.getElementById('vision-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'vision-toast';
      toast.style.cssText = 'position: fixed; top: 24px; left: 50%; transform: translateX(-50%); background: #2c1810; color: #ede0c8; padding: 10px 24px; font-size: 14px; font-family: "EB Garamond", Georgia, serif; opacity: 0; pointer-events: none; z-index: 9999; border-radius: 4px; border: 1px solid #b8860b; transition: opacity 0.4s ease;';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.opacity = '1';
    setTimeout(function() {
      toast.style.opacity = '0';
    }, 2000);
  }

  // ===== УТИЛИТЫ =====
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ===== ПУБЛИЧНЫЙ API =====
  return {
    init: init,
    handleFile: function(e) { handleFileEvent(e.target.files[0]); },
    removeImage: removeImage,
    setMode: setMode,
    saveApiKey: saveApiKey,
    analyze: analyze,
    loadHistoryItem: loadHistoryItem
  };
})();

// ===== АВТОЗАПУСК =====
document.addEventListener('DOMContentLoaded', function() {
  Vision.init();
});