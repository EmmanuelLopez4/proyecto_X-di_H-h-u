document.getElementById('registro-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const nombre = document.getElementById('nombre').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    const errorDiv = document.getElementById('error-message');
    const successDiv = document.getElementById('success-message');

    errorDiv.classList.add('hidden');
    successDiv.classList.add('hidden');

    if (password !== confirmPassword) {
        errorDiv.innerText = "Las contraseñas no coinciden.";
        errorDiv.classList.remove('hidden');
        return;
    }

    try {
        const response = await fetch('/api/auth/registro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                correo: email, 
                password: password, 
                nombre_completo: nombre 
            })
        });

        const data = await response.json();

        if (response.ok) {
            successDiv.classList.remove('hidden');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            errorDiv.innerText = data.detail || "Error al crear la cuenta.";
            errorDiv.classList.remove('hidden');
        }
    } catch (error) {
        console.error("Error de conexión:", error);
        errorDiv.innerText = "Error de conexión con el servidor.";
        errorDiv.classList.remove('hidden');
    }
});