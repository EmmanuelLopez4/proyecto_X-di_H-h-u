import os
from fastapi import FastAPI, HTTPException            
from fastapi.responses import FileResponse                 
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Error crítico: No se encontraron las credenciales de Supabase en el archivo .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="IndigTranslate API",
    description="Backend conectado a Supabase con soporte multimedia de Audio e Imagen",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


class RegistroUsuario(BaseModel):
    nombre_completo: str
    correo: EmailStr
    password: str

class LoginUsuario(BaseModel):
    correo: EmailStr
    password: str

class CambioPassword(BaseModel):
    email: str
    nueva_password: str

@app.post("/api/cambiar-password", summary="Actualizar contraseña del usuario", tags=["Autenticación"])
def cambiar_password(datos: CambioPassword):
    try:
        correo_limpio = datos.email.strip()
        
        response = supabase.table("usuarios").select("id_usu").eq("correo", correo_limpio).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No se encontró una cuenta registrada con ese correo.")
            
        id_usuario = response.data[0]["id_usu"]
        
        supabase.auth.admin.update_user_by_id(
            id_usuario,
            {"password": datos.nueva_password}
        )
        
        return {"status": "success", "message": "Contraseña actualizada correctamente."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cambiar-password", tags=["Interfaz Gráfica"])
def pagina_cambiar_password():
    """
    Ruta para servir la vista web de cambio de contraseña
    """
    ruta_html = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "cambiar_contra.html"
    )
    if os.path.exists(ruta_html):
        return FileResponse(ruta_html)
    return {"error": "No se encontró cambiar_contra.html"}


@app.get("/", tags=["Interfaz Gráfica"])
def pagina_bienvenida():
    """
    Ruta principal:
    http://localhost:8000/
    Muestra la página de inicio.
    """
    ruta_inicio = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "inicio.html"
    )

    if os.path.exists(ruta_inicio):
        return FileResponse(ruta_inicio)

    return {
        "status": "Online",
        "error": "No se encontró inicio.html"
    }


@app.get("/cursos/{categoria}", tags=["Interfaz Gráfica"])
def pagina_curso_especifico(categoria: str):
    """
    Rutas:
    /cursos/vestimenta
    /cursos/familia
    /cursos/animales
    /cursos/saludos

    Todas muestran aprendizaje.html.
    El JavaScript se encargará de leer la categoría.
    """
    ruta_aprendizaje = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "aprendizaje.html"
    )

    if os.path.exists(ruta_aprendizaje):
        return FileResponse(ruta_aprendizaje)

    return {
        "status": "Online",
        "error": "No se encontró aprendizaje.html"
    }



@app.post("/api/auth/registro", summary="Registrar un nuevo estudiante", tags=["Autenticación"])
def registrar_usuario(usuario: RegistroUsuario):
    try:
        auth_response = supabase.auth.sign_up({
            "email": usuario.correo, 
            "password": usuario.password,
            "options": {
                "data": {
                    "nombre_completo": usuario.nombre_completo
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="No se pudo procesar la autenticación en Supabase.")
            
        return {"status": "success", "message": "Usuario registrado exitosamente.", "id_usuario": auth_response.user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en el registro: {str(e)}")


@app.post("/api/auth/login", summary="Iniciar sesión en la plataforma", tags=["Autenticación"])
def login_usuario(credenciales: LoginUsuario):
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": credenciales.correo, "password": credenciales.password})
        if not auth_response.session:
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
            
        user_uuid = auth_response.user.id
        access_token = auth_response.session.access_token
        perfil_response = supabase.table("usuarios").select("nombre, rol").eq("id_usu", user_uuid).execute()
        
        nombre = "Usuario"
        rol = "estudiante"
        if perfil_response.data:
            nombre = perfil_response.data[0].get("nombre", nombre)
            rol = perfil_response.data[0].get("rol", rol)
            
        return {
            "status": "success",
            "message": f"Bienvenido, {nombre}",
            "token_acceso": access_token,
            "perfil": {"id_usuario": user_uuid, "nombre": nombre, "correo": credenciales.correo, "rol": rol}
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Fallo de autenticación: {str(e)}")



@app.get("/api/modulos", summary="Obtener todos los cursos con sus imágenes de portada", tags=["Módulos Didácticos"])
def obtener_cursos():
    try:
        response = supabase.table("cursos").select("id_cur, nombre, descripcion, imagen_url").order("id_cur").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la tabla cursos: {str(e)}")


@app.get("/api/modulos/{id_cur}/vocabulario", summary="Obtener vocabulario con audios e imágenes por curso", tags=["Módulos Didácticos"])
def obtener_vocabulario(id_cur: int):
    try:
        response = supabase.table("vocabulario")\
            .select("id_pal, espanol, otomi, audio_url, imagen_url")\
            .eq("id_cur2", id_cur)\
            .order("id_pal", desc=False)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Este curso aún no cuenta con palabras registradas.")
            
        return response.data
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la tabla vocabulario: {str(e)}")
    


@app.get("/api/usuarios/{id_usu}/progreso", summary="Obtener el progreso del alumno para el Dashboard", tags=["Dashboard"])
def obtener_progreso_usuario(id_usu: str):
    try:
        response = supabase.table("progreso_usuario")\
            .select("id_cur2, porcentaje, estado, cursos(nombre, imagen_url)")\
            .eq("id_usu1", id_usu)\
            .execute()
            
        return {
            "status": "success",
            "id_usuario": id_usu,
            "progreso": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el progreso del Dashboard: {str(e)}")
    
@app.get("/login", tags=["Interfaz Gráfica"])
def pagina_login():
    """
    Ruta:
    http://localhost:8000/login
    
    Muestra la pantalla de inicio de sesión (prototipo).
    """
    ruta_login = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "login.html"
    )

    if os.path.exists(ruta_login):
        return FileResponse(ruta_login)

    return {
        "status": "Online",
        "error": "No se encontró login.html en la carpeta frontend"
    }

@app.get("/registro", tags=["Interfaz Gráfica"])
def pagina_registro():
    """
    Ruta:
    http://localhost:8000/registro
    
    Muestra la pantalla para crear una cuenta nueva.
    """
    ruta_registro = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "registro.html"
    )

    if os.path.exists(ruta_registro):
        return FileResponse(ruta_registro)

    return {
        "status": "Online",
        "error": "No se encontró registro.html en la carpeta frontend"
    }

@app.get("/proyecto", tags=["Interfaz Gráfica"])
def pagina_proyecto():
    """
    Ruta:
    http://localhost:8000/proyecto
    
    Muestra la pantalla informativa con el objetivo y problemática del proyecto.
    """
    ruta_proyecto = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "proyecto.html"
    )

    if os.path.exists(ruta_proyecto):
        return FileResponse(ruta_proyecto)

    return {
        "status": "Online",
        "error": "No se encontró proyecto.html en la carpeta frontend"
    }

@app.get("/equipo", tags=["Interfaz Gráfica"])
def pagina_equipo():
    """
    Ruta:
    http://localhost:8000/equipo
    
    Muestra la pantalla con la información de los desarrolladores.
    """
    ruta_equipo = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "equipo.html"
    )

    if os.path.exists(ruta_equipo):
        return FileResponse(ruta_equipo)

    return {
        "status": "Online",
        "error": "No se encontró equipo.html en la carpeta frontend"
    }

@app.get("/consejos", tags=["Interfaz Gráfica"])
def pagina_consejos():
    """
    Ruta:
    http://localhost:8000/consejos
    Muestra la pantalla de consejos generales sobre el hñähñu.
    """
    ruta_consejos = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "consejos.html"
    )

    if os.path.exists(ruta_consejos):
        return FileResponse(ruta_consejos)

    return {
        "status": "Online",
        "error": "No se encontró consejos.html en la carpeta frontend"
    }

@app.get("/cursos", tags=["Interfaz Gráfica"])
def pagina_cursos_general():
    """
    Ruta:
    http://localhost:8000/cursos
    Carga la pantalla general para elegir un curso.
    """
    ruta_cursos = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "cursos_general.html"
    )

    if os.path.exists(ruta_cursos):
        return FileResponse(ruta_cursos)

    return {
        "status": "Online",
        "error": "No se encontró cursos_general.html"
    }


@app.get("/api/memorama/aleatorio", summary="Obtener palabras aleatorias para el memorama", tags=["Minijuego Memorama"])
def obtener_vocabulario_aleatorio(limite: int = 8):
    """
    Obtiene registros aleatorios de la tabla vocabulario para armar el memorama.
    El parámetro 'limite' define cuántas parejas se necesitan (8 para 4x4, 18 para 6x6).
    """
    try:
        response = supabase.table("vocabulario")\
            .select("id_pal, espanol, otomi, imagen_url")\
            .execute()
        
        palabras = response.data
        
        if not palabras or len(palabras) < limite:
            raise HTTPException(
                status_code=400, 
                detail=f"No hay suficientes palabras en la base de datos para este modo (Se requieren al menos {limite})."
            )
            
        import random
        random.shuffle(palabras)
        seleccionadas = palabras[:limite]
        
        return {
            "status": "success",
            "parejas": seleccionadas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener palabras aleatorias: {str(e)}")

@app.get("/memorama", tags=["Interfaz Gráfica"])
def pagina_memorama():
    """
    Ruta: http://localhost:8000/memorama
    Muestra la interfaz del minijuego de memorama.
    """
    ruta_memorama = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "memorama.html"
    )

    if os.path.exists(ruta_memorama):
        return FileResponse(ruta_memorama)

    return {
        "status": "Online",
        "error": "No se encontró memorama.html en la carpeta frontend"
    }



@app.get("/memorama", tags=["Interfaz Gráfica"])
def pagina_memorama():
    ruta_memorama = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "memorama.html"
    )

    if os.path.exists(ruta_memorama):
        return FileResponse(ruta_memorama)

    return {
        "status": "Online",
        "error": "No se encontró memorama.html en la carpeta frontend"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port
    )
