(function(){
    const ring = document.querySelector('.donut-ring');
    if(!ring) return;
    const counts = {
        regular: parseInt(ring.dataset.regular) || 0,
        ninos: parseInt(ring.dataset.ninos) || 0,
        visitas: parseInt(ring.dataset.visitas) || 0,
        comprometidos: parseInt(ring.dataset.comprometidos) || 0
    };
    const total = counts.regular + counts.ninos + counts.visitas + counts.comprometidos || 1;
    // compute percentages and normalize to 100
    let p = {
        regular: Math.round(counts.regular / total * 100),
        ninos: Math.round(counts.ninos / total * 100),
        visitas: Math.round(counts.visitas / total * 100),
        comprometidos: Math.round(counts.comprometidos / total * 100)
    };
    const sumP = p.regular + p.ninos + p.visitas + p.comprometidos;
    if(sumP !== 100) { p.comprometidos += 100 - sumP; }

    // order: comprometidos, regular, ninos, visitas (matches CSS variable mapping)
    const c1 = p.comprometidos;
    const c2 = c1 + p.regular;
    const c3 = c2 + p.ninos;
    const c4 = 100;

    ring.style.background = `conic-gradient(var(--metric-comprometidos) 0% ${c1}%, var(--metric-regular) ${c1}% ${c2}%, var(--metric-ninos) ${c2}% ${c3}%, var(--metric-visitas) ${c3}% ${c4}%)`;

    // update center number on legend hover
    const legendItems = document.querySelectorAll('.chart-legend li');
    const centerNumber = document.querySelector('.donut-number');
    const originalCenter = centerNumber.textContent;

    legendItems.forEach(function(li){
        const text = li.textContent.trim();
        let cnt = 0;
        if(text.includes('Regulares')) cnt = counts.regular;
        else if(text.includes('Niños')) cnt = counts.ninos;
        else if(text.includes('Visitas')) cnt = counts.visitas;
        else if(text.includes('Comprometidos')) cnt = counts.comprometidos;

        // native tooltip
        li.setAttribute('title', `${text}: ${cnt.toLocaleString()} (${Math.round(cnt/total*100)}%)`);

        li.addEventListener('mouseenter', function(){
            centerNumber.textContent = cnt.toLocaleString();
            li.style.opacity = '1';
        });
        li.addEventListener('mouseleave', function(){
            centerNumber.textContent = total.toLocaleString();
        });
    });
})();