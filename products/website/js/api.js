// js/api.js — API запросы к серверу
(function(global) {
    'use strict';

    const IS_LOCAL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    const API_URL = IS_LOCAL ? '/api/files' : 'files.json';

    function fetchJSON(url, cb) {
        fetch(url)
            .then(function(r) { return r.json(); })
            .then(cb)
            .catch(function(e) { 
                console.error('Ошибка загрузки JSON:', e); 
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
        const url = IS_LOCAL ? '/api/file?path=' + encodeURIComponent(path) : path;
        fetchText(url, function(md) {
            callback(md);
        }, function() {
            if (errorCallback) errorCallback();
        });
    }

    function scanFiles(callback, errorCallback) {
        fetchJSON(API_URL, function(data) {
            callback(data);
        }, function(e) {
            if (errorCallback) errorCallback(e);
        });
    }

    global.GolemAPI = {
        fetchJSON,
        fetchText,
        loadFile,
        scanFiles
    };

})(window);