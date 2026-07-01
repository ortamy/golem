/**
 * InterlinearNavigator — навигация по подстрочнику ТаНаХа.
 *
 * Использование:
 *   const nav = new InterlinearNavigator({
 *     container: '#interlinear-container',
 *     booksData: 'data/tanakh-books.json',
 *     cacheBase: 'data/tanakh-cache'
 *   });
 *   nav.init();
 */
class InterlinearNavigator {
  constructor(options = {}) {
    this.container = document.querySelector(options.container || '#interlinear-container');
    this.booksDataUrl = options.booksData || 'data/tanakh-books.json';
    this.cacheBase = options.cacheBase || 'data/tanakh-cache';
    this.books = [];
    this.currentBook = null;
    this.currentChapter = null;
    this.currentChapterData = null;
    this.translationChecker = options.translationChecker || null;
  }

  async init() {
    if (!this.container) {
      console.error('InterlinearNavigator: контейнер не найден');
      return;
    }
    await this.loadBooksData();
    this.renderNavigation();
    this.bindEvents();
    this.loadFromHash();
  }

  async loadBooksData() {
    try {
      const resp = await fetch(this.booksDataUrl);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      this.books = data.books || [];
    } catch (e) {
      console.error('Ошибка загрузки списка книг:', e);
      this.books = [];
    }
  }

  renderNavigation() {
    const nav = document.createElement('div');
    nav.className = 'interlinear-nav';
    nav.innerHTML = `
      <select class="nav-book-select" aria-label="Книга">
        <option value="">— книга —</option>
        ${this.books.map(b => `<option value="${b.id}">${b.ru} (${b.en})</option>`).join('')}
      </select>
      <select class="nav-chapter-select" disabled aria-label="Глава">
        <option value="">— глава —</option>
      </select>
      <div class="nav-buttons">
        <button class="nav-btn nav-prev" disabled>◂ Назад</button>
        <button class="nav-btn nav-next" disabled>Вперёд ▸</button>
      </div>
    `;
    this.container.prepend(nav);
    this.bookSelect = nav.querySelector('.nav-book-select');
    this.chapterSelect = nav.querySelector('.nav-chapter-select');
    this.prevBtn = nav.querySelector('.nav-prev');
    this.nextBtn = nav.querySelector('.nav-next');
  }

  bindEvents() {
    this.bookSelect.addEventListener('change', (e) => {
      this.onBookChange(e.target.value);
    });
    this.chapterSelect.addEventListener('change', (e) => {
      this.onChapterChange(parseInt(e.target.value, 10));
    });
    this.prevBtn.addEventListener('click', () => this.goPrev());
    this.nextBtn.addEventListener('click', () => this.goNext());
    window.addEventListener('hashchange', () => this.loadFromHash());
  }

  onBookChange(bookId) {
    if (!bookId) {
      this.chapterSelect.innerHTML = '<option value="">— глава —</option>';
      this.chapterSelect.disabled = true;
      this.currentBook = null;
      this.currentChapter = null;
      this.currentChapterData = null;
      this.updateButtons();
      this.renderEmpty();
      return;
    }
    this.currentBook = this.books.find(b => b.id === bookId) || null;
    this.populateChapters(this.currentBook);
    this.chapterSelect.disabled = false;
    if (this.currentBook) {
      this.onChapterChange(1);
    }
  }

  populateChapters(book) {
    if (!book) return;
    const count = book.chapters || 1;
    const options = Array.from({ length: count }, (_, i) => {
      const n = i + 1;
      return `<option value="${n}">${n}</option>`;
    }).join('');
    this.chapterSelect.innerHTML = `<option value="">— глава —</option>${options}`;
  }

  onChapterChange(chapter) {
    if (!this.currentBook || !chapter) return;
    this.currentChapter = chapter;
    this.loadChapter(this.currentBook.id, chapter);
    this.updateHash();
    this.updateButtons();
  }

  async loadChapter(bookId, chapter) {
    this.renderLoading();
    const cachePath = `${this.cacheBase}/${bookId}/${chapter}.json`;
    try {
      const resp = await fetch(cachePath);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      this.currentChapterData = data;
      this.renderChapter(data);
    } catch (e) {
      console.error('Ошибка загрузки главы:', e);
      this.renderError(e.message);
    }
  }

  renderChapter(data) {
    if (!this.container) return;
    const content = document.createElement('div');
    content.className = 'interlinear-content';
    const verses = data.verses || [];
    if (!verses.length) {
      content.innerHTML = '<div class="no-verses">Нет стихов</div>';
      this.container.innerHTML = '';
      this.container.appendChild(content);
      return;
    }
    const header = document.createElement('div');
    header.className = 'chapter-header';
    header.textContent = `${data.ref || ''}`;
    content.appendChild(header);
    for (const v of verses) {
      const block = document.createElement('div');
      block.className = 'verse';
      const hebrew = v.hebrew || '';
      const translit = v.hebrew_plain || '';
      const translation = v.english || '';
      block.innerHTML = `
        <div class="verse-num">${v.verse}</div>
        <div class="verse-hebrew">${this.escapeHtml(hebrew)}</div>
        <div class="verse-translit">${this.escapeHtml(translit)}</div>
        <div class="verse-translation">${this.escapeHtml(translation)}</div>
      `;
      content.appendChild(block);
    }
    this.container.innerHTML = '';
    this.container.appendChild(content);
  }

  renderLoading() {
    if (!this.container) return;
    this.container.innerHTML = '<div class="loading">Загрузка…</div>';
  }

  renderError(msg) {
    if (!this.container) return;
    this.container.innerHTML = `<div class="error">Ошибка: ${this.escapeHtml(msg)}</div>`;
  }

  renderEmpty() {
    if (!this.container) return;
    this.container.innerHTML = '<div class="empty">Выберите книгу и главу</div>';
  }

  updateButtons() {
    if (!this.currentBook || !this.currentChapter) {
      this.prevBtn.disabled = true;
      this.nextBtn.disabled = true;
      return;
    }
    const maxChapter = this.currentBook.chapters || 1;
    this.prevBtn.disabled = this.currentChapter <= 1 && !this.hasPrevBook();
    this.nextBtn.disabled = this.currentChapter >= maxChapter && !this.hasNextBook();
  }

  hasPrevBook() {
    if (!this.currentBook) return false;
    const idx = this.books.findIndex(b => b.id === this.currentBook.id);
    return idx > 0;
  }

  hasNextBook() {
    if (!this.currentBook) return false;
    const idx = this.books.findIndex(b => b.id === this.currentBook.id);
    return idx >= 0 && idx < this.books.length - 1;
  }

  goPrev() {
    if (!this.currentBook) return;
    if (this.currentChapter > 1) {
      this.onChapterChange(this.currentChapter - 1);
      return;
    }
    const idx = this.books.findIndex(b => b.id === this.currentBook.id);
    if (idx > 0) {
      const prevBook = this.books[idx - 1];
      this.bookSelect.value = prevBook.id;
      this.onBookChange(prevBook.id);
      const lastChapter = prevBook.chapters || 1;
      this.onChapterChange(lastChapter);
    }
  }

  goNext() {
    if (!this.currentBook) return;
    const maxChapter = this.currentBook.chapters || 1;
    if (this.currentChapter < maxChapter) {
      this.onChapterChange(this.currentChapter + 1);
      return;
    }
    const idx = this.books.findIndex(b => b.id === this.currentBook.id);
    if (idx < this.books.length - 1) {
      const nextBook = this.books[idx + 1];
      this.bookSelect.value = nextBook.id;
      this.onBookChange(nextBook.id);
      this.onChapterChange(1);
    }
  }

  updateHash() {
    if (!this.currentBook || !this.currentChapter) return;
    const hash = `${this.currentBook.id}-${this.currentChapter}`;
    if (window.location.hash !== `#${hash}`) {
      history.pushState(null, '', `#${hash}`);
    }
  }

  loadFromHash() {
    const hash = window.location.hash.replace(/^#/, '');
    if (!hash) return;
    const [bookId, chapterStr] = hash.split('-');
    const chapter = parseInt(chapterStr, 10);
    if (!bookId || !chapter) return;
    const book = this.books.find(b => b.id === bookId);
    if (!book) return;
    this.currentBook = book;
    this.bookSelect.value = bookId;
    this.populateChapters(book);
    this.chapterSelect.disabled = false;
    this.onChapterChange(chapter);
  }

  escapeHtml(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&')
      .replace(/</g, '<')
      .replace(/>/g, '>')
      .replace(/"/g, '"');
  }
}

window.InterlinearNavigator = InterlinearNavigator;