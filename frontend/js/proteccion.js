document.addEventListener("DOMContentLoaded", () => {
    const sesionGuardada = localStorage.getItem('xadi_sesion');

    if (!sesionGuardada) {
        window.location.href = '/login';
        return;
    }

    const sesion = JSON.parse(sesionGuardada);

    if (sesion.expira !== null && new Date().getTime() > sesion.expira) {
        localStorage.removeItem('xadi_sesion');
        alert("Tu sesión ha expirado por seguridad. Vuelve a iniciar sesión.");
        window.location.href = '/login';
        return;
    }

    console.log("Sesión válida. Bienvenido:", sesion.perfil.nombre);
});

function cerrarSesion() {
    localStorage.removeItem('xadi_sesion');
    window.location.href = '/login';
}