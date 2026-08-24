// Filtros, menús y desplazamiento de la vista de estructura.
(function() {
    const filterButtons = document.querySelectorAll('[data-red-filter]');
    const casaCards = document.querySelectorAll('.casa-card[data-red]');
    const filterLabel = document.getElementById('casasFilterLabel');
    const addCasaCard = document.querySelector('[data-filtered-add-card]');
    function applyRedFilter(selectedFilter) {
        filterButtons.forEach(button => {
            const isSelected = button.dataset.redFilter === selectedFilter;
            const card = button.closest('.red-card');
            button.classList.toggle('active', isSelected);
            button.setAttribute('aria-pressed', String(isSelected));
            if (card) card.classList.toggle('active', isSelected);
        });

        casaCards.forEach(card => {
            const shouldShow = selectedFilter === 'all' || card.dataset.red === selectedFilter;
            card.classList.toggle('is-filtered-out', !shouldShow);
        });

        const selectedButton = document.querySelector(`[data-red-filter="${selectedFilter}"]`);
        const selectedName = selectedButton?.dataset.redName || 'todas las redes';
        if (filterLabel) filterLabel.textContent = selectedName;
        if (addCasaCard) addCasaCard.classList.toggle('is-filtered-out', selectedFilter === 'all');
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

    applyRedFilter(document.querySelector('[data-red-filter].active')?.dataset.redFilter || 'all');

    const menuTriggers = document.querySelectorAll('.menu-trigger');
    function closeMenus() {
        document.querySelectorAll('.red-card.menu-open').forEach(card => card.classList.remove('menu-open'));
        menuTriggers.forEach(trigger => trigger.setAttribute('aria-expanded', 'false'));
    }

    menuTriggers.forEach(trigger => {
        trigger.addEventListener('click', event => {
            event.stopPropagation();
            const card = trigger.closest('.red-card');
            const willOpen = !card.classList.contains('menu-open');
            closeMenus();
            if (willOpen) {
                card.classList.add('menu-open');
                trigger.setAttribute('aria-expanded', 'true');
            }
        });
    });

    document.addEventListener('click', event => {
        if (!event.target.closest('.red-card')) closeMenus();
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
