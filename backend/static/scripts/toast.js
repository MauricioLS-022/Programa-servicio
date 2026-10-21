// Descarte automático y manual de alertas toast después de 5 segundos
document.addEventListener('DOMContentLoaded', () => {
    const toasts = document.querySelectorAll('.toast-alert');
    toasts.forEach(toast => {
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-10px)';
                toast.style.transition = 'all 0.2s ease';
                setTimeout(() => toast.remove(), 200);
            });
        }
        setTimeout(() => {
            if (document.body.contains(toast)) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-10px)';
                toast.style.transition = 'all 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    });
});
