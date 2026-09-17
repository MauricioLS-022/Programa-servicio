// Filtros, menús y desplazamiento de la vista de estructura.
(function() {
    const filterButtons = document.querySelectorAll('[data-red-filter]');
    const casaCards = document.querySelectorAll('.casa-card[data-red]');
    const filterLabel = document.getElementById('casasFilterLabel');
    const addCasaCard = document.querySelector('[data-filtered-add-card]');
    const searchInput = document.getElementById('casasSearchInput');
    const bannerReportes = document.getElementById('bannerReportesPendientes');
    const btnFiltrarPendientes = document.getElementById('btnFiltrarPendientes');
    const btnVerTodasCasas = document.getElementById('btnVerTodasCasas');

    let currentRedFilter = 'all';
    let currentSearchTerm = '';
    let currentReporteFilter = 'all'; // 'all' | 'pendientes'

    function isCardPendiente(card) {
        const pAttr = card.getAttribute('data-pendiente') || card.getAttribute('data-pendiente-7d') || card.dataset.pendiente;
        const actAttr = card.getAttribute('data-activa') || card.getAttribute('data-is-active') || card.dataset.activa;
        const repReciente = card.getAttribute('data-reporte-reciente');

        // Si tiene atributo de pendiente explícito
        if (pAttr !== null && pAttr !== undefined) {
            const isPend = pAttr === '1' || pAttr === 'true';
            const isAct = actAttr === null || actAttr === '1' || actAttr === 'true';
            return isPend && isAct;
        }

        // Si tiene data-reporte-reciente
        if (repReciente !== null && repReciente !== undefined) {
            const noReporto = repReciente === '0' || repReciente === 'false';
            const isAct = actAttr === null || actAttr === '1' || actAttr === 'true';
            return noReporto && isAct;
        }

        // Fallback: verificar por clase de estado visual
        return Boolean(card.querySelector('.status-pendiente'));
    }

    function getPendingCounts() {
        let totalAll = 0;
        const redCounts = {};

        casaCards.forEach(card => {
            if (isCardPendiente(card)) {
                totalAll++;
                const r = card.dataset.red;
                if (r) {
                    redCounts[r] = (redCounts[r] || 0) + 1;
                }
            }
        });

        return { totalAll, redCounts };
    }

    function updateSidebarPendingBadges() {
        const { totalAll, redCounts } = getPendingCounts();

        // Badge en "Todas las redes"
        const allBtn = document.querySelector('[data-red-filter="all"]');
        if (allBtn) {
            let badge = allBtn.querySelector('.red-pending-badge');
            if (totalAll > 0) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'red-pending-badge';
                    allBtn.querySelector('.red-header')?.appendChild(badge);
                }
                badge.textContent = `${totalAll} pend.`;
                badge.title = `${totalAll} Casas de Paz activas sin reporte en los últimos 7 días`;
            } else if (badge) {
                badge.remove();
            }
        }

        // Badge en cada red individual
        filterButtons.forEach(button => {
            const slug = button.dataset.redFilter;
            if (!slug || slug === 'all') return;
            const count = redCounts[slug] || 0;
            let badge = button.querySelector('.red-pending-badge');
            if (count > 0) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'red-pending-badge';
                    button.querySelector('.red-header')?.appendChild(badge);
                }
                badge.textContent = `${count} pend.`;
                badge.title = `${count} Casa${count > 1 ? 's' : ''} de Paz activa${count > 1 ? 's' : ''} sin reporte en los últimos 7 días`;
            } else if (badge) {
                badge.remove();
            }
        });
    }

    function updateBannerState() {
        if (!bannerReportes) return;

        const { totalAll, redCounts } = getPendingCounts();
        const currentPending = currentRedFilter === 'all' ? totalAll : (redCounts[currentRedFilter] || 0);

        const bannerTextElem = bannerReportes.querySelector('.alert-banner-text');
        const bannerTitleElem = bannerReportes.querySelector('.alert-banner-title');
        const bannerIcon = bannerReportes.querySelector('.alert-banner-icon');
        const selectedButton = document.querySelector(`[data-red-filter="${currentRedFilter}"]`);
        const redName = selectedButton?.dataset.redName || 'esta red';
        const cleanRedName = redName.replace(/^red\s+/i, '');

        if (currentPending > 0) {
            bannerReportes.classList.remove('is-hidden');
            bannerReportes.classList.remove('is-all-good');

            if (bannerIcon) bannerIcon.textContent = 'notification_important';

            if (bannerTitleElem) {
                bannerTitleElem.textContent = currentRedFilter === 'all'
                    ? 'Reportes de la Semana Pendientes'
                    : `Reportes Pendientes · Red ${cleanRedName}`;
            }

            if (bannerTextElem) {
                const scopeText = currentRedFilter === 'all'
                    ? 'en la congregación'
                    : `en la Red ${cleanRedName}`;
                bannerTextElem.innerHTML = `
                    <strong>${currentPending} Casa${currentPending > 1 ? 's' : ''} de Paz activa${currentPending > 1 ? 's' : ''}</strong> ${scopeText} no ha${currentPending > 1 ? 'n' : ''} enviado reporte en los últimos 7 días.
                `;
            }

            if (btnFiltrarPendientes) {
                btnFiltrarPendientes.innerHTML = `
                    <span class="material-symbols-outlined">filter_list</span>
                    <span>Ver ${currentPending} pendiente${currentPending > 1 ? 's' : ''}</span>
                `;
                if (currentReporteFilter === 'pendientes') {
                    btnFiltrarPendientes.classList.add('is-hidden');
                    if (btnVerTodasCasas) btnVerTodasCasas.classList.remove('is-hidden');
                } else {
                    btnFiltrarPendientes.classList.remove('is-hidden');
                    if (btnVerTodasCasas) btnVerTodasCasas.classList.add('is-hidden');
                }
            }
        } else {
            // Cero pendientes en la selección actual
            if (currentRedFilter === 'all') {
                bannerReportes.classList.add('is-hidden');
            } else {
                // Mostrar banner positivo si esta red está al día
                bannerReportes.classList.remove('is-hidden');
                bannerReportes.classList.add('is-all-good');

                if (bannerIcon) bannerIcon.textContent = 'check_circle';
                if (bannerTitleElem) bannerTitleElem.textContent = `¡Red al día! · Red ${cleanRedName}`;
                if (bannerTextElem) {
                    bannerTextElem.innerHTML = `Todas las Casas de Paz activas de la <strong>Red ${cleanRedName}</strong> han enviado su reporte en los últimos 7 días.`;
                }
                if (btnFiltrarPendientes) btnFiltrarPendientes.classList.add('is-hidden');
                if (btnVerTodasCasas) btnVerTodasCasas.classList.add('is-hidden');
            }
        }
    }

    function updateCasasVisibility() {
        const term = currentSearchTerm.toLowerCase().trim();
        let visibleCount = 0;

        casaCards.forEach(card => {
            const matchesRed = currentRedFilter === 'all' || card.dataset.red === currentRedFilter;
            const cardText = (card.dataset.search || card.textContent).toLowerCase();
            const matchesSearch = !term || cardText.includes(term);
            const matchesPendiente = currentReporteFilter === 'all' || isCardPendiente(card);
            const isVisible = matchesRed && matchesSearch && matchesPendiente;
            card.classList.toggle('is-filtered-out', !isVisible);
            if (isVisible) visibleCount++;
        });

        if (addCasaCard) {
            addCasaCard.classList.toggle('is-filtered-out', currentRedFilter === 'all' || term.length > 0 || currentReporteFilter === 'pendientes');
        }

        let emptyPendientesMsg = document.getElementById('emptyStatePendientesFilter');
        if (!emptyPendientesMsg) {
            const grid = document.querySelector('.casas-grid');
            if (grid) {
                emptyPendientesMsg = document.createElement('div');
                emptyPendientesMsg.id = 'emptyStatePendientesFilter';
                emptyPendientesMsg.className = 'empty-state is-hidden is-filtered-out';
                emptyPendientesMsg.style.gridColumn = '1 / -1';
                emptyPendientesMsg.style.display = 'none';
                emptyPendientesMsg.innerHTML = `
                    <span class="material-symbols-outlined" style="font-size: 2.6rem; color: #16a34a; margin-bottom: 0.5rem;">check_circle</span>
                    <strong style="font-size: 1.1rem; color: #15803d;">¡Al día con los reportes!</strong>
                    <span style="color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;">No hay Casas de Paz activas pendientes de reporte en esta vista.</span>
                    <button type="button" class="btn-banner-filter btn-banner-all" id="btnVerTodasDesdeEmpty" style="margin-top: 0.75rem; cursor: pointer;">
                        <span class="material-symbols-outlined">restart_alt</span>
                        <span>Ver todas las casas</span>
                    </button>
                `;
                grid.appendChild(emptyPendientesMsg);

                const btnFromEmpty = emptyPendientesMsg.querySelector('#btnVerTodasDesdeEmpty');
                if (btnFromEmpty) {
                    btnFromEmpty.addEventListener('click', function(e) {
                        e.preventDefault();
                        toggleFiltroPendientes(false);
                    });
                }
            }
        }
        if (emptyPendientesMsg) {
            const shouldHide = (visibleCount > 0) || (currentReporteFilter !== 'pendientes');
            emptyPendientesMsg.classList.toggle('is-hidden', shouldHide);
            emptyPendientesMsg.classList.toggle('is-filtered-out', shouldHide);
            emptyPendientesMsg.style.display = shouldHide ? 'none' : 'flex';
        }
    }

    function initReportesToast() {
        if (!bannerReportes) return;
        const total = parseInt(bannerReportes.dataset.totalPendientes || '0', 10);
        if (total <= 0) return;

        // Mostrar aviso toast una vez por sesión
        if (sessionStorage.getItem('reportes_toast_dismissed')) return;

        const toast = document.createElement('div');
        toast.className = 'toast-estructura';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-content">
                <span class="material-symbols-outlined toast-icon">info</span>
                <div class="toast-texts">
                    <strong>Cumplimiento Semanal</strong>
                    <span>${total} Casa${total > 1 ? 's' : ''} de Paz activa${total > 1 ? 's' : ''} sin reporte en los últimos 7 días.</span>
                </div>
            </div>
            <div class="toast-actions">
                <button type="button" class="toast-btn-action" id="toastActionVer">Ver</button>
                <button type="button" class="toast-btn-close" aria-label="Cerrar notificación">&times;</button>
            </div>
        `;
        document.body.appendChild(toast);

        // Entrada con animación
        requestAnimationFrame(() => toast.classList.add('is-visible'));

        function dismissToast() {
            sessionStorage.setItem('reportes_toast_dismissed', '1');
            toast.classList.remove('is-visible');
            setTimeout(() => toast.remove(), 350);
        }

        const closeBtn = toast.querySelector('.toast-btn-close');
        const actBtn = toast.querySelector('#toastActionVer');

        if (closeBtn) closeBtn.addEventListener('click', dismissToast);
        if (actBtn) {
            actBtn.addEventListener('click', () => {
                dismissToast();
                if (btnFiltrarPendientes) {
                    btnFiltrarPendientes.click();
                    const sec = document.querySelector('.casas-section');
                    if (sec) sec.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }

        setTimeout(() => {
            if (document.body.contains(toast)) dismissToast();
        }, 7000);
    }

    // Disparar toast tras breve retardo para que la página renderice suavemente
    setTimeout(initReportesToast, 400);

    function syncUrlParams() {
        if (!window.history || !window.history.replaceState) return;
        const url = new URL(window.location);

        if (currentRedFilter && currentRedFilter !== 'all') {
            const cleanId = currentRedFilter.replace(/^red-/, '');
            url.searchParams.set('red_id', cleanId);
            url.searchParams.delete('red');
        } else {
            url.searchParams.delete('red_id');
            url.searchParams.delete('red');
        }

        // Siempre limpiar cdp_id y casa_id cuando el usuario cambia o sincroniza los filtros
        url.searchParams.delete('cdp_id');
        url.searchParams.delete('casa_id');

        if (currentReporteFilter === 'pendientes') {
            url.searchParams.set('filtro', 'pendientes');
        } else {
            url.searchParams.delete('filtro');
        }

        if (currentSearchTerm) {
            url.searchParams.set('q', currentSearchTerm);
        } else {
            url.searchParams.delete('q');
        }

        const queryString = url.searchParams.toString();
        const cleanUrl = queryString ? `${url.pathname}?${queryString}` : url.pathname;
        window.history.replaceState(null, '', cleanUrl);
    }

    function toggleFiltroPendientes(filtrar, options = {}) {
        const { updateUrl = true } = options;
        currentReporteFilter = filtrar ? 'pendientes' : 'all';

        if (btnFiltrarPendientes && btnVerTodasCasas) {
            if (filtrar) {
                btnFiltrarPendientes.classList.add('is-hidden');
                btnVerTodasCasas.classList.remove('is-hidden');
            } else {
                btnVerTodasCasas.classList.add('is-hidden');
                btnFiltrarPendientes.classList.remove('is-hidden');
            }
        }

        if (filterLabel) {
            const selectedButton = document.querySelector(`[data-red-filter="${currentRedFilter}"]`);
            const selectedName = selectedButton?.dataset.redName || 'todas las redes';
            filterLabel.textContent = filtrar ? `${selectedName} (solo pendientes)` : selectedName;
        }

        updateCasasVisibility();

        if (filtrar) {
            const sec = document.querySelector('.casas-section');
            if (sec) {
                sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        if (updateUrl) {
            syncUrlParams();
        }
    }

    function applyRedFilter(selectedFilter, options = {}) {
        const { updateUrl = true, scrollSidebar = true } = options;
        currentRedFilter = selectedFilter;
        filterButtons.forEach(button => {
            const isSelected = button.dataset.redFilter === selectedFilter;
            const card = button.closest('.red-card');
            button.classList.toggle('active', isSelected);
            button.setAttribute('aria-pressed', String(isSelected));
            if (card) {
                card.classList.toggle('active', isSelected);
                if (isSelected && scrollSidebar) {
                    card.scrollIntoView({ behavior: 'smooth', inline: 'nearest', block: 'nearest' });
                }
            }
        });

        // Comprobar si la red seleccionada tiene pendientes; si no tiene, resetear filtro de pendientes a 'all'
        const { totalAll, redCounts } = getPendingCounts();
        const countInSelected = selectedFilter === 'all' ? totalAll : (redCounts[selectedFilter] || 0);
        if (countInSelected === 0 && currentReporteFilter === 'pendientes') {
            currentReporteFilter = 'all';
        }

        const selectedButton = document.querySelector(`[data-red-filter="${selectedFilter}"]`);
        const selectedName = selectedButton?.dataset.redName || 'todas las redes';
        if (filterLabel) {
            if (currentReporteFilter === 'pendientes') {
                filterLabel.textContent = selectedName + ' (solo pendientes)';
            } else {
                filterLabel.textContent = selectedName;
            }
        }

        updateBannerState();
        updateCasasVisibility();

        if (updateUrl) {
            syncUrlParams();
        }
    }

    if (btnFiltrarPendientes) {
        btnFiltrarPendientes.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleFiltroPendientes(true);
        });
    }

    if (btnVerTodasCasas) {
        btnVerTodasCasas.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleFiltroPendientes(false);
        });
    }

    if (bannerReportes) {
        bannerReportes.addEventListener('click', function(e) {
            const filterBtn = e.target.closest('#btnFiltrarPendientes');
            const allBtn = e.target.closest('#btnVerTodasCasas');
            if (filterBtn) {
                e.preventDefault();
                e.stopPropagation();
                toggleFiltroPendientes(true);
            } else if (allBtn) {
                e.preventDefault();
                e.stopPropagation();
                toggleFiltroPendientes(false);
            }
        });
    }

    if (searchInput) {
        let searchTimeout = null;
        searchInput.addEventListener('input', function() {
            currentSearchTerm = this.value;
            updateCasasVisibility();
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                syncUrlParams();
            }, 300);
        });
    }

    filterButtons.forEach(button => {
        button.addEventListener('click', () => applyRedFilter(button.dataset.redFilter));
        button.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                applyRedFilter(button.dataset.redFilter);
            }
        });
    });

    function initFromUrlAndContext() {
        const urlParams = new URLSearchParams(window.location.search);
        const mainElem = document.querySelector('main.estructura-main');

        const paramRed = urlParams.get('red_id') || urlParams.get('red') || mainElem?.dataset.initialRed || '';
        const paramCdp = urlParams.get('cdp_id') || urlParams.get('casa_id') || mainElem?.dataset.initialCdp || '';
        const paramFiltro = urlParams.get('filtro') || mainElem?.dataset.initialFiltro || '';
        const paramQ = urlParams.get('q') || mainElem?.dataset.initialQ || '';

        // 1. Manejo de búsqueda por texto
        if (paramQ) {
            currentSearchTerm = paramQ;
            if (searchInput) searchInput.value = paramQ;
        }

        // 2. Si vino cdp_id, ubicar tarjeta y asegurar que inferredRed sea la red exacta de la tarjeta
        let targetCdpCard = null;
        let inferredRed = paramRed;
        if (paramCdp) {
            targetCdpCard = document.querySelector(`.casa-card[data-cdp-id="${paramCdp}"]`) || document.getElementById(`cdp-${paramCdp}`);
            if (targetCdpCard) {
                targetCdpCard.style.opacity = '1';
                if (targetCdpCard.dataset.red) {
                    inferredRed = targetCdpCard.dataset.red;
                }
            }
        }

        // 3. Resolver filtro de red (número '2', slug 'red-2' o 'all')
        let resolvedRedFilter = 'all';
        if (inferredRed && inferredRed !== 'all') {
            const slug = inferredRed.startsWith('red-') ? inferredRed : `red-${inferredRed}`;
            if (document.querySelector(`[data-red-filter="${slug}"]`)) {
                resolvedRedFilter = slug;
            } else if (document.querySelector(`[data-red-filter="${inferredRed}"]`)) {
                resolvedRedFilter = inferredRed;
            }
        } else if (!inferredRed) {
            const activeBtn = document.querySelector('[data-red-filter].active');
            if (activeBtn) {
                resolvedRedFilter = activeBtn.dataset.redFilter;
            }
        }

        // Aplicar filtro de red inicial
        applyRedFilter(resolvedRedFilter, { updateUrl: false, scrollSidebar: true });

        // 4. Filtro de pendientes si vino en la URL
        if (paramFiltro === 'pendientes' || paramFiltro === '1' || paramFiltro === 'true') {
            toggleFiltroPendientes(true, { updateUrl: false });
        }

        // 5. Enfocar y resaltar Casa de Paz específica si vino cdp_id
        if (paramCdp) {
            if (!targetCdpCard) {
                targetCdpCard = document.querySelector(`.casa-card[data-cdp-id="${paramCdp}"]`) || document.getElementById(`cdp-${paramCdp}`);
            }
            if (targetCdpCard) {
                targetCdpCard.classList.remove('is-filtered-out');
                targetCdpCard.style.opacity = '1';
                setTimeout(() => {
                    targetCdpCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    targetCdpCard.classList.add('casa-card-highlighted');
                    setTimeout(() => {
                        targetCdpCard.classList.remove('casa-card-highlighted');
                        targetCdpCard.style.opacity = '1';
                    }, 3500);
                }, 350);
            }
        }
    }

    initFromUrlAndContext();
    updateSidebarPendingBadges();
    updateBannerState();

    const menuTriggers = document.querySelectorAll('.menu-trigger');
    const redesList = document.querySelector('.redes-list');
    let activeMenuData = null;

    function closeMenus() {
        if (activeMenuData) {
            const { menu, card, trigger } = activeMenuData;
            menu.classList.remove('is-open');
            menu.style.display = 'none';
            card.classList.remove('menu-open');
            card.appendChild(menu);
            trigger.setAttribute('aria-expanded', 'false');
            activeMenuData = null;
        }
    }

    menuTriggers.forEach(trigger => {
        trigger.addEventListener('click', event => {
            event.stopPropagation();
            const card = trigger.closest('.red-card');
            if (!card) return;

            // Si este mismo menú ya está abierto, cerrarlo
            if (activeMenuData && activeMenuData.trigger === trigger) {
                closeMenus();
                return;
            }

            // Cerrar cualquier otro menú abierto
            closeMenus();

            const menu = card.querySelector('.red-menu');
            if (!menu) return;

            // Guardar datos y mover a document.body para que flote sobre todo sin ser cortado ni afectar el scroll
            const rect = trigger.getBoundingClientRect();
            document.body.appendChild(menu);

            menu.style.position = 'fixed';
            menu.style.top = `${rect.bottom + 4}px`;
            menu.style.left = 'auto';
            menu.style.right = `${Math.max(8, window.innerWidth - rect.right)}px`;
            menu.style.display = 'grid';
            menu.classList.add('is-open');

            card.classList.add('menu-open');
            trigger.setAttribute('aria-expanded', 'true');

            activeMenuData = { menu, card, trigger };
        });
    });

    if (redesList) {
        redesList.addEventListener('scroll', closeMenus, { passive: true });
    }
    window.addEventListener('scroll', closeMenus, { passive: true });
    window.addEventListener('resize', closeMenus, { passive: true });

    document.addEventListener('click', event => {
        if (activeMenuData && !activeMenuData.menu.contains(event.target) && !activeMenuData.trigger.contains(event.target)) {
            closeMenus();
        }
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') closeMenus();
    });

    const sidebar = document.querySelector('.redes-sidebar');
    const arrowLeft = document.querySelector('.scroll-arrow-left');
    const arrowRight = document.querySelector('.scroll-arrow-right');

    if (!sidebar || !arrowLeft || !arrowRight) return;

    const SCROLL_AMOUNT = 150;

    function updateArrows() {
        const scrollLeft = sidebar.scrollLeft;
        const maxScroll = sidebar.scrollWidth - sidebar.clientWidth;

        if (maxScroll <= 10) {
            arrowLeft.classList.remove('visible');
            arrowRight.classList.remove('visible');
            return;
        }

        arrowLeft.classList.toggle('visible', scrollLeft > 5);
        arrowRight.classList.toggle('visible', scrollLeft < maxScroll - 5);
    }

    arrowLeft.addEventListener('click', function() {
        sidebar.scrollBy({ left: -SCROLL_AMOUNT, behavior: 'smooth' });
    });

    arrowRight.addEventListener('click', function() {
        sidebar.scrollBy({ left: SCROLL_AMOUNT, behavior: 'smooth' });
    });

    sidebar.addEventListener('scroll', updateArrows);
    window.addEventListener('resize', updateArrows);

    updateArrows();
})();
