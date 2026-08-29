// ==========================================================================
// Dashboard Multinivel - Filtros Jerárquicos en Cascada y Visualizaciones
// ==========================================================================

(function(){
    // -------------------------------------------------------------------------
    // Sistema de Búsqueda Global (por Red, Código CDP o Líder)
    // -------------------------------------------------------------------------
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearch');
    const selectNivel = document.getElementById('selectNivel');
    const selectRed = document.getElementById('selectRed');
    const selectCdp = document.getElementById('selectCdp');
    const groupRed = document.getElementById('groupRed');
    const groupCdp = document.getElementById('groupCdp');
    const filterForm = document.getElementById('filterForm');

    function performSearch(query) {
        query = query.toLowerCase().trim();
        if (!query) return;

        // Buscar en opciones de Red
        const redOptions = selectRed ? selectRed.querySelectorAll('option[data-search]') : [];
        for (const option of redOptions) {
            const searchData = option.dataset.search || '';
            if (searchData.includes(query)) {
                if (selectNivel) selectNivel.value = 'red';
                updateFilterVisibility();
                if (selectRed) selectRed.value = option.value;
                setTimeout(() => submitForm(), 100);
                return;
            }
        }

        // Buscar en opciones de CDP
        const cdpOptions = selectCdp ? selectCdp.querySelectorAll('option[data-search]') : [];
        for (const option of cdpOptions) {
            const searchData = option.dataset.search || '';
            if (searchData.includes(query)) {
                if (selectNivel) selectNivel.value = 'cdp';
                updateFilterVisibility();
                if (selectCdp) selectCdp.value = option.value;
                setTimeout(() => submitForm(), 100);
                return;
            }
        }
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch(this.value);
            }
        });

        searchInput.addEventListener('input', function() {
            clearTimeout(searchInput.debounceTimer);
            searchInput.debounceTimer = setTimeout(() => {
                if (this.value.length >= 3) {
                    performSearch(this.value);
                }
            }, 400);
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', function() {
            if (searchInput) {
                searchInput.value = '';
                if (filterForm) {
                    window.location.href = filterForm.getAttribute('action');
                }
            }
        });
    }

    // -------------------------------------------------------------------------
    // Configuración del Donut Chart
    // -------------------------------------------------------------------------
    function initDonutCharts() {
        const rings = document.querySelectorAll('.donut-ring');
        rings.forEach(ring => {
            const counts = {
                regular: parseInt(ring.dataset.regular, 10) || 0,
                ninos: parseInt(ring.dataset.ninos, 10) || 0,
                visitas: parseInt(ring.dataset.visitas, 10) || 0,
                comprometidos: parseInt(ring.dataset.comprometidos, 10) || 0
            };
            const sumCounts = counts.regular + counts.ninos + counts.visitas + counts.comprometidos;
            const percentageBase = sumCounts || 1;
            let p = {
                regular: Math.round(counts.regular / percentageBase * 100),
                ninos: Math.round(counts.ninos / percentageBase * 100),
                visitas: Math.round(counts.visitas / percentageBase * 100),
                comprometidos: Math.round(counts.comprometidos / percentageBase * 100)
            };
            const sumP = p.regular + p.ninos + p.visitas + p.comprometidos;
            if (sumP !== 100 && counts.comprometidos > 0) {
                p.comprometidos += 100 - sumP;
            } else if (sumP !== 100) {
                p.regular += 100 - sumP;
            }

            const c1 = p.comprometidos;
            const c2 = c1 + p.regular;
            const c3 = c2 + p.ninos;
            const c4 = 100;

            ring.style.background = `conic-gradient(var(--metric-comprometidos) 0% ${c1}%, var(--metric-regular) ${c1}% ${c2}%, var(--metric-ninos) ${c2}% ${c3}%, var(--metric-visitas) ${c3}% ${c4}%)`;

            const cardParent = ring.closest('.chart-card') || ring.closest('.dashboard-grid') || ring.closest('.view-panel');
            if (cardParent) {
                const legendList = cardParent.querySelector('.chart-legend');
                const legendItems = cardParent.querySelectorAll('.chart-legend li');
                const centerNumber = cardParent.querySelector('.donut-number');
                const centerLabel = cardParent.querySelector('.donut-label');

                // Guardar valor y etiqueta iniciales del centro de la dona
                const initialTotalText = centerNumber ? centerNumber.textContent.trim() : sumCounts.toLocaleString();
                const initialLabelText = centerLabel ? centerLabel.textContent.trim() : 'TOTAL';

                const resetCenter = () => {
                    if (centerNumber) centerNumber.textContent = initialTotalText;
                    if (centerLabel) centerLabel.textContent = initialLabelText;
                };

                legendItems.forEach(function(li) {
                    const text = li.textContent.trim();
                    let cnt = 0;
                    let catLabel = 'TOTAL';

                    if (li.querySelector('.dot.regular') || /regular/i.test(text)) {
                        cnt = counts.regular;
                        catLabel = 'REGULARES';
                    } else if (li.querySelector('.dot.ninos') || /niñ|nino/i.test(text)) {
                        cnt = counts.ninos;
                        catLabel = 'NIÑOS';
                    } else if (li.querySelector('.dot.visitas') || /visita/i.test(text)) {
                        cnt = counts.visitas;
                        catLabel = 'VISITAS';
                    } else if (li.querySelector('.dot.comprometidos') || /compromet/i.test(text)) {
                        cnt = counts.comprometidos;
                        catLabel = 'COMPROMETIDOS';
                    }

                    li.setAttribute('title', `${text}: ${cnt.toLocaleString()} (${Math.round(cnt / percentageBase * 100)}%)`);

                    li.onmouseenter = function() {
                        if (centerNumber) centerNumber.textContent = cnt.toLocaleString();
                        if (centerLabel) centerLabel.textContent = catLabel;
                    };

                    li.onmouseleave = function() {
                        resetCenter();
                    };
                });

                if (legendList) {
                    legendList.onmouseleave = resetCenter;
                }
                const chartArea = cardParent.querySelector('.chart-area');
                if (chartArea) {
                    chartArea.onmouseleave = resetCenter;
                }
            }
        });
    }

    // -------------------------------------------------------------------------
    // Sistema de Filtros Jerárquicos en Cascada
    // -------------------------------------------------------------------------
    function updateFilterVisibility() {
        if (!selectNivel) return;
        
        const nivel = selectNivel.value;
        
        if (groupRed && groupRed.classList.contains('filter-group')) {
            if (nivel === 'general') {
                groupRed.classList.add('hidden');
            } else {
                groupRed.classList.remove('hidden');
            }
        }
        
        if (groupCdp) {
            if (nivel === 'cdp') {
                groupCdp.classList.remove('hidden');
            } else {
                groupCdp.classList.add('hidden');
            }
        }
    }

    function submitForm() {
        if (!filterForm) return;
        updateFilterVisibility();

        const nivel = selectNivel ? selectNivel.value : 'general';
        const searchVal = searchInput ? searchInput.value.trim() : '';

        // Si es la vista general y no hay búsqueda, ir a la URL base limpia
        if (nivel === 'general' && !searchVal) {
            window.location.href = filterForm.getAttribute('action') || '/admin/dashboard';
            return;
        }

        // Desactivar campos no aplicables para evitar contaminar la URL
        if (selectRed && selectRed.tagName === 'SELECT') {
            selectRed.disabled = (nivel === 'general');
        }
        if (selectCdp) {
            selectCdp.disabled = (nivel !== 'cdp');
        }
        if (searchInput && !searchVal) {
            searchInput.disabled = true;
        }

        setTimeout(function() {
            filterForm.submit();
        }, 20);
    }

    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            const nivel = selectNivel ? selectNivel.value : 'general';
            const searchVal = searchInput ? searchInput.value.trim() : '';

            if (nivel === 'general' && !searchVal) {
                e.preventDefault();
                window.location.href = filterForm.getAttribute('action') || '/admin/dashboard';
                return;
            }

            if (selectRed && nivel === 'general') {
                selectRed.disabled = true;
            }
            if (selectCdp && nivel !== 'cdp') {
                selectCdp.disabled = true;
            }
            if (searchInput && !searchVal) {
                searchInput.disabled = true;
            }
        });
    }

    // Event Listeners para los selectores
    if (selectNivel) {
        selectNivel.addEventListener('change', function() {
            updateFilterVisibility();
            if (this.value === 'red') {
                // Preseleccionar la primera red activa si no hay una elegida
                if (selectRed && !selectRed.value && selectRed.options.length > 0) {
                    selectRed.selectedIndex = 0;
                }
                submitForm();
            } else if (this.value === 'cdp') {
                // Preseleccionar la primera casa si no hay una elegida
                if (selectCdp && !selectCdp.value && selectCdp.options.length > 0) {
                    selectCdp.selectedIndex = 0;
                }
                submitForm();
            } else {
                submitForm();
            }
        });
    }

    if (selectRed) {
        selectRed.addEventListener('change', function() {
            const nivel = selectNivel ? selectNivel.value : 'general';
            if (nivel === 'red' && this.value) {
                submitForm();
            }
        });
    }

    if (selectCdp) {
        selectCdp.addEventListener('change', function() {
            const nivel = selectNivel ? selectNivel.value : 'general';
            if (nivel === 'cdp' && this.value) {
                submitForm();
            }
        });
    }

    // Forzar actualización de visibilidad al cargar
    setTimeout(function() {
        updateFilterVisibility();
        initDonutCharts();
    }, 50);

    // -------------------------------------------------------------------------
    // Toggle de botones (gráfico y vistas)
    // -------------------------------------------------------------------------
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            toggleButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
})();