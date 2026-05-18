# Nandetuiter

Clon de Twitter educativo. Backend **Django + DRF**, frontend **Angular 18**, base **SQLite** en dev.

---

## Stack

- **Backend**: Django 5.2, Django REST Framework, SimpleJWT, django-constance
- **Frontend**: Angular 18 (standalone components, signals, SCSS)
- **Base de datos**: SQLite en dev, PostgreSQL 16 en prod
- **Sin Docker en dev** — corre todo nativo

## Estructura

```
nandetuiter/
├── apps/
│   ├── accounts/   # User custom, JWT, perfil, follows
│   ├── posts/      # Posts, likes, feed
│   └── core/       # Config dinámica (constance), middleware, /api/config/
├── nandetuiter/
│   └── settings/   # base.py, dev.py (SQLite), prod.py (Postgres)
├── frontend/       # App Angular 18 (vista Home consume /api/config/)
├── manage.py
├── requirements.txt
└── db.sqlite3      # Se crea al correr migrate
```

---

## Requisitos previos

Instalá estas herramientas en tu máquina:

1. **Git** → https://git-scm.com/downloads
2. **Python 3.12+** → https://www.python.org/downloads/
   - Windows: marcá **"Add Python to PATH"** durante la instalación.
3. **Node.js 20+ LTS** → https://nodejs.org/

Verificá las versiones:

```bash
git --version
python --version    # Windows: python --version | Linux/macOS: python3 --version
node --version
npm --version
```

---

## Setup paso a paso

### 1. Cloná el repositorio

```bash
git clone <URL-del-repo>
cd nandetuiter
```

### 2. Creá el archivo `.env`

```bash
# Linux / macOS
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

El `.env` por defecto ya sirve para correr en local. Si querés un `SECRET_KEY` propio:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Y pegá el resultado en la línea `SECRET_KEY=` del `.env`.

### 3. Backend — crear y activar virtualenv

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea el script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

> Cuando el venv esté activo vas a ver `(venv)` al principio de tu prompt.

### 4. Instalar dependencias Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Migrar la base SQLite

```bash
python manage.py migrate
```

Esto crea `db.sqlite3` en la raíz.

### 6. Crear superusuario

**Opción A — interactiva (recomendado):**

```bash
python manage.py createsuperuser
```

Seguí los prompts (email, password).

**Opción B — usar el superuser de dev ya creado:**

| Campo    | Valor                     |
|----------|---------------------------|
| username | `admin`                   |
| email    | `admin@nandetuiter.local` |
| password | `admin12345`              |

Si no existe, recrealo con:

```bash
python manage.py shell -c "from apps.accounts.models import User; u,_=User.objects.get_or_create(username='admin', defaults={'email':'admin@nandetuiter.local'}); u.is_staff=True; u.is_superuser=True; u.set_password('admin12345'); u.save()"
```

> Estas credenciales son solo para dev local. Nunca usar en prod.

### 7. Levantar el backend

```bash
python manage.py runserver
```

Backend escuchando en **http://localhost:8000**. Dejá esa terminal abierta.

### 8. Frontend — abrir OTRA terminal

```bash
cd frontend
npm install
```

(la primera vez tarda unos minutos)

### 9. Levantar el frontend

```bash
npm start
```

Si el puerto 4200 está ocupado:

```bash
npm start -- --port 4201
```

Frontend en **http://localhost:4200** (o el puerto que elegiste).

### 10. Abrí la app

| Servicio              | URL                                         |
|-----------------------|---------------------------------------------|
| Frontend Angular      | http://localhost:4200                       |
| Backend (API root)    | http://localhost:8000                       |
| Admin Django          | http://localhost:8000/admin/                |
| Endpoint de config    | http://localhost:8000/api/config/           |

La vista Home (`/`) del frontend hace `GET /api/config/` y muestra `SITE_NAME`, `POST_MAX_CHARS`, `POSTS_PER_PAGE`.

---

## Flujo diario

Cada vez que abrís el proyecto:

**Terminal 1 — backend:**

```bash
# Windows
.\venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate

python manage.py runserver
```

**Terminal 2 — frontend:**

```bash
cd frontend
npm start
```

---

## Comandos comunes

### Backend

```bash
# Crear migración después de tocar models.py
python manage.py makemigrations
python manage.py migrate

# Shell de Django
python manage.py shell

# Tests
python manage.py test

# Instalar paquete y persistirlo
pip install <paquete>
pip freeze > requirements.txt
```

### Frontend

```bash
# Generar componente
npx ng generate component pages/feed --standalone

# Generar servicio
npx ng generate service services/api

# Build producción
npx ng build

# Tests
npx ng test
```

---

## Solución de problemas

**`python` no encontrado en Windows**
Reinstalá Python marcando "Add Python to PATH" o usá `py` en vez de `python`.

**`.\venv\Scripts\Activate.ps1` bloqueado**
Corré `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y reabrí PowerShell.

**`ModuleNotFoundError: No module named 'django'`**
Olvidaste activar el venv. Mirá si tu prompt empieza con `(venv)`.

**Puerto 8000 o 4200 ocupado**
Backend: `python manage.py runserver 8001`. Frontend: `npm start -- --port 4201`.

Para matar lo que esté usando el puerto en Windows:

```powershell
netstat -ano | findstr :4200
taskkill /PID <PID> /F
```

**`npm error could not determine executable to run`**
Estás corriendo `npm`/`npx` desde la raíz del repo. Tenés que estar en `frontend/`. Hacé `cd frontend` primero.

**Frontend muestra "Backend no disponible"**
El backend no está corriendo. Levantalo en la Terminal 1.

**CORS error en la consola del navegador**
Confirmá que `DJANGO_SETTINGS_MODULE=nandetuiter.settings.dev` en `.env` (dev permite todos los orígenes).

**Reset total de la base SQLite**
Borrá `db.sqlite3` y corré `python manage.py migrate` + `createsuperuser` de nuevo.

---

## Configuración dinámica (django-constance)

Variables editables desde `/admin/constance/config/` sin reiniciar:

| Key                | Default       | Descripción                                  |
|--------------------|---------------|----------------------------------------------|
| `SITE_NAME`        | "Nandetuiter" | Nombre mostrado en el frontend               |
| `POST_MAX_CHARS`   | 280           | Límite de caracteres por post                |
| `POSTS_PER_PAGE`   | 20            | Tamaño de página del feed                    |
| `MAINTENANCE_MODE` | False         | Bloquea la app a usuarios no-staff (503)     |

El frontend lee `SITE_NAME`, `POST_MAX_CHARS` y `POSTS_PER_PAGE` desde `GET /api/config/`.

---

## Decisiones de diseño

- **SQLite en dev / Postgres en prod**: arranque rápido sin instalar servicios. Prod usa Postgres para constraints + concurrencia reales.
- **JWT (no sessions)**: stateless, encaja con SPA Angular separada del backend.
- **django-constance**: cambiar límites o activar mantenimiento sin redeployar.
- **Custom User desde día 0**: cambiarlo después rompe migraciones (irreversible).
- **Apps bajo `apps/`**: ordena el repo cuando crece.
- **Angular standalone + signals**: sin NgModules, menos boilerplate, idiomático en Angular 18.

---

## Equipo

- **Dev A (Luis)**: backend lead (accounts, posts, core, settings, infra).
- **Dev B**: frontend Angular (auth UI, feed, perfil, composer).
- **Dev C**: backend de soporte (endpoints aislados, tests, seed).

Más docs:
- `TAREAS.md` — asignación día por día.
- `BITACORA.md` — log de decisiones técnicas.
- `CONTRIBUTING.md` — flujo de ramas y reglas de PR.
- `ARQUITECTURA.md` — diagrama de capas y datos.
