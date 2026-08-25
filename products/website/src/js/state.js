// js/state.js — Управление состоянием приложения
(function(global) {
    'use strict';

    const state = {
        FILES: [],
        currentPath: null,
        bookmarks: [],
        fileHistory: [],
        fontSize: 'medium',
        filteredCache: null
    };

    function loadFromStorage() {
        try {
            state.bookmarks = JSON.parse(localStorage.getItem('golem_bookmarks') || '[]');
            state.fileHistory = JSON.parse(localStorage.getItem('golem_history') || '[]');
            state.fontSize = localStorage.getItem('golem_fontSize') || 'medium';
        } catch (e) {
            console.error('Ошибка загрузки из localStorage:', e);
        }
    }

    function saveBookmarks() {
        try {
            localStorage.setItem('golem_bookmarks', JSON.stringify(state.bookmarks));
        } catch (e) {
            console.error('Ошибка сохранения закладок:', e);
        }
    }

    function saveHistory() {
        try {
            localStorage.setItem('golem_history', JSON.stringify(state.fileHistory));
        } catch (e) {
            console.error('Ошибка сохранения истории:', e);
        }
    }

    function saveFontSize() {
        try {
            localStorage.setItem('golem_fontSize', state.fontSize);
        } catch (e) {
            console.error('Ошибка сохранения размера шрифта:', e);
        }
    }

    function addToHistory(path) {
        state.fileHistory = state.fileHistory.filter(function(h) { return h !== path; });
        state.fileHistory.unshift(path);
        if (state.fileHistory.length > 15) state.fileHistory.pop();
        saveHistory();
    }

    function toggleBookmark(path) {
        if (!path) return;
        const index = state.bookmarks.indexOf(path);
        if (index >= 0) {
            state.bookmarks.splice(index, 1);
        } else {
            state.bookmarks.push(path);
        }
        saveBookmarks();
    }

    function isBookmarked(path) {
        return state.bookmarks.indexOf(path) >= 0;
    }

    global.GolemState = {
        state,
        loadFromStorage,
        saveBookmarks,
        saveHistory,
        saveFontSize,
        addToHistory,
        toggleBookmark,
        isBookmarked
    };

})(window);
