// js/i18n.js — Internationalization system
(function(global) {
    'use strict';

    let currentLang = 'ru';
    let translations = {};

    // Load translations from JSON
    async function loadLanguage(lang) {
        try {
            const response = await fetch('../locales/' + lang + '.json');
            if (!response.ok) throw new Error('Failed to load ' + lang);
            translations = await response.json();
            currentLang = lang;
            
            // Update HTML lang and dir attributes
            document.documentElement.lang = translations.lang;
            document.documentElement.dir = translations.dir;
            
            // Apply translations
            applyTranslations();
            
            // Save preference
            localStorage.setItem('golem-lang', lang);
            
            return true;
        } catch (e) {
            console.error('Error loading language:', e);
            return false;
        }
    }

    // Apply translations to all elements with data-i18n attribute
    function applyTranslations() {
        if (!translations.pages) return;
        
        const pageName = getCurrentPage();
        const pageTranslations = translations.pages[pageName] || {};
        
        // Update elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            const key = el.getAttribute('data-i18n');
            const value = getNestedValue(translations, key);
            if (value) {
                el.textContent = value;
            }
        });
        
        // Update page title
        if (pageTranslations.title) {
            document.title = pageTranslations.title;
        }
        
        // Update site name
        if (translations.site && translations.site.name) {
            const siteNameEl = document.querySelector('.logo a');
            if (siteNameEl) {
                siteNameEl.textContent = translations.site.name;
            }
        }
    }

    // Get nested value from object using dot notation
    function getNestedValue(obj, path) {
        return path.split('.').reduce(function(acc, part) {
            return acc && acc[part];
        }, obj);
    }

    // Get current page name from URL
    function getCurrentPage() {
        const path = window.location.pathname;
        const match = path.match(/\/([^\/]+)\/?$/);
        if (match && match[1]) {
            return match[1].replace('.html', '');
        }
        return 'index';
    }

    // Get current language
    function getCurrentLanguage() {
        return currentLang;
    }

    // Get translations object
    function getTranslations() {
        return translations;
    }

    // Initialize i18n
    async function init() {
        // Check for saved language preference
        const savedLang = localStorage.getItem('golem-lang');
        
        // Check URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        
        // Determine which language to load
        const langToLoad = urlLang || savedLang || 'ru';
        
        // Validate language
        const validLangs = ['ru', 'en', 'he'];
        const lang = validLangs.includes(langToLoad) ? langToLoad : 'ru';
        
        // Load the language
        await loadLanguage(lang);
        
        // Update language switcher UI
        updateLanguageSwitcher(lang);
    }

    // Update language switcher buttons
    function updateLanguageSwitcher(activeLang) {
        document.querySelectorAll('.lang-switch-btn').forEach(function(btn) {
            const lang = btn.getAttribute('data-lang');
            if (lang === activeLang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Switch language
    async function switchLanguage(lang) {
        if (lang === currentLang) return;
        
        const success = await loadLanguage(lang);
        if (success) {
            // Update URL without reload
            const url = new URL(window.location);
            url.searchParams.set('lang', lang);
            window.history.pushState({}, '', url);
            
            // Reload page to apply RTL/LTR and reinitialize
            window.location.reload();
        }
    }

    // Export to global scope
    global.GolemI18n = {
        init,
        loadLanguage,
        switchLanguage,
        getCurrentLanguage,
        getTranslations,
        applyTranslations
    };

})(window);