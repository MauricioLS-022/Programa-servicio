// Gestión del modal de eliminación y validación de confirmación 'ELIMINAR' para Redes Ministeriales.
function openDeleteModal() {
    const modal = document.getElementById('deleteBlockedModal') || document.getElementById('deleteConfirmModal');
    if (modal) {
        modal.style.display = 'flex';
        const input = document.getElementById('deleteInput');
        const btn = document.getElementById('btnConfirmDelete');
        if (input && btn) {
            input.value = '';
            btn.disabled = true;
            setTimeout(() => input.focus(), 50);
        }
    }
}

function closeDeleteModal() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
}

window.openDeleteModal = openDeleteModal;
window.closeDeleteModal = closeDeleteModal;

document.addEventListener('DOMContentLoaded', () => {
    const deleteInput = document.getElementById('deleteInput');
    const btnConfirm = document.getElementById('btnConfirmDelete');
    if (deleteInput && btnConfirm) {
        deleteInput.addEventListener('input', () => {
            btnConfirm.disabled = deleteInput.value.trim().toUpperCase() !== 'ELIMINAR';
        });
        deleteInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !btnConfirm.disabled) {
                e.preventDefault();
                const form = document.getElementById('formEliminarRed');
                if (form) form.submit();
            }
        });
    }

    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeDeleteModal();
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeDeleteModal();
    });
});
