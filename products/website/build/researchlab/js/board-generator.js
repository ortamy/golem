// Research Board Generator - Main JavaScript (webapp version)

// ===== STATE =====
let boardData = {
  title: '',
  conclusion: '',
  evidence: [],
  attachments: [],
  nnModel: 'none',
  nnSettings: {}
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
  // Add initial evidence and attachment fields
  addEvidence();
  addAttachment();
  
  // Form submission handler
  document.getElementById('board-form').addEventListener('submit', function(e) {
    e.preventDefault();
    generateBoard();
  });
});

// ===== DYNAMIC FORM FIELDS =====
function addEvidence() {
  const container = document.getElementById('evidence-list');
  const id = Date.now();
  const index = container.children.length + 1;
  
  const div = document.createElement('div');
  div.className = 'evidence-item';
  div.dataset.id = id;
  div.style.cssText = 'margin-bottom: 12px; padding: 12px; background: var(--bg-primary); border: 1px solid var(--border-light); border-radius: 4px;';
  
  div.innerHTML = `
    <div style="display: flex; gap: 8px; margin-bottom: 8px;">
      <input type="text" placeholder="Название улики #${index}" 
        style="flex: 1; padding: 8px 10px; font-family: 'EB Garamond', Georgia, serif; font-size: 14px; border: 1px solid var(--border-light); border-radius: 4px; background: var(--bg-card); color: var(--text-primary); outline: none;"
        onfocus="this.style.borderColor='var(--accent-gold)'" onblur="this.style.borderColor='var(--border-light)'">
      <button type="button" onclick="removeEvidence(${id})" 
        style="padding: 8px 12px; background: var(--accent-red); color: #faf3e0; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600;">
        ✕
      </button>
    </div>
    <textarea placeholder="Описание улики..." rows="2"
      style="width: 100%; padding: 8px 10px; font-family: 'EB Garamond', Georgia, serif; font-size: 14px; border: 1px solid var(--border-light); border-radius: 4px; background: var(--bg-card); color: var(--text-primary); outline: none; resize: vertical;"
      onfocus="this.style.borderColor='var(--accent-gold)'" onblur="this.style.borderColor='var(--border-light)'"></textarea>
  `;
  
  container.appendChild(div);
}

function removeEvidence(id) {
  const item = document.querySelector(`.evidence-item[data-id="${id}"]`);
  if (item) {
    item.remove();
    // Renumber remaining items
    const items = document.querySelectorAll('.evidence-item');
    items.forEach((item, index) => {
      const input = item.querySelector('input[type="text"]');
      if (input) {
        input.placeholder = `Название улики #${index + 1}`;
      }
    });
  }
}

function addAttachment() {
  const container = document.getElementById('attachments-list');
  const id = Date.now();
  const index = container.children.length + 1;
  
  const div = document.createElement('div');
  div.className = 'attachment-item';
  div.dataset.id = id;
  div.style.cssText = 'margin-bottom: 12px; padding: 12px; background: var(--bg-primary); border: 1px solid var(--border-light); border-radius: 4px;';
  
  div.innerHTML = `
    <div style="display: flex; gap: 8px; margin-bottom: 8px;">
      <input type="text" placeholder="Название вложения #${index}" 
        style="flex: 1; padding: 8px 10px; font-family: 'EB Garamond', Georgia, serif; font-size: 14px; border: 1px solid var(--border-light); border-radius: 4px; background: var(--bg-card); color: var(--text-primary); outline: none;"
        onfocus="this.style.borderColor='var(--accent-gold)'" onblur="this.style.borderColor='var(--border-light)'">
      <button type="button" onclick="removeAttachment(${id})" 
        style="padding: 8px 12px; background: var(--accent-red); color: #faf3e0; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600;">
        ✕
      </button>
    </div>
    <input type="text" placeholder="Ссылка на изображение/документ (URL)" 
      style="width: 100%; padding: 8px 10px; font-family: 'EB Garamond', Georgia, serif; font-size: 14px; border: 1px solid var(--border-light); border-radius: 4px; background: var(--bg-card); color: var(--text-primary); outline: none; margin-bottom: 8px;"
      onfocus="this.style.borderColor='var(--accent-gold)'" onblur="this.style.borderColor='var(--border-light)'">
    <textarea placeholder="Краткое описание..." rows="2"
      style="width: 100%; padding: 8px 10px; font-family: 'EB Garamond', Georgia, serif; font-size: 14px; border: 1px solid var(--border-light); border-radius: 4px; background: var(--bg-card); color: var(--text-primary); outline: none; resize: vertical;"
      onfocus="this.style.borderColor='var(--accent-gold)'" onblur="this.style.borderColor='var(--border-light)'"></textarea>
  `;
  
  container.appendChild(div);
}

function removeAttachment(id) {
  const item = document.querySelector(`.attachment-item[data-id="${id}"]`);
  if (item) {
    item.remove();
    // Renumber remaining items
    const items = document.querySelectorAll('.attachment-item');
    items.forEach((item, index) => {
      const input = item.querySelector('input[type="text"]');
      if (input) {
        input.placeholder = `Название вложения #${index + 1}`;
      }
    });
  }
}

// ===== NEURAL NETWORK SETTINGS =====
function updateNNSettings() {
  const model = document.getElementById('nn-model').value;
  const settingsDiv = document.getElementById('nn-settings');
  const generateAIBtn = document.getElementById('btn-generate-ai');
  
  if (model === 'none') {
    settingsDiv.style.display = 'none';
    generateAIBtn.style.display = 'none';
  } else {
    settingsDiv.style.display = 'block';
    generateAIBtn.style.display = 'inline-block';
  }
}

// ===== BOARD GENERATION =====
function generateBoard() {
  // Collect form data
  boardData.title = document.getElementById('board-title').value;
  boardData.conclusion = document.getElementById('main-conclusion').value;
  boardData.nnModel = document.getElementById('nn-model').value;
  
  // Collect evidence
  boardData.evidence = [];
  const evidenceItems = document.querySelectorAll('.evidence-item');
  evidenceItems.forEach((item, index) => {
    const title = item.querySelector('input[type="text"]').value;
    const description = item.querySelector('textarea').value;
    if (title.trim()) {
      boardData.evidence.push({
        number: index + 1,
        title: title,
        description: description
      });
    }
  });
  
  // Collect attachments
  boardData.attachments = [];
  const attachmentItems = document.querySelectorAll('.attachment-item');
  attachmentItems.forEach((item, index) => {
    const name = item.querySelectorAll('input[type="text"]')[0].value;
    const url = item.querySelectorAll('input[type="text"]')[1].value;
    const desc = item.querySelector('textarea').value;
    if (name.trim()) {
      boardData.attachments.push({
        name: name,
        url: url,
        description: desc
      });
    }
  });
  
  // Collect NN settings if needed
  if (boardData.nnModel !== 'none') {
    boardData.nnSettings = {
      apiKey: document.getElementById('nn-api-key').value,
      endpoint: document.getElementById('nn-endpoint').value,
      resolution: document.getElementById('nn-resolution').value,
      style: document.getElementById('nn-style').value
    };
  }
  
  // Render board
  renderBoard();
  
  // Generate prompt
  generatePrompt();
  
  // Show export section
  document.getElementById('export-section').style.display = 'block';
  
  // Show board preview
  document.getElementById('board-preview').style.display = 'block';
  document.getElementById('board-placeholder').style.display = 'none';
}

function renderBoard() {
  const preview = document.getElementById('board-preview');
  
  // Build evidence HTML
  let evidenceHTML = '';
  boardData.evidence.forEach(ev => {
    evidenceHTML += `
      <div class="evidence-card">
        <div class="evidence-number">${ev.number}</div>
        <div class="evidence-title">${escapeHtml(ev.title)}</div>
        <div class="evidence-description">${escapeHtml(ev.description)}</div>
      </div>
    `;
  });
  
  // Build attachments HTML
  let attachmentsHTML = '';
  if (boardData.attachments.length > 0) {
    attachmentsHTML = '<div class="attachments-section"><div class="section-title">Вложения</div><div class="attachments-grid">';
    boardData.attachments.forEach(att => {
      let thumbnailHTML = '';
      if (att.url) {
        thumbnailHTML = `<img src="${escapeHtml(att.url)}" alt="${escapeHtml(att.name)}" class="attachment-thumbnail" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">`;
        thumbnailHTML += `<div class="attachment-placeholder" style="display: none;">📎</div>`;
      } else {
        thumbnailHTML = `<div class="attachment-placeholder">📎</div>`;
      }
      
      attachmentsHTML += `
        <div class="attachment-card">
          ${thumbnailHTML}
          <div class="attachment-name">${escapeHtml(att.name)}</div>
          ${att.description ? `<div class="attachment-desc">${escapeHtml(att.description)}</div>` : ''}
        </div>
      `;
    });
    attachmentsHTML += '</div></div>';
  }
  
  // Build board HTML
  const boardHTML = `
    <div class="research-board">
      <div class="board-decoration top-left">✦</div>
      <div class="board-decoration top-right">✦</div>
      <div class="board-decoration bottom-left">✦</div>
      <div class="board-decoration bottom-right">✦</div>
      
      <div class="board-title">${escapeHtml(boardData.title)}</div>
      
      <div class="board-conclusion">
        <div class="board-conclusion-label">Вывод / Главная улика</div>
        <div class="board-conclusion-text">${escapeHtml(boardData.conclusion)}</div>
      </div>
      
      <div class="evidence-section">
        <div class="section-title">Улики</div>
        <div class="evidence-grid">
          ${evidenceHTML}
        </div>
      </div>
      
      ${attachmentsHTML}
    </div>
  `;
  
  preview.innerHTML = boardHTML;
}

function generatePrompt() {
  const promptSection = document.getElementById('prompt-section');
  const promptText = document.getElementById('generated-prompt');
  
  let prompt = `Исследовательская доска: "${boardData.title}"\n\n`;
  prompt += `Главный вывод: ${boardData.conclusion}\n\n`;
  prompt += `Улики:\n`;
  boardData.evidence.forEach((ev, i) => {
    prompt += `${i + 1}. ${ev.title}: ${ev.description}\n`;
  });
  
  if (boardData.attachments.length > 0) {
    prompt += `\nВложения:\n`;
    boardData.attachments.forEach((att, i) => {
      prompt += `${i + 1}. ${att.name}${att.url ? ` (${att.url})` : ''}: ${att.description}\n`;
    });
  }
  
  // Add AI generation instructions if model selected
  if (boardData.nnModel !== 'none') {
    prompt += `\n---\nПромпт для генерации изображения:\n`;
    prompt += `Создай визуальную исследовательскую доску в стиле древнего манускрипта на пергаменте. `;
    prompt += `Заголовок: "${boardData.title}". `;
    prompt += `Главный вывод: "${boardData.conclusion}". `;
    prompt += `На доске должны быть расположены ${boardData.evidence.length} карточек с уликами, `;
    prompt += `связанных красными нитями. `;
    prompt += `Стиль: пергамент, коричневые тона, золотые акценты, рукописный шрифт. `;
    prompt += `Атмосфера: древняя библиотека, скрипторий, таинственное освещение.`;
    
    if (boardData.nnModel === 'local') {
      prompt += `\n\n[Локальная модель] Используй эндпоинт: ${boardData.nnSettings.endpoint || 'http://localhost:8188'}`;
    } else if (boardData.nnModel === 'dalle') {
      prompt += `\n\n[DALL-E] Используй API ключ для генерации`;
    } else if (boardData.nnModel === 'midjourney') {
      prompt += `\n\n[Midjourney] Используй API для генерации`;
    } else if (boardData.nnModel === 'openrouter') {
      prompt += `\n\n[OpenRouter] Используй выбранную модель для генерации`;
    }
  }
  
  promptText.textContent = prompt;
  promptSection.style.display = 'block';
}

// ===== EXPORT FUNCTIONS =====
function exportPNG() {
  const board = document.querySelector('.research-board');
  if (!board) {
    alert('Сначала сгенерируйте доску!');
    return;
  }
  
  // Use html2canvas
  if (typeof html2canvas !== 'undefined') {
    html2canvas(board, {
      backgroundColor: '#ede0c8',
      scale: 2,
      useCORS: true,
      logging: false
    }).then(canvas => {
      const link = document.createElement('a');
      link.download = `board-${Date.now()}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    }).catch(err => {
      console.error('PNG export error:', err);
      alert('Ошибка при экспорте PNG. Попробуйте другой метод.');
    });
  } else {
    alert('Библиотека html2canvas не загружена. Проверьте подключение к интернету.');
  }
}

function exportPDF() {
  const board = document.querySelector('.research-board');
  if (!board) {
    alert('Сначала сгенерируйте доску!');
    return;
  }
  
  // Use window.print() with print styles
  window.print();
}

function exportTXT() {
  if (!boardData.title) {
    alert('Сначала сгенерируйте доску!');
    return;
  }
  
  let text = `ИССЛЕДОВАТЕЛЬСКАЯ ДОСКА\n`;
  text += `${'='.repeat(50)}\n\n`;
  text += `Заголовок: ${boardData.title}\n\n`;
  text += `ГЛАВНЫЙ ВЫВОД:\n${boardData.conclusion}\n\n`;
  text += `УЛИКИ:\n`;
  boardData.evidence.forEach((ev, i) => {
    text += `${i + 1}. ${ev.title}\n`;
    text += `   ${ev.description}\n\n`;
  });
  
  if (boardData.attachments.length > 0) {
    text += `ВЛОЖЕНИЯ:\n`;
    boardData.attachments.forEach((att, i) => {
      text += `${i + 1}. ${att.name}\n`;
      if (att.url) text += `   URL: ${att.url}\n`;
      if (att.description) text += `   ${att.description}\n\n`;
    });
  }
  
  text += `${'='.repeat(50)}\n`;
  text += `Создано: ${new Date().toLocaleString('ru-RU')}\n`;
  text += `Проект: Golem — Свидетель Истины\n`;
  
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const link = document.createElement('a');
  link.download = `board-${Date.now()}.txt`;
  link.href = URL.createObjectURL(blob);
  link.click();
  URL.revokeObjectURL(link.href);
}

function copyPrompt() {
  const promptText = document.getElementById('generated-prompt').textContent;
  if (!promptText) {
    alert('Сначала сгенерируйте доску!');
    return;
  }
  
  navigator.clipboard.writeText(promptText).then(() => {
    showToast('Промпт скопирован в буфер обмена!');
  }).catch(err => {
    console.error('Copy error:', err);
    alert('Не удалось скопировать промпт');
  });
}

// ===== UTILITIES =====
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function showToast(message) {
  const toast = document.getElementById('copy-toast');
  toast.textContent = message;
  toast.style.opacity = '1';
  setTimeout(() => {
    toast.style.opacity = '0';
  }, 2000);
}

// ===== AI IMAGE GENERATION =====
async function generateWithAI() {
  const model = document.getElementById('nn-model').value;
  const apiKey = document.getElementById('nn-api-key').value;
  const endpoint = document.getElementById('nn-endpoint').value;
  const resolution = document.getElementById('nn-resolution').value;
  const style = document.getElementById('nn-style').value;
  
  if (!apiKey && model !== 'local') {
    alert('Введите API ключ для выбранной модели');
    return;
  }
  
  if (model === 'local' && !endpoint) {
    alert('Введите URL эндпоинта для локальной модели');
    return;
  }
  
  // Generate prompt
  const prompt = document.getElementById('generated-prompt').textContent;
  
  try {
    let imageUrl;
    
    if (model === 'local') {
      // Local Stable Diffusion / ComfyUI
      imageUrl = await generateLocalImage(endpoint, prompt, resolution);
    } else if (model === 'dalle') {
      // DALL-E
      imageUrl = await generateDALLEImage(apiKey, prompt, resolution);
    } else if (model === 'midjourney') {
      // Midjourney (via API proxy)
      imageUrl = await generateMidjourneyImage(apiKey, prompt);
    } else if (model === 'openrouter') {
      // OpenRouter
      imageUrl = await generateOpenRouterImage(apiKey, endpoint, prompt, resolution);
    }
    
    if (imageUrl) {
      showToast('Изображение сгенерировано! (В разработке: полная интеграция)');
      // TODO: Display generated image in preview
      console.log('Generated image URL:', imageUrl);
    }
  } catch (error) {
    console.error('AI generation error:', error);
    alert('Ошибка при генерации изображения: ' + error.message);
  }
}

// Placeholder functions for AI generation
async function generateLocalImage(endpoint, prompt, resolution) {
  // TODO: Implement ComfyUI / SD WebUI API integration
  console.log('Local generation:', endpoint, prompt, resolution);
  throw new Error('Локальная генерация в разработке');
}

async function generateDALLEImage(apiKey, prompt, resolution) {
  // TODO: Implement DALL-E API integration
  console.log('DALL-E generation:', prompt, resolution);
  throw new Error('DALL-E генерация в разработке');
}

async function generateMidjourneyImage(apiKey, prompt) {
  // TODO: Implement Midjourney API integration
  console.log('Midjourney generation:', prompt);
  throw new Error('Midjourney генерация в разработке');
}

async function generateOpenRouterImage(apiKey, endpoint, prompt, resolution) {
  // TODO: Implement OpenRouter API integration
  console.log('OpenRouter generation:', endpoint, prompt, resolution);
  throw new Error('OpenRouter генерация в разработке');
}
