// Gestión del modal de confirmación de eliminación con palabra clave 'ELIMINAR' para Líderes
function openDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
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
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }
}

window.openDeleteModal = openDeleteModal;
window.closeDeleteModal = closeDeleteModal;

document.addEventListener('DOMContentLoaded', () => {
    const deleteInput = document.getElementById('deleteInput');
    const btnConfirm = document.getElementById('btnConfirmDelete');
    const formEliminar = document.getElementById('formEliminarLider');

    if (deleteInput && btnConfirm) {
        deleteInput.addEventListener('input', () => {
            btnConfirm.disabled = deleteInput.value.trim().toUpperCase() !== 'ELIMINAR';
        });

        deleteInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !btnConfirm.disabled) {
                e.preventDefault();
                if (formEliminar) formEliminar.submit();
            }
        });
    }

    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeDeleteModal();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal && modal.style.display === 'flex') {
            closeDeleteModal();
        }
    });
});

