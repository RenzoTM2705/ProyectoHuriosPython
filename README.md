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
- `GET /products` lista productos desde Supabase PostgreSQL.
- `GET /products/{id}` consulta un producto por identificador.
- `POST /products` crea un producto nuevo.
- `PUT /products/{id}` actualiza un producto completo.
- `DELETE /products/{id}` elimina un producto.
- `POST /orders` crea un pedido y calcula el total automáticamente.
- `GET /orders` lista pedidos con sus detalles.
- `GET /orders/{id}` consulta un pedido por identificador.

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

### Productos

- `app/routers/products_router.py` expone el CRUD de productos.
- `app/services/product_service.py` maneja las reglas del caso de uso.
- `app/repositories/product_repository.py` consulta la tabla `products` en Supabase PostgreSQL.
- `app/models/product.py` define la entidad de dominio del producto.
- `app/schemas/product.py` valida precio positivo, stock válido y campos requeridos.

### Pedidos

- `app/routers/orders_router.py` expone el flujo público de pedidos.
- `app/services/order_service.py` valida stock, calcula totales y maneja compensación de fallos.
- `app/repositories/order_repository.py` persiste pedidos y detalles en Supabase PostgreSQL.
- `app/models/order.py` define las entidades `Order` y `OrderDetail`.
- `app/schemas/order.py` valida usuario, productos, cantidades y estructura de respuesta.

### Tabla esperada en Supabase

El módulo asume tablas `orders` y `order_details` con columnas similares a:

- `orders.id` UUID
- `orders.user_id` UUID
- `orders.total` numeric
- `orders.status` text
- `orders.created_at` timestamptz
- `orders.updated_at` timestamptz
- `order_details.id` UUID
- `order_details.order_id` UUID
- `order_details.product_id` UUID
- `order_details.product_name` text
- `order_details.quantity` integer
- `order_details.unit_price` numeric
- `order_details.subtotal` numeric

### Tabla esperada en Supabase

El módulo asume una tabla `products` con columnas similares a:

- `id` UUID
- `name` text
- `description` text
- `price` numeric
- `stock` integer
- `sku` text
- `status` text
- `created_at` timestamptz
- `updated_at` timestamptz

El módulo de usuarios mantiene su propia definición de tabla en la sección anterior.



