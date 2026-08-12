(function(){
    const ring = document.querySelector('.donut-ring');
if (ring) {
    const counts = {
        regular: parseInt(ring.dataset.regular) || 0,
        ninos: parseInt(ring.dataset.ninos) || 0,
        visitas: parseInt(ring.dataset.visitas) || 0,
        comprometidos: parseInt(ring.dataset.comprometidos) || 0
    };
    const total = counts.regular + counts.ninos + counts.visitas + counts.comprometidos || 1;
    let p = {
        regular: Math.round(counts.regular / total * 100),
        ninos: Math.round(counts.ninos / total * 100),
        visitas: Math.round(counts.visitas / total * 100),
        comprometidos: Math.round(counts.comprometidos / total * 100)
    };
    const sumP = p.regular + p.ninos + p.visitas + p.comprometidos;
    if (sumP !== 100) { p.comprometidos += 100 - sumP; }

    const c1 = p.comprometidos;
    const c2 = c1 + p.regular;
    const c3 = c2 + p.ninos;
    const c4 = 100;

    ring.style.background = `conic-gradient(var(--metric-comprometidos) 0% ${c1}%, var(--metric-regular) ${c1}% ${c2}%, var(--metric-ninos) ${c2}% ${c3}%, var(--metric-visitas) ${c3}% ${c4}%)`;

    const legendItems = document.querySelectorAll('.chart-legend li');
    const centerNumber = document.querySelector('.donut-number');

    legendItems.forEach(function(li) {
        const text = li.textContent.trim();
        let cnt = 0;
        if (text.includes('Regulares')) cnt = counts.regular;
        else if (text.includes('Niños')) cnt = counts.ninos;
        else if (text.includes('Visitas')) cnt = counts.visitas;
        else if (text.includes('Comprometidos')) cnt = counts.comprometidos;

        li.setAttribute('title', `${text}: ${cnt.toLocaleString()} (${Math.round(cnt / total * 100)}%)`);

        li.addEventListener('mouseenter', function() {
            centerNumber.textContent = cnt.toLocaleString();
        });
        li.addEventListener('mouseleave', function() {
            centerNumber.textContent = total.toLocaleString();
        });
    });
}

const tabButtons = document.querySelectorAll('.view-tab');
const viewPanels = document.querySelectorAll('.view-panel');

function setActiveView(viewName) {
    tabButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.view === viewName));
    viewPanels.forEach(panel => panel.classList.toggle('active', panel.classList.contains(`view-${viewName}`)));
}

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        setActiveView(button.dataset.view);
    });
});

const defaultView = 'general';
setActiveView(defaultView);
})();
