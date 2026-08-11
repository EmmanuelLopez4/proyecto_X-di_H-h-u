document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('error-message');

    errorDiv.classList.add('hidden');

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                correo: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            const recordar = document.getElementById('recordarme').checked;
            const unDia = 86400000;
            const sieteDias = 604800000;
            const tiempoCaducidad = recordar
            ? new Date().getTime() + sieteDias
            : new Date().getTime() + unDia;
            const sesionData = {
                
                token: data.token_acceso,
                perfil: data.perfil,
                expira: tiempoCaducidad
            };
            localStorage.setItem('xadi_sesion', JSON.stringify(sesionData));
            window.location.href = '/cursos';
        } else {
            errorDiv.innerText = data.detail || "Error al iniciar sesión.";
            errorDiv.classList.remove('hidden');
        }

    } catch (error) {
        console.error("Error de conexión:", error);
        errorDiv.innerText = "Error de conexión con el servidor.";
        errorDiv.classList.remove('hidden');
    }
});