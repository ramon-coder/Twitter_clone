# API de Sistema de Gestión de Suscripciones y Pagos Recurrentes

API RESTful para la gestión de suscripciones y pagos recurrentes, desarrollada con FastAPI.

## Características

- **Gestión de Usuarios**: Registro, autenticación y perfil de usuarios
- **Planes de Suscripción**: Creación, edición y consulta de planes
- **Suscripciones**: Administración del ciclo de vida de las suscripciones
- **Pagos Recurrentes**: Integración con Stripe para procesamiento de pagos
- **Notificaciones**: Envío de emails con SendGrid
- **Webhooks**: Manejo de eventos de Stripe
- **Tareas Programadas**: Verificación automática de suscripciones vencidas
- **Autenticación**: OAuth2 con JWT

## Tecnologías Utilizadas

- **FastAPI**: Framework web para APIs rápidas y modernas
- **SQLAlchemy**: ORM para interactuar con la base de datos
- **SQLite**: Base de datos relacional (configurable)
- **Stripe**: Pasarela de pagos
- **SendGrid**: Servicio de envío de emails
- **APScheduler**: Programador de tareas
- **Docker**: Contenerización
- **pytest**: Framework de pruebas

## Requisitos Previos

- Python 3.9+
- Docker y Docker Compose (opcional)
- Cuenta en Stripe para pruebas
- Cuenta en SendGrid para envío de emails

## Instalación y Ejecución

### 1. Clonar el Repositorio

```bash
git clone [URL_DEL_REPOSITORIO]
cd "API de Sistema de Gestión de Suscripciones y Pagos Recurrentes"
```

### 2. Crear el Archivo .env

Duplicar el archivo `.env.example` (si existe) o crear un nuevo archivo `.env` con las siguientes variables:

```env
SECRET_KEY=tu-clave-secreta
DATABASE_URL=sqlite:///./subscriptions.db
STRIPE_API_KEY=tu-clave-api-stripe
STRIPE_WEBHOOK_SECRET=tu-secreto-webhook-stripe
SENDGRID_API_KEY=tu-clave-api-sendgrid
EMAIL_SENDER=no-reply@tu-dominio.com
ADMIN_EMAIL=admin@tu-dominio.com
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`.

### 5. Acceder a la Documentación

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Ejecución con Docker

```bash
docker-compose up -d
```

## Pruebas

```bash
pytest
```

## Estructura del Proyecto

```
.
├── main.py              # Archivo principal de la aplicación
├── models/              # Definición de modelos de datos
├── routers/             # Rutas de la API
├── services/            # Servicios y lógica de negocio
├── tests/               # Pruebas unitarias
├── .env                 # Variables de entorno
├── requirements.txt     # Dependencias del proyecto
├── Dockerfile           # Archivo de configuración Docker
└── docker-compose.yml   # Compose para desarrollo
```

## Endpoints Principales

### Autenticación

- `POST /token` - Obtener token de acceso
- `POST /register` - Registrar nuevo usuario

### Usuarios

- `GET /users/me` - Obtener perfil del usuario actual
- `PUT /users/me` - Actualizar perfil del usuario
- `DELETE /users/me` - Eliminar usuario

### Planes

- `GET /plans` - Obtener lista de planes
- `GET /plans/{plan_id}` - Obtener detalles de un plan
- `POST /plans` - Crear un nuevo plan
- `PUT /plans/{plan_id}` - Actualizar un plan
- `DELETE /plans/{plan_id}` - Eliminar un plan

### Suscripciones

- `GET /subscriptions` - Obtener suscripciones del usuario
- `POST /subscriptions` - Crear una suscripción
- `PUT /subscriptions/{subscription_id}` - Actualizar una suscripción
- `DELETE /subscriptions/{subscription_id}` - Cancelar una suscripción
- `POST /subscriptions/{subscription_id}/pause` - Pausar suscripción
- `POST /subscriptions/{subscription_id}/resume` - Reanudar suscripción

### Pagos

- `GET /payments` - Obtener historial de pagos
- `GET /payments/{payment_id}` - Obtener detalles de un pago
- `POST /payments/{subscription_id}` - Realizar un pago

## Contribuciones

1. Fork el repositorio
2. Crear una rama para la funcionalidad (`git checkout -b feature/funcionalidad`)
3. Realizar los cambios y commit (`git commit -m "Agrega funcionalidad"`)
4. Push a la rama (`git push origin feature/funcionalidad`)
5. Crear un Pull Request

## Licencia

[MIT License](LICENSE)
