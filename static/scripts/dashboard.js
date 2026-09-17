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
                if (selectRed && option.dataset.redId) {
                    selectRed.value = option.dataset.redId;
                    filterCdpOptions(option.dataset.redId);
                }
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
    // Configuración del Donut Chart (Segmentos Interactivos SVG y Tooltips Accesibles)
    // -------------------------------------------------------------------------
    function initDonutCharts() {
        const wrappers = document.querySelectorAll('.donut-wrapper');
        wrappers.forEach(wrapper => {
            const ring = wrapper.querySelector('.donut-ring');
            if (!ring) return;

            const counts = {
                regular: Math.max(0, parseInt(ring.dataset.regular, 10) || 0),
                ninos: Math.max(0, parseInt(ring.dataset.ninos, 10) || 0),
                visitas: Math.max(0, parseInt(ring.dataset.visitas, 10) || 0),
                comprometidos: Math.max(0, parseInt(ring.dataset.comprometidos, 10) || 0)
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
            if (sumCounts > 0 && sumP !== 100) {
                const maxKey = Object.keys(counts).reduce((a, b) => counts[a] >= counts[b] ? a : b);
                if (counts[maxKey] > 0) {
                    p[maxKey] += (100 - sumP);
                }
            }

            const cardParent = wrapper.closest('.chart-card') || wrapper.closest('.dashboard-grid') || wrapper.closest('.view-panel');
            const legendItems = cardParent ? cardParent.querySelectorAll('.chart-legend li') : [];
            const centerNumber = wrapper.querySelector('.donut-number');
            const centerLabel = wrapper.querySelector('.donut-label');
            let donutTooltip = wrapper.querySelector('.donut-tooltip');
            if (!donutTooltip) {
                donutTooltip = document.createElement('div');
                donutTooltip.className = 'donut-tooltip';
                donutTooltip.setAttribute('role', 'tooltip');
                donutTooltip.setAttribute('aria-hidden', 'true');
                wrapper.appendChild(donutTooltip);
            }
            if (!donutTooltip.id) {
                donutTooltip.id = 'donut-tip-' + Math.floor(Math.random() * 100000);
            }

            const initialTotalText = centerNumber ? centerNumber.textContent.trim() : sumCounts.toLocaleString();
            const initialLabelText = centerLabel ? centerLabel.textContent.trim() : 'TOTAL';

            // Generar o actualizar SVG interactivo de segmentos dentro de donut-ring
            let existingSvg = ring.querySelector('.donut-svg') || wrapper.querySelector('.donut-svg');
            if (existingSvg) existingSvg.remove();

            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('class', 'donut-svg');
            svg.setAttribute('viewBox', '0 0 100 100');
            svg.setAttribute('width', '100%');
            svg.setAttribute('height', '100%');
            svg.setAttribute('role', 'graphics-document');
            svg.setAttribute('aria-label', 'Segmentos interactivos del gráfico circular');
            svg.setAttribute('style', 'position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; border-radius: 50% !important; z-index: 2 !important; overflow: visible !important; pointer-events: auto !important; display: block !important;');
            svg.setAttribute('style', 'position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; border-radius: 50% !important; z-index: 2 !important; overflow: visible !important; pointer-events: none !important; display: block !important;');

            wrapper.style.cssText = 'position: relative !important; width: 220px !important; height: 220px !important; min-height: 220px !important; display: flex !important; align-items: center !important; justify-content: center !important; margin: 0 auto !important; flex-shrink: 0 !important;';
            ring.style.cssText = 'position: relative !important; width: 180px !important; height: 180px !important; min-width: 180px !important; min-height: 180px !important; border-radius: 50% !important; display: flex !important; align-items: center !important; justify-content: center !important; background: transparent !important; margin: 0 auto !important; flex-shrink: 0 !important;';

            const centerBox = ring.querySelector('.donut-center') || wrapper.querySelector('.donut-center');
            if (centerBox) {
                if (centerBox.parentElement !== ring) {
                    ring.appendChild(centerBox);
                }
                centerBox.style.cssText = 'position: absolute !important; top: 50% !important; left: 50% !important; transform: translate(-50%, -50%) !important; z-index: 10 !important; pointer-events: none !important; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; text-align: center !important; width: 100px !important; height: 100px !important; margin: 0 !important; padding: 0 !important; box-sizing: border-box !important;';
            }

            const C = 2 * Math.PI * 38; // ~238.761
            const categories = [
                { key: 'comprometidos', label: 'Comprometidos', count: counts.comprometidos, pct: p.comprometidos, color: 'var(--metric-comprometidos, #2b0000)' },
                { key: 'regular', label: 'Regulares', count: counts.regular, pct: p.regular, color: 'var(--metric-regular, #7a2222)' },
                { key: 'ninos', label: 'Niños', count: counts.ninos, pct: p.ninos, color: 'var(--metric-ninos, #c86b6b)' },
                { key: 'visitas', label: 'Visitas', count: counts.visitas, pct: p.visitas, color: 'var(--metric-visitas, #e9b9b9)' }
            ];

            let accumulatedPct = 0;
            const segmentElements = {};

            const activate = (cat, isDonutHover = false) => {
                if (centerNumber) centerNumber.textContent = cat.count.toLocaleString();
                if (centerLabel) centerLabel.textContent = cat.label.toUpperCase();
                if (segmentElements[cat.key]) segmentElements[cat.key].classList.add('active');
                legendItems.forEach(li => {
                    const liKey = li.dataset.category || (li.querySelector('.dot.regular') ? 'regular' : li.querySelector('.dot.ninos') ? 'ninos' : li.querySelector('.dot.visitas') ? 'visitas' : 'comprometidos');
                    if (liKey === cat.key) {
                        li.classList.add('active');
                        const tip = li.querySelector('.legend-tooltip');
                        if (tip) tip.setAttribute('aria-hidden', isDonutHover ? 'true' : 'false');
                    }
                });
                if (donutTooltip && isDonutHover) {
                    donutTooltip.innerHTML = `
                        <span class="tooltip-title">${cat.label}</span>
                        <span class="tooltip-val"><strong>${cat.count.toLocaleString()}</strong> personas</span>
                        <span class="tooltip-pct">${cat.pct}% del total</span>
                    `;
                    donutTooltip.classList.add('visible');
                    donutTooltip.setAttribute('aria-hidden', 'false');
                } else if (donutTooltip) {
                    donutTooltip.classList.remove('visible');
                    donutTooltip.setAttribute('aria-hidden', 'true');
                }
            };

            const deactivate = () => {
                if (centerNumber) centerNumber.textContent = initialTotalText;
                if (centerLabel) centerLabel.textContent = initialLabelText;
                Object.values(segmentElements).forEach(el => el.classList.remove('active'));
                legendItems.forEach(li => {
                    li.classList.remove('active');
                    const tip = li.querySelector('.legend-tooltip');
                    if (tip) tip.setAttribute('aria-hidden', 'true');
                });
                if (donutTooltip) {
                    donutTooltip.classList.remove('visible');
                    donutTooltip.setAttribute('aria-hidden', 'true');
                }
            };

            if (sumCounts === 0) {
                // Anillo neutro para estado vacío
                const emptyCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                emptyCircle.setAttribute('cx', '50');
                emptyCircle.setAttribute('cy', '50');
                emptyCircle.setAttribute('r', '38');
                emptyCircle.setAttribute('fill', 'transparent');
                emptyCircle.setAttribute('fill', 'none');
                emptyCircle.setAttribute('stroke', 'rgba(221, 192, 189, 0.25)');
                emptyCircle.setAttribute('stroke-width', '18');
                emptyCircle.setAttribute('pointer-events', 'none');
                svg.appendChild(emptyCircle);
            } else {
                categories.forEach(cat => {
                    if (cat.count > 0 && sumCounts > 0) {
                        const exactPct = (cat.count / sumCounts) * 100;
                        const strokeLen = (exactPct / 100) * C;
                        const strokeOffset = -((accumulatedPct / 100) * C);
                        accumulatedPct += exactPct;

                        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                        circle.setAttribute('cx', '50');
                        circle.setAttribute('cy', '50');
                        circle.setAttribute('r', '38');
                        circle.setAttribute('fill', 'transparent');
                        circle.setAttribute('fill', 'none');
                        circle.setAttribute('class', `donut-segment segment-${cat.key}`);
                        circle.setAttribute('style', 'pointer-events: stroke !important;');
                        circle.setAttribute('tabindex', '0');
                        circle.setAttribute('role', 'graphics-symbol');
                        circle.setAttribute('aria-roledescription', 'segmento de gráfico circular');
                        circle.setAttribute('aria-label', `${cat.label}: ${cat.count} (${cat.pct}%)`);
                        circle.setAttribute('aria-describedby', donutTooltip.id);
                        circle.setAttribute('stroke', cat.color);
                        circle.setAttribute('stroke-dasharray', `${strokeLen} ${C - strokeLen}`);
                        circle.setAttribute('stroke-dashoffset', `${strokeOffset}`);
                        circle.setAttribute('transform', 'rotate(-90 50 50)');

                        circle.addEventListener('mouseenter', () => activate(cat, true));
                        circle.addEventListener('mouseleave', deactivate);
                        circle.addEventListener('focus', () => activate(cat, true));
                        circle.addEventListener('blur', deactivate);
                        circle.addEventListener('keydown', (e) => {
                            if (e.key === 'Escape') {
                                circle.blur();
                                deactivate();
                            }
                        });

                        svg.appendChild(circle);
                        segmentElements[cat.key] = circle;
                    }
                });
            }

            // Insertar dentro del anillo y desactivar el fondo duplicado
            ring.insertBefore(svg, ring.firstChild);
            ring.classList.add('has-svg');
            ring.style.background = 'transparent';

            // Interacción en items de la leyenda
            legendItems.forEach(li => {
                const text = li.textContent.trim();
                let catKey = li.dataset.category;
                if (!catKey) {
                    if (li.querySelector('.dot.regular') || /regular/i.test(text)) catKey = 'regular';
                    else if (li.querySelector('.dot.ninos') || /niñ|nino/i.test(text)) catKey = 'ninos';
                    else if (li.querySelector('.dot.visitas') || /visita/i.test(text)) catKey = 'visitas';
                    else if (li.querySelector('.dot.comprometidos') || /compromet/i.test(text)) catKey = 'comprometidos';
                }
                const catObj = categories.find(c => c.key === catKey);
                if (catObj) {
                    li.addEventListener('mouseenter', () => activate(catObj, false));
                    li.addEventListener('mouseleave', deactivate);
                    li.addEventListener('focus', () => activate(catObj, false));
                    li.addEventListener('blur', deactivate);
                    li.addEventListener('keydown', (e) => {
                        if (e.key === 'Escape') {
                            li.blur();
                            deactivate();
                        }
                    });
                }
            });
        });
    }

    // -------------------------------------------------------------------------
    // Configuración de Barras de Tendencia (Tooltips Accesibles e Interactivos)
    // -------------------------------------------------------------------------
    function initTrendBars() {
        const trendCols = document.querySelectorAll('.trend-bar-col');
        trendCols.forEach(col => {
            const tip = col.querySelector('.trend-tooltip');
            const showTip = () => {
                col.classList.add('tooltip-active');
                if (tip) tip.setAttribute('aria-hidden', 'false');
            };
            const hideTip = () => {
                col.classList.remove('tooltip-active');
                if (tip) tip.setAttribute('aria-hidden', 'true');
            };

            col.addEventListener('mouseenter', showTip);
            col.addEventListener('mouseleave', hideTip);
            col.addEventListener('focus', showTip);
            col.addEventListener('blur', hideTip);
            col.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    col.blur();
                    hideTip();
                }
            });
        });
    }

    // -------------------------------------------------------------------------
    // Sistema de Filtros Jerárquicos en Cascada
    // -------------------------------------------------------------------------
    function filterCdpOptions(redId) {
        if (!selectCdp) return;
        const options = Array.from(selectCdp.querySelectorAll('option'));
        let firstVisible = null;
        let isSelectedVisible = false;
        let emptyOption = selectCdp.querySelector('.no-cdp-option');

        options.forEach(opt => {
            if (opt.classList.contains('no-cdp-option')) return;
            if (!opt.value) return; // omitir placeholder o vacío
            const optRedId = opt.dataset.redId;
            const match = !redId || optRedId === String(redId);
            if (match) {
                opt.hidden = false;
                opt.disabled = false;
                if (!firstVisible) firstVisible = opt;
                if (opt.value === selectCdp.value) {
                    isSelectedVisible = true;
                }
            } else {
                opt.hidden = true;
                opt.disabled = true;
            }
        });

        if (firstVisible) {
            if (emptyOption) {
                emptyOption.hidden = true;
                emptyOption.disabled = true;
            }
            // Si la opción seleccionada no pertenece a la red elegida, cambiar al primer CDP visible
            if (!isSelectedVisible) {
                selectCdp.value = firstVisible.value;
            }
        } else {
            // No hay ninguna CDP en esta red
            if (!emptyOption) {
                emptyOption = document.createElement('option');
                emptyOption.className = 'no-cdp-option';
                emptyOption.value = '';
                emptyOption.textContent = 'Sin Casas de Paz en esta red';
                selectCdp.appendChild(emptyOption);
            }
            emptyOption.hidden = false;
            emptyOption.disabled = false;
            selectCdp.value = '';
        }
    }

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
                if (selectRed && selectRed.value) {
                    filterCdpOptions(selectRed.value);
                }
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
            selectCdp.disabled = (nivel !== 'cdp' || !selectCdp.value);
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
            if (selectCdp && (nivel !== 'cdp' || !selectCdp.value)) {
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
                if (selectRed && selectRed.value) {
                    filterCdpOptions(selectRed.value);
                }
                // Preseleccionar la primera casa visible si no hay una elegida o está deshabilitada
                if (selectCdp && (!selectCdp.value || selectCdp.selectedOptions[0]?.disabled)) {
                    for (const opt of selectCdp.options) {
                        if (!opt.disabled && opt.value) {
                            selectCdp.value = opt.value;
                            break;
                        }
                    }
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
            } else if (nivel === 'cdp' && this.value) {
                filterCdpOptions(this.value);
                submitForm();
            }
        });
    }

    if (selectCdp) {
        selectCdp.addEventListener('change', function() {
            const nivel = selectNivel ? selectNivel.value : 'general';
            if (nivel === 'cdp' && this.value) {
                // Sincronización bidireccional: al cambiar de CDP, sincronizar la red correspondiente
                const selectedOpt = this.selectedOptions[0];
                if (selectedOpt && selectedOpt.dataset.redId && selectRed) {
                    selectRed.value = selectedOpt.dataset.redId;
                }
                submitForm();
            }
        });
    }

    // Forzar actualización de visibilidad y filtros al cargar
    setTimeout(function() {
        if (selectRed && selectRed.value) {
            filterCdpOptions(selectRed.value);
        }
        updateFilterVisibility();
        initDonutCharts();
        initTrendBars();
    }, 50);

    // -------------------------------------------------------------------------
    // Descarte global con tecla ESC para tooltips (WCAG 2.1 SC 1.4.13)
    // -------------------------------------------------------------------------
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.donut-tooltip.visible').forEach(tip => {
                tip.classList.remove('visible');
                tip.setAttribute('aria-hidden', 'true');
            });
            document.querySelectorAll('.donut-segment.active').forEach(seg => {
                seg.classList.remove('active');
                seg.blur();
            });
            document.querySelectorAll('.chart-legend li.active').forEach(li => {
                li.classList.remove('active');
                const tip = li.querySelector('.legend-tooltip');
                if (tip) tip.setAttribute('aria-hidden', 'true');
                li.blur();
            });
            document.querySelectorAll('.trend-bar-col.tooltip-active').forEach(col => {
                col.classList.remove('tooltip-active');
                const tip = col.querySelector('.trend-tooltip');
                if (tip) tip.setAttribute('aria-hidden', 'true');
                col.blur();
            });
        }
    });
})();