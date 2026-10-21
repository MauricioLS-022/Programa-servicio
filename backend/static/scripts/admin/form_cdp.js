// Gestión de alternancia entre modo de usuario nuevo y usuario existente en el formulario de Casa de Paz.
document.addEventListener('DOMContentLoaded', () => {
    const formCdp = document.getElementById('crudFormCdp') || document.querySelector('form.crud-form');
    const isEdit = formCdp ? (formCdp.dataset.isEdit === 'true' || formCdp.getAttribute('data-is-edit') === 'true') : false;

    const radioExistente = document.getElementById('modo_existente');
    const radioNuevo = document.getElementById('modo_nuevo');
    const seccionExistente = document.getElementById('seccion-usuario-existente');
    const seccionNuevo = document.getElementById('seccion-usuario-nuevo');

    const selectExistente = document.getElementById('usuario_existente_id');
    const inputNombre = document.getElementById('nombre');
    const inputApellido = document.getElementById('apellido');
    const inputUsername = document.getElementById('username');
    const inputPassword = document.getElementById('password');

    function toggleModoUsuario() {
        const esExistente = radioExistente && radioExistente.checked;

        if (seccionExistente) {
            seccionExistente.style.display = esExistente ? 'grid' : 'none';
        }
        if (seccionNuevo) {
            seccionNuevo.style.display = esExistente ? 'none' : 'grid';
        }

        if (selectExistente) {
            selectExistente.required = esExistente;
        }

        if (inputNombre) inputNombre.required = !esExistente;
        if (inputApellido) inputApellido.required = !esExistente;
        if (inputUsername) inputUsername.required = !esExistente;
        if (inputPassword) {
            inputPassword.required = !esExistente && !isEdit;
        }
    }

    if (radioExistente) radioExistente.addEventListener('change', toggleModoUsuario);
    if (radioNuevo) radioNuevo.addEventListener('change', toggleModoUsuario);

    toggleModoUsuario();
});
