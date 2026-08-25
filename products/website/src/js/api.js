// js/api.js — API запросы к серверу
(function(global) {
    'use strict';

    const IS_LOCAL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    const STATIC_FILES_URL = '../files.json';
    const API_URL = IS_LOCAL ? '/api/files' : STATIC_FILES_URL;

    function fetchJSON(url, cb, errorCallback) {
        fetch(url)
            .then(function(r) {
                if (!r.ok) throw new Error('HTTP ' + r.status + ' при загрузке ' + url);
                return r.json();
            })
            .then(cb)
            .catch(function(e) { 
                console.error('Ошибка загрузки JSON:', e); 
                if (errorCallback) errorCallback(e);
            });
    }

    function fetchText(url, cb) {
        fetch(url)
            .then(function(r) { 
                if (!r.ok) throw new Error('HTTP ' + r.status); 
                return r.text(); 
            })
            .then(cb)
            .catch(function(e) { 
                console.error('Ошибка загрузки текста:', e); 
            });
    }

    function loadFile(path, callback, errorCallback) {
        const apiUrl = '/api/file?path=' + encodeURIComponent(path);
        const staticUrl = '../' + path;
        const requestUrl = IS_LOCAL ? apiUrl : staticUrl;

        fetch(requestUrl)
            .then(function(response) {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.text();
            })
            .then(callback)
            .catch(function(error) {
                // Live Server has no /api/file endpoint; use the static file tree.
                if (IS_LOCAL && requestUrl === apiUrl) {
                    fetchText(staticUrl, callback, errorCallback);
                } else if (errorCallback) {
                    errorCallback(error);
                }
            });
    }

    function scanFiles(callback, errorCallback) {
        fetchJSON(API_URL, callback, function(error) {
            // Fall back to files.json when the page is opened through VS Code
            // Live Server (127.0.0.1:5500), which does not expose /api/files.
            if (IS_LOCAL && API_URL !== STATIC_FILES_URL) {
                fetchJSON(STATIC_FILES_URL, callback, errorCallback);
            } else if (errorCallback) {
                errorCallback(error);
            }
        });
    }

    global.GolemAPI = {
        fetchJSON,
        fetchText,
        loadFile,
        scanFiles
    };

})(window);
