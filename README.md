## Backend Empresarial con FastAPI

Base profesional para un backend modular en Python, organizada con una
estructura inspirada en Spring Boot y preparada para escalar por capas.

### Objetivos de la base

- Separación clara entre `routers`, `services`, `repositories`, `models`, `schemas`, `config` y `utils`.
- Punto de entrada funcional con FastAPI.
- Integración con Supabase Auth usando JWT emitido por Supabase.
- Estructura preparada para PostgreSQL y autenticación JWT futura.
- Código base pensado para clean architecture y mantenimiento a largo plazo.

### Estructura

```text
app/
├── config/
├── models/
├── repositories/
├── routers/
├── schemas/
├── services/
└── utils/
```

### Requisitos

- Python 3.11 o superior recomendado.
- Dependencias instaladas desde `requirements.txt`.

### Configuración

1. Copia `.env.example` a `.env`.
2. Completa `SUPABASE_URL` y `SUPABASE_KEY`.
3. Ajusta `DATABASE_URL` y los secretos JWT cuando correspondan.

### Instalación

```bash
pip install -r requirements.txt
```

### Ejecución

```bash
uvicorn app.main:app --reload
```

### Endpoints iniciales

- `GET /` valida que la API está levantada.
- `GET /api/v1/health` devuelve el estado del servicio.
- `POST /auth/register` registra un usuario con Supabase Auth.
- `POST /auth/login` autentica y devuelve el JWT emitido por Supabase.
- `GET /users` lista usuarios desde Supabase PostgreSQL.
- `GET /users/{id}` consulta un usuario por identificador.
- `PUT /users/{id}` actualiza un usuario completo.
- `DELETE /users/{id}` elimina un usuario.

### Notas de arquitectura

- `routers` expone la API HTTP.
- `services` contiene la lógica del negocio.
- `repositories` abstrae el acceso a datos.
- `models` representa el dominio.
- `schemas` define contratos de entrada y salida.
- `config` centraliza configuración, Supabase y seguridad.
- `utils` concentra utilidades compartidas.

### Autenticación

- `app/routers/auth_router.py` expone el contrato público de autenticación.
- `app/services/auth_service.py` maneja las reglas del caso de uso.
- `app/repositories/auth_repository.py` encapsula las llamadas a Supabase Auth.
- `app/config/security.py` prepara utilidades de seguridad y JWT para futuras rutas protegidas.

### Usuarios

- `app/routers/users_router.py` expone el CRUD básico de usuarios.
- `app/services/user_service.py` resuelve las reglas del caso de uso.
- `app/repositories/user_repository.py` consulta la tabla `users` en Supabase PostgreSQL.
- `app/models/user.py` define la entidad de dominio y los roles `admin` y `customer`.
- `app/schemas/user.py` valida nombres, emails, roles y respuestas públicas.

### Tabla esperada en Supabase

El módulo asume una tabla `users` con columnas similares a:

- `id` UUID
- `name` text
- `email` text
- `role` text
- `is_active` boolean
- `created_at` timestamptz
- `updated_at` timestamptz



