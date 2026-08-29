/**
 * Vino Nuevo - Control de Modales para Panel de Líder de Casa de Paz
 * Modales: Ver Detalle, Editar Reporte, Eliminar Reporte.
 */

document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // 1. MODAL DETALLE DE REPORTE
    // =========================================================================
    const modalDetalle = document.getElementById('modalDetalleReporte');
    const closeDetalleBtns = document.querySelectorAll('.btn-close-detalle');

    const detalleFields = {
        fecha: document.getElementById('detFecha'),
        horario: document.getElementById('detHorario'),
        lider: document.getElementById('detLider'),
        tema: document.getElementById('detTema'),
        regulares: document.getElementById('detRegulares'),
        ninos: document.getElementById('detNinos'),
        visitas: document.getElementById('detVisitas'),
        comprometidos: document.getElementById('detComprometidos'),
        asistencia: document.getElementById('detAsistenciaTotal'),
        reconciliaciones: document.getElementById('detReconciliaciones'),
        confesiones: document.getElementById('detConfesiones'),
        ofrendasBs: document.getElementById('detOfrendasBs'),
        ofrendasUsd: document.getElementById('detOfrendasUsd'),
        cesta: document.getElementById('detCesta'),
        observaciones: document.getElementById('detObservaciones')
    };

    function openDetalleModal(btn) {
        if (!modalDetalle) return;

        const d = btn.dataset;
        if (detalleFields.fecha) detalleFields.fecha.value = d.fechaFormateada || d.fecha || '';
        if (detalleFields.horario) detalleFields.horario.value = (d.hrInicio && d.hrFin) ? `${d.hrInicio} - ${d.hrFin}` : (d.hrInicio || 'No registrado');
        if (detalleFields.lider) detalleFields.lider.value = d.liderNombre || 'Líder Encargado';
        if (detalleFields.tema) detalleFields.tema.value = d.tema || 'Sin tema registrado';
        if (detalleFields.regulares) detalleFields.regulares.value = d.regulares || 0;
        if (detalleFields.ninos) detalleFields.ninos.value = d.ninos || 0;
        if (detalleFields.visitas) detalleFields.visitas.value = d.visitas || 0;
        if (detalleFields.comprometidos) detalleFields.comprometidos.value = d.comprometidos || 0;
        if (detalleFields.asistencia) detalleFields.asistencia.textContent = d.asistencia || 0;
        if (detalleFields.reconciliaciones) detalleFields.reconciliaciones.value = d.reconciliaciones || 0;
        if (detalleFields.confesiones) detalleFields.confesiones.value = d.confesiones || 0;
        if (detalleFields.ofrendasBs) detalleFields.ofrendasBs.value = `Bs. ${parseFloat(d.ofrendasBs || 0).toFixed(2)}`;
        if (detalleFields.ofrendasUsd) detalleFields.ofrendasUsd.value = `$${parseFloat(d.ofrendasUsd || d.ofrendas || 0).toFixed(2)}`;
        const tieneCesta = (d.cesta === '1' || d.cesta === 'true' || d.cesta === 'True' || d.cesta === 1 || d.cesta === true || d.cesta === 'Sí' || d.cesta === 'Si');
        if (detalleFields.cesta) detalleFields.cesta.value = tieneCesta ? 'Sí' : 'No';
        if (detalleFields.observaciones) detalleFields.observaciones.value = d.observaciones || 'Sin observaciones adicionales.';

        modalDetalle.classList.add('active');
        modalDetalle.setAttribute('aria-hidden', 'false');
    }

    function closeDetalleModal() {
        if (!modalDetalle) return;
        modalDetalle.classList.remove('active');
        modalDetalle.setAttribute('aria-hidden', 'true');
    }

    // =========================================================================
    // 2. MODAL EDITAR REPORTE
    // =========================================================================
    const modalEditar = document.getElementById('modalEditarReporte');
    const formEditar = document.getElementById('formEditarReporte');
    const closeEditarBtns = document.querySelectorAll('.btn-close-editar');

    const editInputs = {
        liderSelect: document.getElementById('editLiderId'),
        fecha: document.getElementById('editFecha'),
        hrInicio: document.getElementById('editHrInicio'),
        hrFin: document.getElementById('editHrFin'),
        tema: document.getElementById('editTema'),
        regulares: document.getElementById('editRegulares'),
        ninos: document.getElementById('editNinos'),
        visitas: document.getElementById('editVisitas'),
        comprometidos: document.getElementById('editComprometidos'),
        asistenciaTotal: document.getElementById('editAsistenciaTotal'),
        reconciliaciones: document.getElementById('editReconciliaciones'),
        confesiones: document.getElementById('editConfesiones'),
        ofrendasBs: document.getElementById('editOfrendasBs'),
        ofrendasUsd: document.getElementById('editOfrendasUsd'),
        cesta: document.getElementById('editCestaAmor'),
        observaciones: document.getElementById('editObservaciones')
    };

    function calcularAsistenciaEdicion() {
        if (!editInputs.asistenciaTotal) return;
        const r = parseInt(editInputs.regulares?.value, 10) || 0;
        const n = parseInt(editInputs.ninos?.value, 10) || 0;
        const v = parseInt(editInputs.visitas?.value, 10) || 0;
        const c = parseInt(editInputs.comprometidos?.value, 10) || 0;
        editInputs.asistenciaTotal.textContent = (r + n + v + c).toString();
    }

    [editInputs.regulares, editInputs.ninos, editInputs.visitas, editInputs.comprometidos].forEach(input => {
        if (input) {
            input.addEventListener('input', calcularAsistenciaEdicion);
        }
    });

    function openEditarModal(btn) {
        if (!modalEditar || !formEditar) return;

        const d = btn.dataset;
        const reporteId = d.id;

        // Actualizar URL de acción del formulario
        formEditar.action = `/lider_cdp/reporte/${reporteId}/editar`;

        // Pre-cargar valores
        if (editInputs.liderSelect) {
            editInputs.liderSelect.value = d.liderId || '';
        }
        if (editInputs.fecha) editInputs.fecha.value = d.fecha || '';
        if (editInputs.hrInicio) editInputs.hrInicio.value = d.hrInicio || '';
        if (editInputs.hrFin) editInputs.hrFin.value = d.hrFin || '';
        if (editInputs.tema) editInputs.tema.value = d.tema || '';
        if (editInputs.regulares) editInputs.regulares.value = d.regulares || 0;
        if (editInputs.ninos) editInputs.ninos.value = d.ninos || 0;
        if (editInputs.visitas) editInputs.visitas.value = d.visitas || 0;
        if (editInputs.comprometidos) editInputs.comprometidos.value = d.comprometidos || 0;
        if (editInputs.reconciliaciones) editInputs.reconciliaciones.value = d.reconciliaciones || 0;
        if (editInputs.confesiones) editInputs.confesiones.value = d.confesiones || 0;
        if (editInputs.ofrendasBs) editInputs.ofrendasBs.value = parseFloat(d.ofrendasBs || 0).toFixed(2);
        if (editInputs.ofrendasUsd) editInputs.ofrendasUsd.value = parseFloat(d.ofrendasUsd || d.ofrendas || 0).toFixed(2);
        if (editInputs.cesta) {
            const tieneCesta = (d.cesta === '1' || d.cesta === 'true' || d.cesta === 'True' || d.cesta === 1 || d.cesta === true || d.cesta === 'Sí' || d.cesta === 'Si');
            editInputs.cesta.value = tieneCesta ? '1' : '0';
        }
        if (editInputs.observaciones) editInputs.observaciones.value = d.observaciones || '';

        calcularAsistenciaEdicion();

        modalEditar.classList.add('active');
        modalEditar.setAttribute('aria-hidden', 'false');
    }

    function closeEditarModal() {
        if (!modalEditar) return;
        modalEditar.classList.remove('active');
        modalEditar.setAttribute('aria-hidden', 'true');
    }

    // =========================================================================
    // 3. MODAL ELIMINAR REPORTE
    // =========================================================================
    const modalEliminar = document.getElementById('modalEliminarReporte');
    const formEliminar = document.getElementById('formEliminarReporte');
    const closeEliminarBtns = document.querySelectorAll('.btn-close-eliminar');
    const deleteFechaPreview = document.getElementById('delFechaPreview');
    const deleteTemaPreview = document.getElementById('delTemaPreview');
    const deleteAsistenciaPreview = document.getElementById('delAsistenciaPreview');

    function openEliminarModal(btn) {
        if (!modalEliminar || !formEliminar) return;

        const d = btn.dataset;
        const reporteId = d.id;

        // Actualizar URL de acción del formulario
        formEliminar.action = `/lider_cdp/reporte/${reporteId}/eliminar`;

        if (deleteFechaPreview) deleteFechaPreview.textContent = d.fechaFormateada || d.fecha || '-';
        if (deleteTemaPreview) deleteTemaPreview.textContent = d.tema || 'Sin tema registrado';
        if (deleteAsistenciaPreview) deleteAsistenciaPreview.textContent = `${d.asistencia || 0} personas`;

        modalEliminar.classList.add('active');
        modalEliminar.setAttribute('aria-hidden', 'false');
    }

    function closeEliminarModal() {
        if (!modalEliminar) return;
        modalEliminar.classList.remove('active');
        modalEliminar.setAttribute('aria-hidden', 'true');
    }

    // =========================================================================
    // 4. EVENT LISTENERS PARA BOTONES
    // =========================================================================
    document.querySelectorAll('.btn-action-view').forEach(btn => {
        btn.addEventListener('click', () => openDetalleModal(btn));
    });

    document.querySelectorAll('.btn-action-edit').forEach(btn => {
        btn.addEventListener('click', () => openEditarModal(btn));
    });

    document.querySelectorAll('.btn-action-delete').forEach(btn => {
        btn.addEventListener('click', () => openEliminarModal(btn));
    });

    closeDetalleBtns.forEach(btn => btn.addEventListener('click', closeDetalleModal));
    closeEditarBtns.forEach(btn => btn.addEventListener('click', closeEditarModal));
    closeEliminarBtns.forEach(btn => btn.addEventListener('click', closeEliminarModal));

    // Cerrar al hacer clic en el backdrop
    [modalDetalle, modalEditar, modalEliminar].forEach(m => {
        if (m) {
            m.addEventListener('click', (e) => {
                if (e.target === m) {
                    m.classList.remove('active');
                    m.setAttribute('aria-hidden', 'true');
                }
            });
        }
    });

    // Cerrar con Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeDetalleModal();
            closeEditarModal();
            closeEliminarModal();
        }
    });
});
