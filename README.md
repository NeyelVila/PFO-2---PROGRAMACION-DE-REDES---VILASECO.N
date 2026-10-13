# PFO 2 – Sistema de Gestión de Tareas con API y Base de Datos

API REST hecha con **Flask** y **SQLite**, con registro e inicio de sesión de usuarios (contraseñas hasheadas) y un cliente de consola.

## Estructura

```
pfo2/
├── servidor.py        # API Flask + SQLite
├── cliente.py         # Cliente de consola
├── requirements.txt
├── README.md
└── capturas/          # Capturas de pruebas exitosas
```

## Cómo ejecutar

```bash
git clone https://github.com/<tu-usuario>/<tu-repo>.git
cd <tu-repo>
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python servidor.py
```

El servidor queda en `http://127.0.0.1:5000`. La base `tareas.db` se crea sola al iniciar.

## Endpoints

| Método | Ruta        | Descripción                                   | Respuestas        |
|--------|-------------|-----------------------------------------------|-------------------|
| POST   | `/registro` | Crea un usuario (contraseña hasheada)         | 201, 400, 409     |
| POST   | `/login`    | Verifica credenciales e inicia sesión         | 200, 400, 401     |
| GET    | `/tareas`   | HTML de bienvenida (requiere haber hecho login) | 200, 401        |

Cuerpo JSON para `/registro` y `/login`:

```json
{"usuario": "nombre", "contraseña": "1234"}
```

## Cómo probar

### Con el cliente de consola
En otra terminal (con el servidor corriendo):

```bash
python cliente.py
```

Registrarse (1) → Iniciar sesión (2) → Ver tareas (3).

### Con curl
```bash
curl -X POST http://127.0.0.1:5000/registro -H "Content-Type: application/json" \
     -d '{"usuario":"ana","contraseña":"1234"}'

curl -c cookies.txt -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" \
     -d '{"usuario":"ana","contraseña":"1234"}'

curl -b cookies.txt http://127.0.0.1:5000/tareas
```
(En Windows PowerShell conviene usar Postman/Thunder Client o el `cliente.py`, por el manejo de comillas.)

## Capturas de pruebas exitosas

Guardá en `capturas/` imágenes de:
1. Registro exitoso (201)
2. Registro duplicado (409)
3. Login con contraseña incorrecta (401)
4. Login correcto (200)
5. `/tareas` sin sesión (401) y con sesión (HTML de bienvenida)
6. La tabla `usuarios` mostrando `password_hash` (no texto plano)

## GitHub Pages

GitHub Pages solo sirve sitios **estáticos**, por lo que no puede ejecutar Flask. Se usa para publicar la documentación del proyecto (`docs/index.html` o este README con capturas); la API se ejecuta de forma local siguiendo las instrucciones de arriba.

Activación: *Settings → Pages → Source: Deploy from a branch → `main` / carpeta `/docs`*.

## Respuestas conceptuales

### ¿Por qué hashear contraseñas?
- **Evita guardar secretos en texto plano.** Si la base de datos se filtra, el atacante no obtiene las contraseñas reales, solo hashes.
- **El hash es de una sola vía.** No se puede "desencriptar"; para validar se hashea lo que ingresa el usuario y se compara.
- **Protege a los usuarios que reutilizan contraseñas** en otros sitios.
- **Salt:** `generate_password_hash` agrega un valor aleatorio por contraseña, de modo que dos usuarios con la misma clave tienen hashes distintos y se frustran los ataques con tablas precalculadas (*rainbow tables*).
- **Costo computacional:** algoritmos como scrypt/PBKDF2 son deliberadamente lentos, lo que encarece los ataques de fuerza bruta.
- Incluso los administradores del sistema no pueden ver las contraseñas.

### Ventajas de usar SQLite en este proyecto
- **Sin servidor:** es una base embebida; no hay que instalar ni configurar nada.
- **Un solo archivo (`tareas.db`):** fácil de copiar, respaldar y versionar.
- **Incluida en Python** (`sqlite3`), sin dependencias extra.
- **Persistente:** los datos sobreviven al reinicio del servidor.
- **SQL estándar y transacciones ACID**, con restricciones como `UNIQUE` para evitar usuarios duplicados.
- **Ideal para prototipos y proyectos pequeños** con pocos usuarios concurrentes.
- *Limitación:* para muchos accesos simultáneos de escritura conviene migrar a PostgreSQL/MySQL.
