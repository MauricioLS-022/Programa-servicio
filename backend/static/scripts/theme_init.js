// Detección temprana de tema oscuro (anti-FOUC)
(function() {
    try {
        var t = localStorage.getItem('theme');
        if (t === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    } catch (e) {}
})();
