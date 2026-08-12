// ==========================================================================
// Dashboard Multinivel - Filtros Jerárquicos en Cascada
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
                // Encontró coincidencia en red
                selectNivel.value = 'red';
                updateFilterVisibility();
                selectRed.value = option.value;
                setTimeout(() => submitForm(), 100);
                return;
            }
        }

        // Buscar en opciones de CDP
        const cdpOptions = selectCdp ? selectCdp.querySelectorAll('option[data-search]') : [];
        for (const option of cdpOptions) {
            const searchData = option.dataset.search || '';
            if (searchData.includes(query)) {
                // Encontró coincidencia en CDP
                selectNivel.value = 'cdp';
                updateFilterVisibility();
                selectCdp.value = option.value;
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
            // Búsqueda automática con debounce
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
                window.location.href = filterForm.getAttribute('action');
            }
        });
    }

    // -------------------------------------------------------------------------
    // Configuración del Donut Chart (gráfico existente)
    // -------------------------------------------------------------------------
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

    // -------------------------------------------------------------------------
    // Sistema de Filtros Jerárquicos en Cascada
    // -------------------------------------------------------------------------

    function updateFilterVisibility() {
        if (!selectNivel || !groupRed || !groupCdp) return;
        
        const nivel = selectNivel.value;
        
        if (nivel === 'general') {
            // Ocultar selectores de red y CDP
            groupRed.classList.add('hidden');
            groupCdp.classList.add('hidden');
            // Limpiar valores
            if (selectRed) selectRed.value = '';
            if (selectCdp) selectCdp.value = '';
        } else if (nivel === 'red') {
            // Mostrar selector de red, ocultar CDP
            groupRed.classList.remove('hidden');
            groupCdp.classList.add('hidden');
            // Limpiar CDP
            if (selectCdp) selectCdp.value = '';
        } else if (nivel === 'cdp') {
            // Mostrar ambos selectores
            groupRed.classList.remove('hidden');
            groupCdp.classList.remove('hidden');
        }
    }

    function submitForm() {
        if (filterForm) {
            // Primero actualizar visibilidad antes de enviar
            updateFilterVisibility();
            // Pequeño delay para que el usuario vea el cambio
            setTimeout(function() {
                filterForm.submit();
            }, 50);
        }
    }

    // Event Listeners para los selectores
    if (selectNivel) {
        selectNivel.addEventListener('change', function() {
            updateFilterVisibility();
            // Solo enviar si no es CDP (en CDP debe seleccionar primero red)
            if (this.value !== 'cdp') {
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

    // Forzar actualización de visibilidad al cargar la página
    // Usar setTimeout para asegurar que el DOM esté listo
    setTimeout(function() {
        updateFilterVisibility();
    }, 100);

    // -------------------------------------------------------------------------
    // Toggle de botones (gráfico)
    // -------------------------------------------------------------------------
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            toggleButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
})();
