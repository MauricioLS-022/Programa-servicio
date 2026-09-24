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

            const getLegendItems = () => cardParent ? cardParent.querySelectorAll('.chart-legend li') : [];

            const activate = (cat, isDonutHover = false) => {
                if (centerNumber) centerNumber.textContent = cat.count.toLocaleString();
                if (centerLabel) centerLabel.textContent = cat.label.toUpperCase();
                if (segmentElements[cat.key]) segmentElements[cat.key].classList.add('active');
                getLegendItems().forEach(li => {
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
                getLegendItems().forEach(li => {
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

            // Interacción en items de la leyenda (clonar nodo para reemplazar listeners previos)
            const currentLegendItems = cardParent ? cardParent.querySelectorAll('.chart-legend li') : [];
            currentLegendItems.forEach(li => {
                const newLi = li.cloneNode(true);
                li.parentNode.replaceChild(newLi, li);
                const text = newLi.textContent.trim();
                let catKey = newLi.dataset.category;
                if (!catKey) {
                    if (newLi.querySelector('.dot.regular') || /regular/i.test(text)) catKey = 'regular';
                    else if (newLi.querySelector('.dot.ninos') || /niñ|nino/i.test(text)) catKey = 'ninos';
                    else if (newLi.querySelector('.dot.visitas') || /visita/i.test(text)) catKey = 'visitas';
                    else if (newLi.querySelector('.dot.comprometidos') || /compromet/i.test(text)) catKey = 'comprometidos';
                }
                const catObj = categories.find(c => c.key === catKey);
                if (catObj) {
                    newLi.addEventListener('mouseenter', () => activate(catObj, false));
                    newLi.addEventListener('mouseleave', deactivate);
                    newLi.addEventListener('focus', () => activate(catObj, false));
                    newLi.addEventListener('blur', deactivate);
                    newLi.addEventListener('keydown', (e) => {
                        if (e.key === 'Escape') {
                            newLi.blur();
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
        
        function adjustTooltip(col, tip) {
            if (!col || !tip) return;
            const chartArea = col.closest('.trend-chart-area');
            if (!chartArea || !chartArea.classList.contains('has-scroll')) {
                tip.style.transform = '';
                tip.style.removeProperty('--arrow-left');
                return;
            }
            tip.style.transform = 'translateX(-50%) translateY(0)';
            tip.style.removeProperty('--arrow-left');
            const tipRect = tip.getBoundingClientRect();
            const areaRect = chartArea.getBoundingClientRect();
            const pad = 12;
            if (tipRect.left < areaRect.left + pad) {
                const shiftX = Math.round((areaRect.left + pad) - tipRect.left);
                tip.style.transform = `translateX(calc(-50% + ${shiftX}px)) translateY(0)`;
                tip.style.setProperty('--arrow-left', `calc(50% - ${shiftX}px)`);
            } else if (tipRect.right > areaRect.right - pad) {
                const shiftX = Math.round(tipRect.right - (areaRect.right - pad));
                tip.style.transform = `translateX(calc(-50% - ${shiftX}px)) translateY(0)`;
                tip.style.setProperty('--arrow-left', `calc(50% + ${shiftX}px)`);
            }
        }

        trendCols.forEach(col => {
            const tip = col.querySelector('.trend-tooltip');
            const showTip = () => {
                col.classList.add('tooltip-active');
                if (tip) {
                    tip.setAttribute('aria-hidden', 'false');
                    adjustTooltip(col, tip);
                }
            };
            const hideTip = () => {
                col.classList.remove('tooltip-active');
                if (tip) {
                    tip.setAttribute('aria-hidden', 'true');
                    tip.style.transform = '';
                    tip.style.removeProperty('--arrow-left');
                }
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

        // Reajustar tooltip activo al hacer scroll
        document.querySelectorAll('.trend-chart-area.has-scroll').forEach(area => {
            if (area.dataset.scrollBound) return;
            area.dataset.scrollBound = 'true';
            area.addEventListener('scroll', () => {
                const activeCol = area.querySelector('.trend-bar-col.tooltip-active');
                if (activeCol) {
                    const tip = activeCol.querySelector('.trend-tooltip');
                    adjustTooltip(activeCol, tip);
                }
            }, { passive: true });
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

        // Si es la vista general y no hay búsqueda, ir a la URL base limpia (preservando período si no es semanal)
        if (nivel === 'general' && !searchVal) {
            const inputPeriodo = document.getElementById('inputPeriodo');
            const pVal = inputPeriodo ? inputPeriodo.value : 'semana';
            const baseUrl = filterForm.getAttribute('action') || '/admin/dashboard';
            window.location.href = (pVal && pVal !== 'semana') ? `${baseUrl}?periodo=${encodeURIComponent(pVal)}` : baseUrl;
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
                const inputPeriodo = document.getElementById('inputPeriodo');
                const pVal = inputPeriodo ? inputPeriodo.value : 'semana';
                const baseUrl = filterForm.getAttribute('action') || '/admin/dashboard';
                window.location.href = (pVal && pVal !== 'semana') ? `${baseUrl}?periodo=${encodeURIComponent(pVal)}` : baseUrl;
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

    // -------------------------------------------------------------------------
    // Selector Dinámico de Período (Semana / Mes / Año) con AJAX y Persistencia
    // -------------------------------------------------------------------------
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatMoney(num) {
        const n = parseFloat(num) || 0;
        return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function initPeriodToggle() {
        const periodButtons = document.querySelectorAll('.period-btn');
        if (!periodButtons.length) return;

        const inputPeriodo = document.getElementById('inputPeriodo');

        function applyPeriodData(data, periodo, nivel) {
            if (!data) return;

            // 1. Textos y etiquetas dinámicas según período
            const periodoLabels = {
                semana: {
                    cumplimientoTitle: 'Cumplimiento Semanal',
                    cumplimientoSubRed: 'Casas con reporte enviado esta semana',
                    trendTitleGen: 'Asistencia por Red esta Semana',
                    trendTitleRed: 'Asistencia por Casa esta Semana',
                    trendSubGen: 'Desglose por Red del último reporte recibido',
                    trendSubRed: `Desglose por Casa de Paz en ${data.nombre_red || ''}`,
                    distSubGen: 'Composición de membresía y consolidación de la semana activa',
                    distSubRed: `Composición de asistentes en ${data.nombre_red || ''}`,
                    rankingSub: 'Cumplimiento y asistencia de la semana'
                },
                mes: {
                    cumplimientoTitle: 'Cumplimiento Mensual',
                    cumplimientoSubRed: 'Casas con reporte en el mes en curso',
                    trendTitleGen: 'Evolución Semanal del Mes',
                    trendTitleRed: 'Evolución Semanal del Mes',
                    trendSubGen: 'Histórico semanal del mes en curso',
                    trendSubRed: `Histórico semanal del mes en curso en ${data.nombre_red || ''}`,
                    distSubGen: 'Composición acumulada de la membresía en el mes en curso',
                    distSubRed: 'Composición de miembros en el mes en curso',
                    rankingSub: 'Cumplimiento y asistencia del mes'
                },
                anio: {
                    cumplimientoTitle: 'Cumplimiento Anual',
                    cumplimientoSubRed: 'Casas con reporte en el año en curso',
                    trendTitleGen: 'Evolución Mensual del Año',
                    trendTitleRed: 'Evolución Mensual del Año',
                    trendSubGen: 'Histórico mes a mes del año en curso',
                    trendSubRed: `Histórico mes a mes del año en curso en ${data.nombre_red || ''}`,
                    distSubGen: 'Composición acumulada de la membresía en el año en curso',
                    distSubRed: 'Composición de miembros en el año en curso',
                    rankingSub: 'Cumplimiento y asistencia del año'
                }
            };

            const labels = periodoLabels[periodo] || periodoLabels.semana;

            if (nivel === 'general') {
                // Títulos Generales
                const lblCumplimiento = document.getElementById('lblCumplimientoTitleGen');
                if (lblCumplimiento) lblCumplimiento.textContent = labels.cumplimientoTitle;

                const lblTrendTitle = document.getElementById('lblTrendTitleGen');
                if (lblTrendTitle) lblTrendTitle.textContent = labels.trendTitleGen;

                const lblTrendSub = document.getElementById('lblTrendSubGen');
                if (lblTrendSub) lblTrendSub.textContent = labels.trendSubGen;

                const lblDistSub = document.getElementById('lblDistribucionSubGen');
                if (lblDistSub) lblDistSub.textContent = labels.distSubGen;

                const lblRankingSub = document.getElementById('lblRankingSubGen');
                if (lblRankingSub) lblRankingSub.textContent = labels.rankingSub;

                // KPIs Generales
                const kpiTotal = document.getElementById('kpiTotalAsistenciaGen');
                if (kpiTotal) kpiTotal.textContent = (data.total_asistencia || 0).toLocaleString();

                const kpiCumplPct = document.getElementById('kpiCumplimientoPctGen');
                if (kpiCumplPct) kpiCumplPct.textContent = `${data.cumplimiento || 0}%`;

                const kpiCumplSub = document.getElementById('kpiCumplimientoSubGen');
                if (kpiCumplSub) {
                    const rep = data.casas_con_reporte !== undefined ? data.casas_con_reporte : (data.reportes_enviados || 0);
                    const tot = data.total_casas || 0;
                    kpiCumplSub.textContent = `${rep} de ${tot} CDP`;
                }

                const kpiOfrendasUsd = document.getElementById('kpiOfrendasUsdGen');
                if (kpiOfrendasUsd) kpiOfrendasUsd.textContent = `$${formatMoney(data.ofrendas_usd)}`;

                const kpiOfrendasBs = document.getElementById('kpiOfrendasBsGen');
                if (kpiOfrendasBs) kpiOfrendasBs.textContent = `Bs. ${formatMoney(data.ofrendas_bs)}`;

                const kpiConversiones = document.getElementById('kpiConversionesGen');
                if (kpiConversiones) kpiConversiones.textContent = (data.conversiones || 0).toLocaleString();

                const frutoConv = document.getElementById('frutoConversionesGen');
                if (frutoConv) frutoConv.textContent = (data.conversiones || 0).toLocaleString();

                const frutoRecon = document.getElementById('frutoReconciliacionesGen');
                if (frutoRecon) frutoRecon.textContent = (data.reconciliaciones || 0).toLocaleString();

                // Tendencia de Asistencia General
                renderTrendBars('Gen', data.tendencia_semanas, data.promedio_tendencia);

                // Distribución Donut General
                renderDonut('Gen', data.distribucion, data.total_asistencia);

                // Ranking de Redes
                renderRanking(data.ranking_redes);

            } else if (nivel === 'red') {
                // Títulos de Red
                const lblCumplimiento = document.getElementById('lblCumplimientoTitleRed');
                if (lblCumplimiento) lblCumplimiento.textContent = labels.cumplimientoTitle;

                const lblCumplSub = document.getElementById('lblCumplimientoSubRed');
                if (lblCumplSub) lblCumplSub.textContent = labels.cumplimientoSubRed;

                const lblTrendTitle = document.getElementById('lblTrendTitleRed');
                if (lblTrendTitle) lblTrendTitle.textContent = labels.trendTitleRed;

                const lblTrendSub = document.getElementById('lblTrendSubRed');
                if (lblTrendSub) lblTrendSub.textContent = labels.trendSubRed;

                const lblDistSub = document.getElementById('lblDistribucionSubRed');
                if (lblDistSub) lblDistSub.textContent = labels.distSubRed;

                // KPIs de Red
                const kpiTotal = document.getElementById('kpiTotalAsistenciaRed');
                if (kpiTotal) kpiTotal.textContent = (data.asistencia_total || 0).toLocaleString();

                const kpiProm = document.getElementById('kpiPromedioCasaRed');
                if (kpiProm) kpiProm.textContent = (data.promedio_casa || 0).toLocaleString();

                const kpiConversiones = document.getElementById('kpiConversionesRed');
                if (kpiConversiones) kpiConversiones.textContent = (data.conversiones || 0).toLocaleString();

                const kpiOfrendasUsd = document.getElementById('kpiOfrendasUsdRed');
                if (kpiOfrendasUsd) kpiOfrendasUsd.textContent = `$${formatMoney(data.ofrendas_usd)}`;

                const kpiOfrendasBs = document.getElementById('kpiOfrendasBsRed');
                if (kpiOfrendasBs) kpiOfrendasBs.textContent = `Bs. ${formatMoney(data.ofrendas_bs)}`;

                // Tarjeta de Cumplimiento de Red
                const pctRed = document.getElementById('cumplimientoPctRed');
                if (pctRed) pctRed.textContent = `${data.cumplimiento || 0}%`;

                const fracRed = document.getElementById('cumplimientoFractionRed');
                if (fracRed) fracRed.textContent = `${data.casas_con_reporte || 0} de ${data.casas_activas || 0} casas`;

                const barRed = document.getElementById('cumplimientoBarRed');
                if (barRed) barRed.style.setProperty('--bar-width', `${data.cumplimiento || 0}%`);

                const pillAlDia = document.getElementById('pillAlDiaNumRed');
                if (pillAlDia) pillAlDia.textContent = (data.casas_con_reporte || 0);

                const pillPend = document.getElementById('pillPendientesNumRed');
                if (pillPend) pillPend.textContent = (data.casas_pendientes || 0);

                // Tendencia de Asistencia de Red
                renderTrendBars('Red', data.tendencia_semanas, data.promedio_tendencia);

                // Distribución Donut de Red
                renderDonut('Red', data.distribucion, data.asistencia_total);
            }
        }

        function renderTrendBars(suffix, tendencia, promedio) {
            const container = document.getElementById(`trendBars${suffix}`);
            const badgeContainer = document.getElementById(`trendBadge${suffix}`);
            if (!container) return;

            // Alternar scroll horizontal si hay más de 7 elementos (hasta 7 entran completos)
            const chartArea = container.closest('.trend-chart-area');
            if (tendencia && tendencia.length > 7) {
                container.classList.add('has-scroll');
                if (chartArea) chartArea.classList.add('has-scroll');
            } else {
                container.classList.remove('has-scroll');
                if (chartArea) chartArea.classList.remove('has-scroll');
            }

            // Variación respecto a la medición anterior o promedio
            if (badgeContainer) {
                if (tendencia && tendencia.length > 1 && (tendencia[tendencia.length - 2]?.asistencia || 0) > 0) {
                    const prev = tendencia[tendencia.length - 2].asistencia;
                    const curr = tendencia[tendencia.length - 1].asistencia;
                    const variacion = Math.round(((curr - prev) / prev * 100) * 10) / 10;
                    const sign = variacion >= 0 ? '+' : '';
                    const icon = variacion >= 0 ? 'trending_up' : 'trending_down';
                    const negClass = variacion < 0 ? 'negative' : '';
                    badgeContainer.innerHTML = `
                        <div class="trend-badge-pill ${negClass}" role="status" aria-label="Variación: ${sign}${variacion.toFixed(1)}% respecto a la medición anterior">
                            <span class="material-symbols-outlined">${icon}</span>
                            <span>${sign}${variacion.toFixed(1)}% vs anterior</span>
                        </div>
                    `;
                } else if (tendencia && tendencia.length > 1 && promedio > 0) {
                    const curr = tendencia[tendencia.length - 1].asistencia;
                    const variacion = Math.round(((curr - promedio) / promedio * 100) * 10) / 10;
                    const sign = variacion >= 0 ? '+' : '';
                    const icon = variacion >= 0 ? 'trending_up' : 'trending_down';
                    const negClass = variacion < 0 ? 'negative' : '';
                    badgeContainer.innerHTML = `
                        <div class="trend-badge-pill ${negClass}" role="status" aria-label="Variación: ${sign}${variacion.toFixed(1)}% respecto al promedio">
                            <span class="material-symbols-outlined">${icon}</span>
                            <span>${sign}${variacion.toFixed(1)}% vs promedio</span>
                        </div>
                    `;
                } else if (tendencia && tendencia.length > 1) {
                    badgeContainer.innerHTML = `
                        <div class="trend-badge-pill" role="status" aria-label="Variación: 0.0%">
                            <span class="material-symbols-outlined">trending_flat</span>
                            <span>0.0% vs anterior</span>
                        </div>
                    `;
                } else {
                    badgeContainer.innerHTML = '';
                }
            }

            // Renderizado de las columnas de barras
            if (tendencia && tendencia.length > 0) {
                let html = '';
                tendencia.forEach((item, index) => {
                    const tipId = `trend-tip-${suffix.toLowerCase()}-${index + 1}`;
                    html += `
                        <div class="trend-bar-col" tabindex="0" role="graphics-symbol" aria-roledescription="barra de asistencia" aria-describedby="${tipId}" aria-label="${escapeHtml(item.semana)}: ${item.asistencia || 0} asistentes, ${item.porcentaje || 0}% del pico">
                            <div class="trend-bar-track">
                                <div class="trend-bar-fill" style="--bar-height: ${item.porcentaje || 0}%;">
                                    <span class="trend-bar-val">${item.asistencia || 0}</span>
                                </div>
                            </div>
                            <span class="trend-bar-lbl">${escapeHtml(item.semana)}${item.rango_fecha ? `<span class="trend-bar-sublbl">${escapeHtml(item.rango_fecha)}</span>` : ''}</span>
                            <div class="trend-tooltip" id="${tipId}" role="tooltip" aria-hidden="true">
                                <span class="tooltip-date">${escapeHtml(item.fecha_completa || item.semana)}</span>
                                <span class="tooltip-val"><strong>${item.asistencia || 0}</strong> asistentes</span>
                                <span class="tooltip-pct">${item.porcentaje || 0}% del pico</span>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
                initTrendBars();
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <span class="material-symbols-outlined empty-icon">monitoring</span>
                        <p class="empty-message">Aún no hay reportes para mostrar una tendencia.</p>
                    </div>
                `;
            }
        }

        function renderDonut(suffix, dist, totalAsist) {
            const ring = document.getElementById(`donutRing${suffix}`);
            const centerNum = document.getElementById(`donutNumber${suffix}`);
            if (!ring) return;

            const d_reg = (dist && dist.regulares) || 0;
            const d_nin = (dist && dist.ninos) || 0;
            const d_vis = (dist && dist.visitas) || 0;
            const d_com = (dist && dist.comprometidos) || 0;
            const sum = d_reg + d_nin + d_vis + d_com;
            const base = sum > 0 ? sum : 1;

            // Actualizar atributos de datos en el anillo
            ring.dataset.regular = d_reg;
            ring.dataset.ninos = d_nin;
            ring.dataset.visitas = d_vis;
            ring.dataset.comprometidos = d_com;

            if (centerNum) {
                centerNum.textContent = (totalAsist !== undefined ? totalAsist : sum).toLocaleString();
            }

            // Actualizar elementos de la leyenda
            const updateLegendItem = (cat, val, label) => {
                const item = document.getElementById(`legendItem${cat}${suffix}`);
                const valSpan = document.getElementById(`legendVal${cat}${suffix}`);
                if (item) {
                    const pct = Math.round(val / base * 100);
                    item.dataset.count = val;
                    item.dataset.percent = pct;
                    item.setAttribute('aria-label', `${label}: ${val} personas (${pct}%)`);
                    const tipVal = item.querySelector('.legend-tooltip .tooltip-val strong');
                    if (tipVal) tipVal.textContent = val.toLocaleString();
                    const tipPct = item.querySelector('.legend-tooltip .tooltip-pct');
                    if (tipPct) tipPct.textContent = `${pct}% del período`;
                }
                if (valSpan) {
                    valSpan.textContent = val;
                }
            };

            updateLegendItem('Reg', d_reg, 'Regulares');
            updateLegendItem('Nin', d_nin, 'Niños');
            updateLegendItem('Vis', d_vis, 'Visitas');
            updateLegendItem('Com', d_com, 'Comprometidos');

            // Reconstruir los segmentos SVG interactivos
            initDonutCharts();
        }

        function renderRanking(ranking) {
            const container = document.getElementById('rankingListGen');
            if (!container) return;

            if (ranking && ranking.length > 0) {
                let html = '';
                ranking.slice(0, 3).forEach((red, idx) => {
                    const pos = idx + 1;
                    const cumpl = parseInt(red.cumplimiento, 10) || 0;
                    const asist = parseInt(red.asistencia, 10) || 0;
                    const asistTot = parseInt(red.asistencia_total, 10) || 0;
                    const totCasas = parseInt(red.total_casas, 10) || 0;
                    const repCasas = parseInt(red.casas_reportadas, 10) || 0;
                    const colorClass = red.color_class || (pos === 1 ? 'gold' : pos === 2 ? 'silver' : 'bronze');

                    const asistTitle = asistTot > 0 ? `${asistTot} asistencias acumuladas` : 'Asistencia del período actual';
                    const cumplTitle = totCasas > 0 ? `${repCasas} de ${totCasas} Casas de Paz han reportado en este período (${cumpl}%)` : `${cumpl}% de Casas de Paz con reporte en este período`;

                    html += `
                        <div class="ranking-item podium-${pos}">
                            <div class="ranking-row">
                                <div class="ranking-name-box">
                                    <span class="ranking-pos pos-${pos}" title="Puesto #${pos} del podio ministerial">#${pos}</span>
                                    <strong>${escapeHtml(red.nombre)}</strong>
                                    <span class="ranking-sup">(${escapeHtml(red.supervisor)})</span>
                                </div>
                                <div class="ranking-stats">
                                    <span class="ranking-asist" title="${asistTitle}">${asist} asists.</span>
                                    <span class="ranking-percent" title="${cumplTitle}">${cumpl}% cumpl.</span>
                                </div>
                            </div>
                            <div class="progress-bar" title="${cumplTitle}">
                                <div class="progress-fill fill-${colorClass}" style="--bar-width: ${cumpl}%;"></div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <span class="material-symbols-outlined empty-icon">leaderboard</span>
                        <p class="empty-message">Aún no hay redes con reportes para comparar.</p>
                    </div>
                `;
            }
        }

        const periodDataCache = {};

        function syncPeriodUrl(periodo, options = {}) {
            if (!window.history || !window.history.replaceState) return;
            const { pushHistory = true } = options;
            const url = new URL(window.location);

            if (periodo && periodo !== 'semana') {
                url.searchParams.set('periodo', periodo);
            } else {
                url.searchParams.delete('periodo');
            }

            const queryString = url.searchParams.toString();
            const cleanUrl = queryString ? `${url.pathname}?${queryString}` : url.pathname;

            if (window.location.pathname + window.location.search === cleanUrl) return;

            if (pushHistory && window.history.pushState) {
                window.history.pushState({ periodo: periodo }, '', cleanUrl);
            } else {
                window.history.replaceState({ periodo: periodo }, '', cleanUrl);
            }
        }

        function switchPeriod(periodo, btnElement, options = {}) {
            if (!periodo) return;
            const { updateUrl = true, pushHistory = true } = options;

            // Actualizar botones visualmente
            periodButtons.forEach(btn => {
                const matches = btn.dataset.periodo === periodo;
                btn.classList.toggle('active', matches);
                btn.setAttribute('aria-pressed', matches ? 'true' : 'false');
            });

            // Actualizar input oculto del formulario
            if (inputPeriodo) {
                inputPeriodo.value = periodo;
            }

            // Persistir preferencia en localStorage
            try {
                localStorage.setItem('dashboard_periodo', periodo);
            } catch (e) {
                // Manejar almacenamiento bloqueado
            }

            // Sincronizar URL del navegador
            if (updateUrl) {
                syncPeriodUrl(periodo, { pushHistory });
            }

            const nivel = selectNivel ? selectNivel.value : 'general';
            const redId = selectRed && nivel !== 'general' ? selectRed.value : '';
            const cdpId = selectCdp && nivel === 'cdp' ? selectCdp.value : '';

            const cacheKey = `${nivel}_${redId}_${cdpId}_${periodo}`;
            if (periodDataCache[cacheKey]) {
                applyPeriodData(periodDataCache[cacheKey], periodo, nivel);
                return;
            }

            // Efecto visual de carga
            const loadingCards = document.querySelectorAll('.summary-grid, .chart-card, .participation-card');
            loadingCards.forEach(c => c.classList.add('metric-loading'));

            const params = new URLSearchParams({
                nivel: nivel,
                periodo: periodo
            });
            if (redId) params.append('red_id', redId);
            if (cdpId) params.append('cdp_id', cdpId);

            fetch(`/api/dashboard/datos?${params.toString()}`)
                .then(res => {
                    if (!res.ok) throw new Error('Error al cargar datos del período');
                    return res.json();
                })
                .then(data => {
                    periodDataCache[cacheKey] = data;
                    applyPeriodData(data, periodo, nivel);
                })
                .catch(err => {
                    console.error('[Dashboard] Error cambiando de período:', err);
                })
                .finally(() => {
                    loadingCards.forEach(c => {
                        c.classList.remove('metric-loading');
                        c.classList.remove('metric-fade-in');
                        void c.offsetWidth; // Forzar reflow para reiniciar animación CSS
                        c.classList.add('metric-fade-in');
                    });
                });
        }

        // Registrar event listeners para cada botón de período
        periodButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                if (this.classList.contains('active')) return;
                const periodo = this.dataset.periodo;
                switchPeriod(periodo, this, { updateUrl: true, pushHistory: true });
            });
        });

        // Soporte para navegación con historial del navegador (Atrás / Adelante)
        window.addEventListener('popstate', function(e) {
            const currentParams = new URLSearchParams(window.location.search);
            const targetPeriodo = currentParams.get('periodo') || 'semana';
            const targetBtn = document.querySelector(`.period-btn[data-periodo="${targetPeriodo}"]`);
            if (targetBtn && !targetBtn.classList.contains('active')) {
                switchPeriod(targetPeriodo, targetBtn, { updateUrl: false });
            }
        });

        // Sincronización inicial con localStorage si la URL no especifica período
        const urlParams = new URLSearchParams(window.location.search);
        const urlPeriodo = urlParams.get('periodo');
        if (urlPeriodo && ['semana', 'mes', 'anio'].includes(urlPeriodo)) {
            try {
                localStorage.setItem('dashboard_periodo', urlPeriodo);
            } catch (e) {}
        } else {
            try {
                const savedPeriodo = localStorage.getItem('dashboard_periodo');
                if (savedPeriodo && ['mes', 'anio'].includes(savedPeriodo)) {
                    const targetBtn = document.querySelector(`.period-btn[data-periodo="${savedPeriodo}"]`);
                    if (targetBtn) {
                        switchPeriod(savedPeriodo, targetBtn, { updateUrl: true, pushHistory: false });
                    }
                }
            } catch (e) {}
        }
    }

    // Forzar actualización de visibilidad y filtros al cargar
    setTimeout(function() {
        if (selectRed && selectRed.value) {
            filterCdpOptions(selectRed.value);
        }
        updateFilterVisibility();
        initDonutCharts();
        initTrendBars();
        initPeriodToggle();
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