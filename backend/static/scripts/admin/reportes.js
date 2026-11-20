/**
 * Vino Nuevo - Reportes de Actividad Ministerial
 * Control del modal de detalle, filtros dinámicos y exportación de reportes a PDF/Excel.
 */
document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // 1. FILTROS DINÁMICOS
    // ==========================================
    const filterForm = document.querySelector('.filter-section');
    const redSelect = document.getElementById('filter-red');
    const cdpSelect = document.getElementById('filter-cdp');
    const fechaDesde = document.getElementById('fecha_desde');
    const fechaHasta = document.getElementById('fecha_hasta');
    const searchInput = document.getElementById('filter-search');

    [redSelect, cdpSelect].forEach(select => {
        if (select && filterForm) {
            select.addEventListener('change', () => filterForm.submit());
        }
    });

    if (searchInput && filterForm) {
        searchInput.addEventListener('search', () => filterForm.submit());
    }

    if (fechaDesde && fechaHasta && filterForm) {
        [fechaDesde, fechaHasta].forEach(input => {
            input.addEventListener('change', () => {
                if (fechaDesde.value && fechaHasta.value) {
                    filterForm.submit();
                }
            });
        });
    }

    // ==========================================
    // 2. MODAL DE DETALLES DEL REPORTE
    // ==========================================
    const modal = document.getElementById('reporteModal');
    const modalClose = document.getElementById('modalClose');
    const modalCancel = document.getElementById('modalCancel');
    const modalSave = document.getElementById('modalSave');
    const modalTitle = document.getElementById('modalTitle');
    const modalHeaderIcon = document.getElementById('modalHeaderIcon');
    const reporteForm = document.getElementById('reporteForm');
    const modalReporteId = document.getElementById('modalReporteId');
    const modalCdpId = document.getElementById('modalCdpId');
    const modalCestaSelect = document.getElementById('modalCestaSelect');
    let lastFocusedBtn = null;

    const fields = {
        lider: document.getElementById('modalLider'),
        casa: document.getElementById('modalCasa'),
        fecha: document.getElementById('modalFecha'),
        horaInicio: document.getElementById('modalHoraInicio'),
        horaFin: document.getElementById('modalHoraFin'),
        regulares: document.getElementById('modalRegulares'),
        ninos: document.getElementById('modalNinos'),
        visitas: document.getElementById('modalVisitas'),
        comprometidos: document.getElementById('modalComprometidos'),
        asistencia: document.getElementById('modalAsistencia'),
        reconciliaciones: document.getElementById('modalReconciliaciones'),
        confesiones: document.getElementById('modalConfesiones'),
        ofrendasBs: document.getElementById('modalOfrendasBs'),
        ofrendasUsd: document.getElementById('modalOfrendasUsd'),
        cesta: document.getElementById('modalCesta'),
        tema: document.getElementById('modalTema'),
        obs: document.getElementById('modalObs')
    };

    function calcAsistencia() {
        if (!fields.regulares) return 0;
        const r = parseInt(fields.regulares.value, 10) || 0;
        const n = parseInt(fields.ninos.value, 10) || 0;
        const v = parseInt(fields.visitas.value, 10) || 0;
        const c = parseInt(fields.comprometidos.value, 10) || 0;
        const total = r + n + v + c;
        if (fields.asistencia) {
            fields.asistencia.textContent = total.toString();
        }
        return total;
    }

    function formatTime12h(timeStr) {
        if (!timeStr) return 'No registrado';
        const match = timeStr.toString().trim().match(/^(\d{1,2}):(\d{2})/);
        if (!match) return timeStr;
        let hours = parseInt(match[1], 10);
        const minutes = match[2];
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        if (hours === 0) hours = 12;
        const padHours = hours < 10 ? '0' + hours : hours;
        return `${padHours}:${minutes} ${ampm}`;
    }

    function formatTime24h(val) {
        if (!val) return '';
        const parts = val.toString().trim().split(':');
        if (parts.length >= 2 && !isNaN(parseInt(parts[0], 10)) && !isNaN(parseInt(parts[1], 10))) {
            const h = parts[0].padStart(2, '0');
            const m = parts[1].padStart(2, '0');
            return `${h}:${m}`;
        }
        return val;
    }

    function openModal(btn, isEdit) {
        if (!modal) return;
        lastFocusedBtn = btn;
        const d = btn.dataset;

        // Título e Icono del Modal
        if (modalTitle) {
            modalTitle.textContent = isEdit ? 'Editar Reporte Semanal' : 'Detalle del Reporte';
        }
        if (modalHeaderIcon) {
            modalHeaderIcon.textContent = isEdit ? 'edit_document' : 'visibility';
        }
        if (modalCancel) {
            modalCancel.textContent = isEdit ? 'Cancelar' : 'Cerrar';
        }

        // Action y campos ocultos
        if (modalReporteId) modalReporteId.value = d.id || '';
        if (modalCdpId) modalCdpId.value = d.cdpId || '';
        if (reporteForm) {
            reporteForm.action = `/admin/reporte/${d.id || ''}/editar`;
        }

        // Sección 1: Fecha y Encargado
        if (fields.lider) fields.lider.value = d.lider || 'Líder Encargado';
        if (fields.casa) fields.casa.value = d.casa || '';

        if (fields.fecha) {
            if (isEdit) {
                fields.fecha.type = 'date';
                fields.fecha.value = d.fechaIso || d.fecha || '';
                fields.fecha.readOnly = false;
            } else {
                fields.fecha.type = 'text';
                fields.fecha.value = d.fecha || '';
                fields.fecha.readOnly = true;
            }
        }

        if (fields.tema) {
            fields.tema.value = d.tema || '';
            fields.tema.readOnly = !isEdit;
        }

        if (fields.horaInicio) {
            if (isEdit) {
                fields.horaInicio.type = 'time';
                fields.horaInicio.value = formatTime24h(d.horaInicio);
                fields.horaInicio.readOnly = false;
            } else {
                fields.horaInicio.type = 'text';
                fields.horaInicio.value = formatTime12h(d.horaInicio);
                fields.horaInicio.readOnly = true;
            }
        }

        if (fields.horaFin) {
            if (isEdit) {
                fields.horaFin.type = 'time';
                fields.horaFin.value = formatTime24h(d.horaFin);
                fields.horaFin.readOnly = false;
            } else {
                fields.horaFin.type = 'text';
                fields.horaFin.value = formatTime12h(d.horaFin);
                fields.horaFin.readOnly = true;
            }
        }

        // Sección 2: Asistencia y Desglose
        if (fields.regulares) {
            fields.regulares.value = d.regulares || 0;
            fields.regulares.readOnly = !isEdit;
        }
        if (fields.ninos) {
            fields.ninos.value = d.ninos || 0;
            fields.ninos.readOnly = !isEdit;
        }
        if (fields.visitas) {
            fields.visitas.value = d.visitas || 0;
            fields.visitas.readOnly = !isEdit;
        }
        if (fields.comprometidos) {
            fields.comprometidos.value = d.comprometidos || 0;
            fields.comprometidos.readOnly = !isEdit;
        }
        calcAsistencia();

        // Sección 3: Ministerio y Ofrendas
        if (fields.reconciliaciones) {
            fields.reconciliaciones.value = d.reconciliaciones || 0;
            fields.reconciliaciones.readOnly = !isEdit;
        }
        if (fields.confesiones) {
            fields.confesiones.value = d.confesiones || 0;
            fields.confesiones.readOnly = !isEdit;
        }

        const rawOfrendasBs = parseFloat(d.ofrendasBs || 0);
        const rawOfrendasUsd = parseFloat(d.ofrendasUsd || 0);

        if (fields.ofrendasBs) {
            if (isEdit) {
                fields.ofrendasBs.type = 'number';
                fields.ofrendasBs.step = '0.01';
                fields.ofrendasBs.min = '0';
                fields.ofrendasBs.value = rawOfrendasBs.toFixed(2);
                fields.ofrendasBs.readOnly = false;
            } else {
                fields.ofrendasBs.type = 'text';
                fields.ofrendasBs.value = `Bs. ${rawOfrendasBs.toFixed(2)}`;
                fields.ofrendasBs.readOnly = true;
            }
        }

        if (fields.ofrendasUsd) {
            if (isEdit) {
                fields.ofrendasUsd.type = 'number';
                fields.ofrendasUsd.step = '0.01';
                fields.ofrendasUsd.min = '0';
                fields.ofrendasUsd.value = rawOfrendasUsd.toFixed(2);
                fields.ofrendasUsd.readOnly = false;
            } else {
                fields.ofrendasUsd.type = 'text';
                fields.ofrendasUsd.value = `$${rawOfrendasUsd.toFixed(2)}`;
                fields.ofrendasUsd.readOnly = true;
            }
        }

        const tieneCesta = (d.cestaVal === '1' || d.cesta === 'Sí' || d.cesta === 'Si' || d.cesta === 'true' || d.cesta === '1');
        if (isEdit) {
            if (fields.cesta) fields.cesta.style.display = 'none';
            if (modalCestaSelect) {
                modalCestaSelect.style.display = 'block';
                modalCestaSelect.value = tieneCesta ? '1' : '0';
            }
        } else {
            if (fields.cesta) {
                fields.cesta.style.display = 'block';
                fields.cesta.value = tieneCesta ? 'Sí' : 'No';
                fields.cesta.readOnly = true;
            }
            if (modalCestaSelect) modalCestaSelect.style.display = 'none';
        }

        if (fields.obs) {
            fields.obs.value = d.obs || '';
            fields.obs.readOnly = !isEdit;
        }

        if (modalSave) modalSave.style.display = isEdit ? 'inline-flex' : 'none';
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        if (modalClose) modalClose.focus();
    }

    function closeModal() {
        if (!modal) return;
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        if (lastFocusedBtn) {
            lastFocusedBtn.focus();
            lastFocusedBtn = null;
        }
    }

    [fields.regulares, fields.ninos, fields.visitas, fields.comprometidos].forEach(f => {
        if (f) {
            f.addEventListener('input', calcAsistencia);
        }
    });

    document.querySelectorAll('.btn-view').forEach(btn => {
        btn.addEventListener('click', () => openModal(btn, false));
    });

    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', () => openModal(btn, true));
    });

    if (modalClose) modalClose.addEventListener('click', closeModal);
    if (modalCancel) modalCancel.addEventListener('click', closeModal);
    if (modal) {
        modal.addEventListener('click', e => {
            if (e.target === modal) closeModal();
        });
    }

    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
            closeModal();
        }
    });

    if (reporteForm) {
        reporteForm.addEventListener('submit', () => {
            if (modalSave) {
                modalSave.disabled = true;
                modalSave.innerHTML = '<span class="material-symbols-outlined spin">sync</span> Guardando...';
            }
        });
    }

    // ==========================================
    // 3. EXPORTACIÓN REAL SERVER-SIDE A PDF / EXCEL (.xlsx)
    // ==========================================
    const btnExportPdf = document.querySelector('.footer-actions button:first-child');
    const btnExportExcel = document.querySelector('.footer-actions button:last-child');

    function buildReportesExportUrl(format) {
        const params = new URLSearchParams({ format });
        if (searchInput && searchInput.value.trim()) params.set('q', searchInput.value.trim());
        if (redSelect && redSelect.value.trim()) params.set('red_id', redSelect.value.trim());
        if (cdpSelect && cdpSelect.value.trim()) params.set('cdp_id', cdpSelect.value.trim());
        if (fechaDesde && fechaDesde.value.trim()) params.set('fecha_desde', fechaDesde.value.trim());
        if (fechaHasta && fechaHasta.value.trim()) params.set('fecha_hasta', fechaHasta.value.trim());
        return `/api/export/reportes?${params.toString()}`;
    }

    if (btnExportExcel) {
        btnExportExcel.addEventListener('click', () => {
            window.location.href = buildReportesExportUrl('xlsx');
        });
    }

    if (btnExportPdf) {
        btnExportPdf.addEventListener('click', () => {
            window.location.href = buildReportesExportUrl('pdf');
        });
    }
});

