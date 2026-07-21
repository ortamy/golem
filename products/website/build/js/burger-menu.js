// currentScript валиден только во время синхронного выполнения — захватываем сразу.
var burgerMenuScriptEl = document.currentScript || document.querySelector('script[src*="burger-menu.js"]');

document.addEventListener('DOMContentLoaded', function() {
    // Путь к самому скрипту (../../js/burger-menu.js) уже верно резолвится
    // браузером с учётом любого суб-пути хостинга (например /golem/ на GitHub Pages).
    // Строим ссылки от корня сайта (js/ на уровень выше), а не от глубины URL,
    // которая не знает о суб-пути хостинга.
    var prefix = new URL('../', burgerMenuScriptEl.src).href;

    var htmlLang = document.documentElement.lang || 'ru';
    var isRTL = document.documentElement.dir === 'rtl';
    
    var menuTexts = {
        ru: { home: 'Главная', tanakh: 'Чтение ТаНаХа', research: 'Исследования', methods: 'Методы разоблачения', dictionaries: 'Словари', methodology: 'Методология', tools: 'Инструменты', about: 'О проекте', logo: 'ГОЛЕМ' },
        en: { home: 'Home', tanakh: 'Tanakh Reading', research: 'Research', methods: 'Exposure Methods', dictionaries: 'Dictionaries', methodology: 'Methodology', tools: 'Tools', about: 'About', logo: 'GOLEM' },
        he: { home: 'ראשי', tanakh: 'קריאת תנ״ך', research: 'מחקר', methods: 'שיטות חשיפה', dictionaries: 'מילונים', methodology: 'מתודולוגיה', tools: 'כלים', about: 'אודות', logo: 'גולם' }
    };
    
    var texts = menuTexts[htmlLang] || menuTexts.ru;
    
    var langOptions = {
        ru: [
            { value: '?lang=ru', label: 'RU', selected: htmlLang === 'ru' },
            { value: '?lang=en', label: 'EN', selected: htmlLang === 'en' },
            { value: '?lang=he', label: 'HE', selected: htmlLang === 'he' }
        ],
        en: [
            { value: '?lang=en', label: 'EN', selected: htmlLang === 'en' },
            { value: '?lang=ru', label: 'RU', selected: htmlLang === 'ru' },
            { value: '?lang=he', label: 'HE', selected: htmlLang === 'he' }
        ],
        he: [
            { value: '?lang=he', label: 'HE', selected: htmlLang === 'he' },
            { value: '?lang=ru', label: 'RU', selected: htmlLang === 'ru' },
            { value: '?lang=en', label: 'EN', selected: htmlLang === 'en' }
        ]
    };
    
    var options = langOptions[htmlLang] || langOptions.ru;
    var selectHTML = '<select onchange="if(this.value) GolemI18n.switchLanguage(this.value.split(\'=\')[1])">';
    options.forEach(function(opt) {
        selectHTML += '<option value="' + opt.value + '"' + (opt.selected ? ' selected' : '') + '>' + opt.label + '</option>';
    });
    selectHTML += '</select>';
    
    var rtlStyle = isRTL ? ' style="direction:rtl;text-align:right"' : '';
    
    var burgerHTML = '<div class="side-panel-overlay" id="sidePanelOverlay" onclick="toggleSidePanel()"></div>' +
        '<div class="side-panel" id="sidePanel"' + rtlStyle + '>' +
        '  <div class="side-panel-header">' +
        '    <span class="logo-text">' + texts.logo + '</span>' +
        '    <button class="side-panel-close" onclick="toggleSidePanel()">✕</button>' +
        '  </div>' +
        '  <div class="side-panel-links">' +
        '    <a href="' + prefix + 'index.html">' + texts.home + '</a>' +
        '    <a href="' + prefix + 'pages/tanakh/index.html">' + texts.tanakh + '</a>' +
        '    <a href="' + prefix + 'pages/research/index.html">' + texts.research + '</a>' +
        '    <a href="' + prefix + 'pages/research/methods.html">' + texts.methods + '</a>' +
        '    <a href="' + prefix + 'pages/research/dictionaries.html">' + texts.dictionaries + '</a>' +
        '    <a href="' + prefix + 'pages/research/methodology.html">' + texts.methodology + '</a>' +
        '    <a href="' + prefix + 'pages/tools/index.html">' + (texts.tools || 'Инструменты') + '</a>' +
        '    <a href="' + prefix + 'apps/researchlab/index.html">🔬 Лаборатория</a>' +
        '    <a href="' + prefix + 'pages/about/index.html">' + texts.about + '</a>' +
        '  </div>' +
        '  <div class="side-panel-lang-switcher">' + selectHTML + '</div>' +
        '</div>';

    document.body.insertAdjacentHTML('beforeend', burgerHTML);
});

function toggleSidePanel() {
    document.getElementById('sidePanel').classList.toggle('open');
    document.getElementById('sidePanelOverlay').classList.toggle('show');
}
