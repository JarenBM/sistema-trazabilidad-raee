# Backend — Sistema de Gestión y Trazabilidad de RAEE

API en **Python + FastAPI** conectada a **PostgreSQL (Supabase)**.
Documentación interactiva en `http://localhost:8000/docs`.

## Requisitos

- [uv](https://docs.astral.sh/uv/)
- Python 3.12 (gestionado automáticamente por uv según `.python-version`)
- Variables de entorno definidas en `backend/.env` (ver `.env.example`)

## Comandos

```powershell
cd backend
uv sync
uv run uvicorn src.backend.main:app
```

El servidor queda disponible en `http://localhost:8000`.
Tras modificar el código se debe reiniciar el servidor manualmente.

### Pruebas

```powershell
cd backend
uv run pytest -q
```

Las pruebas de humo son offline: no abren conexión a Supabase.

## Estructura

```
src/backend/
├── main.py          # Instancia FastAPI, CORS y manejadores de errores
├── config.py        # Variables de entorno validadas
├── database.py      # Conexiones psycopg (dict_row, autocommit)
├── errors.py        # Excepciones de dominio
├── security.py      # Argon2id, JWT HS256 y dependencias de rol
├── apis/            # Routers HTTP
├── services/        # Lógica de negocio
├── repositories/    # Funciones almacenadas fn_* de PostgreSQL
└── schemas/         # Modelos Pydantic v2
```

Flujo unidireccional: `main.py -> apis -> services -> repositories`.

## Endpoints

| Método | Ruta | Rol |
|---|---|---|
| GET | `/api/health` | Público |
| POST | `/api/auth/registro` | Público |
| POST | `/api/auth/login` | Público |
| GET | `/api/auth/me` | Autenticado |
| GET | `/api/usuarios` | ADMIN |
| POST | `/api/usuarios/encargado` | ADMIN |
| PATCH | `/api/usuarios/{id_usuario}/estado` | ADMIN |
| GET | `/api/catalogos/distritos` | Público |
| GET | `/api/catalogos/categorias` | Público |
| GET | `/api/catalogos/tipos-destino` | Público |
| GET | `/api/catalogos/centros` | Público |
| POST | `/api/centros` | ADMIN |
| PATCH | `/api/centros/{id_centro}/estado` | ADMIN |
| GET | `/api/publico/rastreo/{codigo_seguimiento}` | Público |
| POST | `/api/raee` | CIUDADANO |
| GET | `/api/raee/mios` | CIUDADANO |
| POST | `/api/solicitudes` | CIUDADANO |
| PATCH | `/api/solicitudes/{id_solicitud}/cancelar` | CIUDADANO |
| GET | `/api/solicitudes/centro` | ENCARGADO |
| PATCH | `/api/solicitudes/{id_solicitud}/recepcionar` | ENCARGADO |
| POST | `/api/evaluaciones` | ENCARGADO |
| GET | `/api/reportes/resumen` | ADMIN |

## Códigos de error

| Excepción | HTTP |
|---|---|
| `NoEncontradoError` | 404 |
| `ConflictoNegocioError` | 409 |
| `NoAutorizadoError` | 401 |
| `ProhibidoError` | 403 |
| `psycopg.Error` | 503 |

Los repositorios traducen los prefijos `NO_ENCONTRADO:`, `CONFLICTO:` y
`PROHIBIDO:` lanzados por las funciones almacenadas.
