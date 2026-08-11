const API_URL = "/api";
let palabrasActuales = [];
let indiceActual = 0;
let audioObjeto = null;
let idCursoActual = 1;

async function cargarCurso(idCur, nombreCurso = "") {
    idCursoActual = idCur; 
    
    if(!nombreCurso) {
        const nombres = {
            1: "Saludos", 2: "Animales", 3: "Vestimenta", 4: "Números",
            5: "Acciones", 6: "Ubicaciones", 7: "Personas y Familia",
            8: "Utensilios", 9: "Partes del Cuerpo", 10: "Emociones", 11: "Tiempo y Cantidad"
        };
        nombreCurso = nombres[idCur] || "Curso";
    }
    
    document.getElementById("breadcrumb-curso").innerText = nombreCurso;
    window.history.pushState({}, '', `/cursos/${nombreCurso.toLowerCase()}`);
    
    actualizarMenuLateral(idCur);
    
    try {
        const response = await fetch(`/api/modulos/${idCur}/vocabulario`);
        if (!response.ok) throw new Error("No hay palabras en este curso");
        
        palabrasActuales = await response.json();
        indiceActual = 0;
        mostrarPalabra();
        actualizarIndicadores();
    } catch (error) {
        console.error(error);
        alert("Asegúrate de tener encendido tu uvicorn y datos en Supabase para este curso.");
    }
}

function actualizarMenuLateral(idCursoSeleccionado) {
    const botones = document.querySelectorAll('.curso-item');

    botones.forEach(boton => {
        const idCurso = boton.getAttribute('data-id');

        if (idCurso == idCursoSeleccionado) {
            boton.className = "curso-item flex items-center gap-4 w-full px-4 py-3 rounded-xl bg-secondary text-white shadow-md transition-all active:scale-95";
        } else {
            boton.className = "curso-item flex items-center gap-4 w-full px-4 py-3 rounded-xl text-on-surface-variant hover:bg-surface-container-high transition-all";
        }
    });
}

async function mostrarPalabra() {
    if (palabrasActuales.length === 0) return;
    const palabra = palabrasActuales[indiceActual];
    
    document.getElementById("vocabulario-espanol").innerText = palabra.espanol;
    document.getElementById("vocabulario-otomi").innerText = palabra.otomi;
    
    let avisoElement = document.getElementById("aviso-posesivo");
    if (!avisoElement) {
        const contenedorOtomi = document.getElementById("vocabulario-otomi").parentElement;
        avisoElement = document.createElement("div");
        avisoElement.id = "aviso-posesivo";
        avisoElement.className = "mt-3 inline-flex items-center gap-1.5 px-3 py-1 bg-secondary/10 text-secondary rounded-lg text-xs font-bold tracking-wide";
        avisoElement.innerHTML = `<span class="material-icons text-sm">info</span> Nota: El prefijo "ma" indica posesión ("mi").`;
        contenedorOtomi.appendChild(avisoElement);
    }

    if (idCursoActual === 9) {
        avisoElement.classList.remove("hidden");
    } else {
        avisoElement.classList.add("hidden");
    }

    const imgElement = document.getElementById("vocabulario-imagen");
    const tiempoActual = new Date().getTime(); 
    imgElement.src = `${palabra.imagen_url}?v=${tiempoActual}`;
    
    const botonAudio = document.getElementById("boton-audio");
    
    if (!palabra.audio_url || palabra.audio_url.trim() === "") {
        audioObjeto = null;
        botonAudio.classList.add("hidden");
        return;
    }
    
    const rutaAudio = palabra.audio_url;
    
    try {
        const testAudio = new Audio();
        
        const audioExiste = await new Promise((resolve) => {
            testAudio.oncanplaythrough = () => resolve(true);
            testAudio.onerror = () => resolve(false);
            testAudio.src = rutaAudio;
        });

        if (audioExiste) {
            audioObjeto = testAudio;
            botonAudio.classList.remove("hidden");
        } else {
            audioObjeto = null;
            botonAudio.classList.add("hidden");
        }
    } catch (error) {
        audioObjeto = null;
        botonAudio.classList.add("hidden");
    }
}

function reproducirAudio() {
    if (audioObjeto) {
        audioObjeto.play().catch(e => console.log("Error al reproducir audio:", e));
    }
}

function cambiarPalabra(direccion) {
    let nuevoIndice = indiceActual + direccion;
    if (nuevoIndice >= 0 && nuevoIndice < palabrasActuales.length) {
        indiceActual = nuevoIndice;
        mostrarPalabra();
        actualizarIndicadores();
    }
}

function actualizarIndicadores() {
    const contenedor = document.getElementById("indicadores-paginas");
    contenedor.innerHTML = "";
    palabrasActuales.forEach((_, i) => {
        const dot = document.createElement("div");
        dot.className = `w-2.5 h-2.5 rounded-full transition-all ${i === indiceActual ? 'bg-primary scale-110' : 'bg-primary/20'}`;
        contenedor.appendChild(dot);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;
    const mapaCursos = {
        "saludos": 1,
        "animales": 2,
        "vestimenta": 3,
        "numeros": 4,
        "acciones": 5,
        "ubicaciones": 6,
        "personas": 7,
        "utensilios": 8,
        "cuerpo": 9,
        "emociones": 10,
        "tiempo": 11
    };

    let idEncontrado = 1;
    let nombreEncontrado = "Saludos";
    
    for (const [key, value] of Object.entries(mapaCursos)) {
        if (path.includes(key)) {
            idEncontrado = value;
            nombreEncontrado = key.charAt(0).toUpperCase() + key.slice(1);
            break;
        }
    }

    cargarCurso(idEncontrado, nombreEncontrado);
});

document.addEventListener("click", (e) => {
    if (e.target.matches('#boton-salir') || e.target.closest('#boton-salir')) {
        e.preventDefault();
        
        localStorage.removeItem("xadi_sesion");
        
        window.location.replace("/login");
    }
});