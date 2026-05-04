# API de Sistema de Gestión de Suscripciones y Pagos Recurrentes

API RESTful para la gestión de suscripciones y pagos recurrentes, desarrollada con FastAPI.

## 🚀 Características

- **Gestión de Usuarios**: Registro, autenticación y perfil de usuarios
- **Planes de Suscripción**: Creación, edición y consulta de planes
- **Suscripciones**: Administración del ciclo de vida de las suscripciones
- **Pagos Recurrentes**: Integración con Stripe para procesamiento de pagos
- **Webhooks**: Manejo de eventos de Stripe, PayPal y Mercado Pago
- **Notificaciones por Email**: Envío de emails con SendGrid
- **Tareas Programadas**: Verificación automática de suscripciones vencidas
- **Autenticación Segura**: OAuth2 con JWT
- **Rate Limiting**: Protección contra ataques de fuerza bruta
- **Logging**: Sistema completo de logs
- **Migraciones**: Base de datos con Alembic

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web para APIs rápidas y modernas
- **SQLAlchemy**: ORM para interactuar con la base de datos
- **PostgreSQL/SQLite**: Bases de datos soportadas
- **Stripe**: Pasarela de pagos
- **SendGrid**: Servicio de envío de emails
- **APScheduler**: Programador de tareas
- **Alembic**: Migraciones de base de datos
- **Docker**: Contenerización
- **pytest**: Framework de pruebas

## 📋 Requisitos Previos

- Python 3.9+
- Docker y Docker Compose (opcional)
- Cuenta en Stripe para pruebas
- Cuenta en SendGrid para envío de emails
- PostgreSQL (para producción)

## 🔧 Instalación y Ejecución

### 1. Clonar el Repositorio

```bash
git clone [URL_DEL_REPOSITORIO]
cd "API de Sistema de Gestión de Suscripciones y Pagos Recurrentes"
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus valores:

```env
# Application
SECRET_KEY=tu-clave-secreta-muy-larga-minimo-32-caracteres
APP_ENV=development
DEBUG=True

# Database (SQLite para desarrollo)
DATABASE_URL=sqlite:///./subscriptions.db

# Para PostgreSQL en producción:
# DATABASE_URL=postgresql://user:password@localhost/subscriptions_db

# Stripe Configuration
STRIPE_API_KEY=sk_test_tu_api_key_stripe
STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret
STRIPE_PUBLISHABLE_KEY=pk_test_tu_publishable_key

# SendGrid Configuration
SENDGRID_API_KEY=SG.tu_api_key_sendgrid
EMAIL_SENDER=no-reply@tudominio.com
ADMIN_EMAIL=admin@tudominio.com

# Rate Limiting
AUTH_RATE_LIMIT=5
AUTH_RATE_WINDOW=60

# Scheduler
SCHEDULER_ENABLED=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Inicializar Base de Datos

```bash
# Crear tablas (automático en primer inicio)
python main.py

# O usar migraciones de Alembic:
alembic upgrade head

# Para desarrollo, poblar con datos de prueba:
python seed.py
```

### 5. Ejecutar la Aplicación

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## 🐳 Ejecución con Docker

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Detener
docker-compose down
```

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Con coverage
pytest --cov=.

# Solo pruebas unitarias
pytest -m unit

# Con reporte HTML
pytest --cov=. --cov-report=html
```

## 🗄️ Estructura del Proyecto

```
.
├── main.py                    # Archivo principal de la aplicación
├── routers/                   # Rutas de la API (FastAPI)
│   ├── auth.py
│   ├── plans.py
│   ├── users.py
│   ├── subscriptions.py
│   ├── payments.py
│   └── webhooks.py
├── models/                    # Modelos de datos SQLAlchemy (por archivo)
│   ├── __init__.py
│   ├── user.py
│   ├── plan.py
│   ├── subscription.py
│   ├── payment.py
│   └── invoice.py
├── services/                  # Lógica de negocio
│   ├── payment_service.py
│   ├── email_service.py
│   └── scheduled_tasks.py
├── middleware/                # Middleware personalizado
│   └── rate_limit.py
├── tests/                     # Pruebas unitarias e integración
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_plans.py
│   └── test_subscriptions.py
├── alembic/                   # Migraciones de base de datos
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── .env.example               # Variables de entorno de ejemplo
├── .env                       # Variables de entorno (NO versionado)
├── requirements.txt           # Dependencias del proyecto
├── Dockerfile                 # Configuración Docker
├── docker-compose.yml         # Compose para desarrollo
├── pytest.ini                 # Configuración de pruebas
└── README.md                  # Documentación
```

## 📡 Endpoints Principales

### Autenticación

- `POST /token` - Obtener token de acceso (rate limited)
- `POST /register` - Registrar nuevo usuario (rate limited)
- `GET /users/me` - Obtener perfil del usuario actual

### Usuarios (requiere autenticación)

- `GET /users/me` - Obtener perfil del usuario actual
- `PUT /users/me` - Actualizar perfil del usuario
- `DELETE /users/me` - Eliminar usuario

### Planes (requiere autenticación)

- `GET /plans` - Obtener lista de planes
- `GET /plans/{plan_id}` - Obtener detalles de un plan
- `POST /plans` - Crear un nuevo plan (solo admin)
- `PUT /plans/{plan_id}` - Actualizar un plan (solo admin)
- `DELETE /plans/{plan_id}` - Eliminar un plan (solo admin)

### Suscripciones (requiere autenticación)

- `GET /subscriptions` - Obtener suscripciones del usuario
- `GET /subscriptions/{subscription_id}` - Obtener detalles de una suscripción
- `POST /subscriptions` - Crear una suscripción
- `PUT /subscriptions/{subscription_id}` - Actualizar una suscripción
- `PUT /subscriptions/{subscription_id}/cancel` - Cancelar una suscripción
- `PUT /subscriptions/{subscription_id}/renew` - Renovar una suscripción

### Pagos (requiere autenticación)

- `GET /payments` - Obtener historial de pagos
- `GET /payments/{payment_id}` - Obtener detalles de un pago
- `POST /payments/{subscription_id}` - Realizar un pago

### Webhooks (no requieren autenticación)

- `POST /webhooks/stripe` - Webhook de Stripe
- `POST /webhooks/paypal` - Webhook de PayPal
- `POST /webhooks/mercado_pago` - Webhook de Mercado Pago
- `GET /webhooks/health` - Health check de webhooks

## ⚙️ Configuración de Producción

### Variables de Entorno Requeridas

```env
APP_ENV=production
DEBUG=False
SECRET_KEY=<clave-secreta-muy-segura-min-32-caracteres>
DATABASE_URL=postgresql://user:password@db/subscriptions_db
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...
SENDGRID_API_KEY=SG.live_...
EMAIL_SENDER=no-reply@tudominio.com
ADMIN_EMAIL=admin@tudominio.com
```

### Configuraciones de Seguridad

- ✅ SECRET_KEY debe ser único y de al menos 32 caracteres
- ✅ Usar PostgreSQL en producción
- ✅ Configurar CORS con dominios específicos
- ✅ Habilitar rate limiting
- ✅ Deshabilitar DEBUG
- ✅ Usar HTTPS
- ✅ Configurar logging a archivo

### Despliegue con Docker

```bash
# Construir imagen de producción
docker build -t subscription-api .

# Ejecutar con docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🗃️ Migraciones de Base de Datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción de cambios"

# Aplicar migraciones
alembic upgrade head

# Ver historial
alembic history

# Rollback a versión anterior
alembic downgrade -1
```

## 🔍 Logging

Los logs se escriben en consola y archivo (`app.log` por defecto):

```
2024-01-15 10:30:00 - INFO - Application started in production mode
2024-01-15 10:30:05 - WARNING - HTTP 401: Could not validate credentials - Path: /token
2024-01-15 10:30:10 - ERROR - Failed to process payment: ...
```

Niveles de log: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## 🛡️ Rate Limiting

Los endpoints de autenticación están limitados a `5 intentos por minuto` por defecto (configurable).

Cabeceras de respuesta:
- `X-RateLimit-Remaining`: Intentos restantes
- `X-RateLimit-Window`: Ventana de tiempo en segundos

## 🧩 Tareas Programadas

El sistema ejecuta automáticamente:

- **Recordatorios de renovación**: Diario a las 8:00 AM
- **Verificación de suscripciones vencidas**: Diario a las 2:00 AM
- **Verificación de pagos atrasados**: Diario a las 10:00 AM
- **Reporte mensual**: Primer día de cada mes a las 3:00 AM

Nota: En desarrollo las tareas están deshabilitadas por defecto.

## 🤝 Contribuciones

1. Fork el repositorio
2. Crear una rama para la funcionalidad (`git checkout -b feature/funcionalidad`)
3. Realizar los cambios y commit (`git commit -m "Agrega funcionalidad"`)
4. Push a la rama (`git push origin feature/funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

[MIT License](LICENSE)
