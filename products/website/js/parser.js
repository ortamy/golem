// js/parser.js — Парсинг Markdown и извлечение метаданных
(function(global) {
    'use strict';

    const EMOJI_REGEX = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}\u{2300}-\u{23FF}\u{2000}-\u{27B0}\u{FE00}-\u{FE0F}\u{1FA00}-\u{1FA6F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{1F1E0}-\u{1F1FF}\u{2702}-\u{27B0}\u{2934}-\u{2935}\u{25AA}-\u{25AB}\u{25FB}-\u{25FE}\u{2B05}-\u{2B07}\u{2B1B}-\u{2B1C}\u{2B50}\u{2764}\u{2714}\u{2716}\u{303D}\u{2122}\u{00A9}\u{00AE}\u{2194}-\u{2199}\u{21A9}-\u{21AA}\u{231A}-\u{231B}\u{2328}\u{23CF}\u{23E9}-\u{23F3}\u{23F8}-\u{23FA}\u{24C2}\u{25B6}\u{25C0}\u{3030}\u{3297}\u{3299}]+/gu;

    function escHtml(s) {
        return s.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>').replace(/"/g, '"').replace(/'/g, '&#039;');
    }

    function extractTitle(content) {
        const match = content.match(/^#\s+(.+?)$/m);
        if (match) {
            return match[1]
                .replace(/[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}\u{FE00}-\u{FEFF}\u{200D}\u{FE0F}]/gu, '')
                .replace(/^\s+/, '')
                .trim()
                .substring(0, 80);
        }
        return '';
    }

    function extractTopic(content) {
        const match = content.match(/\*\*Тема:\*\*\s*(.+?)(?:\n|$)/);
        return match ? match[1].trim().substring(0, 100) : '';
    }

    function extractRelated(content) {
        const sections = content.match(/\*\*Связанные файлы:\*\*[\s\S]*?(?=\n\n|$)/g);
        if (!sections) return [];
        const related = [];
        for (const section of sections) {
            const matches = section.matchAll(/`([^`]+)`/g);
            for (const m of matches) {
                if (!related.includes(m[1])) {
                    related.push(m[1]);
                }
            }
        }
        return related;
    }

    function parseMD(t, fileIcon) {
        t = t.replace(/\*\*Метаданные файла\*\*[\s\S]*?(?=\n---|\n# |\n## )/, '');
        
        function cleanHeading(raw) {
            return raw.replace(/!\[icon\]\([^)]*\)/g, '').replace(EMOJI_REGEX, '').trim();
        }
        
        function cleanId(raw) {
            return raw.replace(/!\[icon\]\([^)]*\)/g, '').replace(EMOJI_REGEX, '').replace(/[^a-zA-Zа-яА-ЯёЁ0-9\s-]/g, '').trim();
        }
        
        const lines = t.split('\n');
        let html = '';
        let inParagraph = false;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            if (line.trim() === '') {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                continue;
            }
            
            if (line.match(/^#### (.+)$/)) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                const h4raw = line.replace(/^#### /, '');
                html += '<h4>' + escHtml(h4raw) + '</h4>';
                continue;
            }
            if (line.match(/^### (.+)$/)) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                const h3raw = line.replace(/^### /, '');
                const h3text = cleanHeading(h3raw);
                const h3id = cleanId(h3text);
                html += '<h3 id="' + h3id + '">' + escHtml(h3raw) + '</h3>';
                continue;
            }
            if (line.match(/^## (.+)$/)) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                const h2raw = line.replace(/^## /, '');
                const h2text = cleanHeading(h2raw);
                const h2id = cleanId(h2text);
                html += '<h2 id="' + h2id + '">' + escHtml(h2raw) + '</h2>';
                continue;
            }
            if (line.match(/^# (.+)$/)) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                const h1raw = line.replace(/^# /, '');
                const iconHtml = fileIcon ? fileIcon : '';
                html += '<h1>' + iconHtml + escHtml(h1raw) + '</h1>';
                continue;
            }
            
            if (line.match(/^---$/)) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                html += '<hr class="meander">';
                continue;
            }
            
            if (line.match(/^> (.+)$/)) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                html += '<blockquote>' + escHtml(line.replace(/^> /, '')) + '</blockquote>';
                continue;
            }
            
            if (!inParagraph) {
                html += '<p>';
                inParagraph = true;
            } else {
                html += '\n';
            }
            
            const parsedLine = escHtml(line);
            const formattedLine = parsedLine.replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.+?)\*/g, '<em>$1</em>');
            
            html += formattedLine;
        }
        
        if (inParagraph) { html += '</p>'; }
        
        html = html.replace(/!\[icon\]\(([^)]+)\)/g, '<img src="$1" class="h2-icon" alt="Иконка раздела" style="width:20px;height:20px;vertical-align:middle;margin-right:8px;">');
        
        return html;
    }

    global.GolemParser = {
        extractTitle,
        extractTopic,
        extractRelated,
        parseMD
    };

})(window);