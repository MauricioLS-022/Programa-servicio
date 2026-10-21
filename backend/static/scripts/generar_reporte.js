// Micro-cálculo visual de Asistencia Total en tiempo real para el formulario de generación de reportes.
document.addEventListener('DOMContentLoaded', function() {
    const counters = document.querySelectorAll('.attendance-counter');
    const badgeTotal = document.getElementById('badge-total-asistencia');

    function updateTotal() {
        let total = 0;
        counters.forEach(function(input) {
            const val = parseInt(input.value, 10);
            if (!isNaN(val) && val > 0) {
                total += val;
            }
        });
        if (badgeTotal) {
            badgeTotal.textContent = total;
        }
    }

    counters.forEach(function(input) {
        input.addEventListener('input', updateTotal);
        input.addEventListener('change', updateTotal);
    });

    updateTotal();
});
