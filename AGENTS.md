# AGENTS.md

## Proyecto

Sistema Web para la Gestión y Trazabilidad de RAEE — Huancayo, Junín (Perú).
Backend en **Python + FastAPI** conectado a **PostgreSQL (Supabase)**.

## Arquitectura y Flujo Estricto

Estructura obligatoria dentro de `backend/src/backend/`:

- `main.py`: Instancia FastAPI, configuración CORS (`http://localhost:4200`), manejadores globales de excepciones y registro de routers.
- `config.py`: Carga variables desde `.env` (`DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRACION_MINUTOS`, `CORS_ORIGINS`). Falla al iniciar si falta `DATABASE_URL` o `JWT_SECRET` (< 32 chars).
- `database.py`: Gestión de conexiones a PostgreSQL usando `psycopg` (`dict_row`, `autocommit=True`). Sin ORM ni SQLAlchemy.
- `errors.py`: Excepciones de dominio (`NoEncontradoError`, `ConflictoNegocioError`, `NoAutorizadoError`, `ProhibidoError`) mapeadas en `main.py` a HTTP 404, 409, 401 y 403.
- `security.py`: Hash de contraseñas con `argon2-cffi` (`PasswordHasher`), tokens JWT HS256 (`pyjwt`) y dependencias FastAPI (`get_usuario_actual`, `requerir_roles(...)`).
- `apis/`: Routers HTTP (`/api/...`). Validan schemas, inyectan usuario autenticado y llaman a `services/`. Nunca llaman a `repositories/`.
- `services/`: Lógica de negocio y orquestación.
- `repositories/`: Invocan exclusivamente las funciones almacenadas `fn_*` de PostgreSQL mediante `SELECT * FROM fn_nombre(%s, ...)`. No escriben SQL directo sobre tablas ni nombres de tablas en Python. Capturan `psycopg.Error` y traducen prefijos (`NO_ENCONTRADO:`, `CONFLICTO:`, `PROHIBIDO:`) a excepciones de `errors.py`.
- `schemas/`: Modelos Pydantic v2 (`request` y `response`).

Flujo unidireccional obligatorio: `main.py -> apis -> services -> repositories`.

## Comandos (ejecutar dentro de `backend/`)

- `uv sync` — instala/actualiza dependencias.
- `uv run uvicorn src.backend.main:app` — único comando de inicio de la API en `http://localhost:8000` (Swagger en `/docs`). Sin `--reload`: tras cambiar código se debe reiniciar el servidor manualmente.
- `uv run python <archivo>` — ejecutar scripts dentro del entorno virtual.

## Funciones Almacenadas Disponibles en Supabase (PostgreSQL)

Todas las transacciones e inserciones en `historial_trazabilidad` ya están resueltas dentro de estas funciones:

- **Seguridad y Usuarios:**
  - `fn_usuario_obtener_sesion(p_correo)` -> `(id_usuario, nombres, apellidos, correo, password_hash, rol, id_centro, activo)`
  - `fn_usuario_registrar(p_nombres, p_apellidos, p_correo, p_password_hash, p_telefono, p_rol, p_ubigeo, p_direccion, p_id_centro)` -> `(id_usuario, correo, rol)`
  - `fn_usuarios_listar()` -> `(id_usuario, nombres, apellidos, correo, telefono, rol, distrito, nombre_centro, activo, fecha_registro)`
  - `fn_usuario_cambiar_estado(p_id_usuario, p_activo)` -> `boolean`
- **Catálogos y Centros:**
  - `fn_catalogos_distritos()` -> `(ubigeo, distrito, provincia)`
  - `fn_catalogos_categorias()` -> `(id_categoria, nombre, descripcion)`
  - `fn_catalogos_tipos_destino()` -> `(id_tipo_destino, nombre, descripcion, es_valorizacion)`
  - `fn_centros_listar(p_solo_activos)` -> `(id_centro, nombre_centro, direccion, telefono, ubigeo, distrito, latitud, longitud, activo)`
  - `fn_centro_crear(p_nombre_centro, p_direccion, p_telefono, p_ubigeo, p_latitud, p_longitud)` -> `int`
  - `fn_centro_cambiar_estado(p_id_centro, p_activo)` -> `boolean`
- **Dispositivos y Solicitudes (Ciudadano):**
  - `fn_raee_registrar(p_id_usuario, p_id_categoria, p_marca, p_modelo, p_descripcion)` -> `(id_raee, codigo_seguimiento)`
  - `fn_raee_listar_por_usuario(p_id_usuario)` -> `(id_raee, codigo_seguimiento, categoria, marca, modelo, descripcion, fecha_registro, estado_actual, destino_final, peso_kg)`
  - `fn_solicitud_crear(p_id_raee, p_id_usuario, p_id_centro, p_tipo_solicitud, p_fecha_programada)` -> `int`
  - `fn_solicitud_cancelar(p_id_solicitud, p_id_usuario)` -> `boolean`
- **Recepción y Evaluación (Encargado):**
  - `fn_solicitudes_listar_por_centro(p_id_centro, p_estado)` -> `(id_solicitud, id_raee, codigo_seguimiento, categoria, marca, modelo, ciudadano, telefono_ciudadano, direccion_ciudadano, tipo_solicitud, fecha_programada, estado_solicitud, estado_raee_actual)`
  - `fn_solicitud_recepcionar(p_id_solicitud, p_id_encargado)` -> `boolean`
  - `fn_evaluacion_registrar(p_id_raee, p_id_evaluador, p_id_tipo_destino, p_condicion_fisica, p_es_operativo, p_peso_kg, p_observaciones)` -> `int`
- **Público y Reportes:**
  - `fn_publico_obtener_raee(p_codigo_seguimiento)` -> `(id_raee, codigo_seguimiento, categoria, marca, modelo, descripcion, fecha_registro, estado_actual, destino_final, es_valorizacion, peso_kg)`
  - `fn_publico_historial_raee(p_codigo_seguimiento)` -> `(id_historial, estado_anterior, estado_nuevo, comentario, fecha_cambio)`
  - `fn_reportes_resumen()` -> `(total_dispositivos, total_registrados, total_solicitados, total_recibidos, total_evaluados, peso_total_kg, peso_valorizado_kg, peso_disposicion_final_kg)`

## Reglas de Negocio y Seguridad

- `POST /api/auth/login` usa `OAuth2PasswordRequestForm` (`username` = correo, `password`). Nunca exponer `password_hash`.
- `id_usuario`, `id_evaluador` e `id_encargado` nunca viajan en el body JSON; siempre se extraen del usuario autenticado por el token JWT.
- Los `Decimal` (`peso_kg`, `latitud`, `longitud`) se manejan con Pydantic v2.
