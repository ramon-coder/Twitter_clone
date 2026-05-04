# Sistema Completo de Gestión de Suscripciones y Pagos Recurrentes

Este proyecto contiene tanto el frontend como el backend de un sistema completo para la gestión de suscripciones y pagos recurrentes.

## Estructura del Proyecto

```
Sistema de Suscripciones Completo/
├── backend/                  # API RESTful desarrollada con FastAPI
│   ├── main.py              # Archivo principal de la aplicación
│   ├── routers/             # Rutas de la API (FastAPI)
│   ├── models/              # Modelos de datos SQLAlchemy
│   ├── services/            # Lógica de negocio
│   ├── middleware/          # Middleware personalizado
│   ├── tests/               # Pruebas unitarias e integración
│   ├── alembic/             # Migraciones de base de datos
│   ├── Dockerfile           # Configuración Docker
│   ├── docker-compose.yml   # Compose para desarrollo
│   └── README.md            # Documentación detallada del backend
│
└── frontend/                # Interfaz de usuario web
    ├── static/
    │   ├── index.html       # Página principal
    │   ├── css/
    │   │   └── styles.css   # Estilos personalizados
    │   └── js/
    │       └── app.js       # Lógica de la aplicación frontend
    └── README.md            # Esta documentación
```

## Características

### Backend (FastAPI)
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

### Frontend (Interfaz Web)
- Dashboard interactivo
- Gestión de planes de suscripción
- Visualización y gestión de suscripciones
- Historial de pagos
- Perfil de usuario
- Diseño responsivo con Bootstrap

## 🚀 Inicio Rápido

### Opción 1: Ejecutar todo junto (recomendado para desarrollo)
```bash
# Desde la raíz del proyecto
run_all.bat
```
Esto iniciará:
- Backend en http://localhost:8000
- Frontend en http://localhost:3000
- Documentación API en http://localhost:8000/docs

### Opción 2: Ejecutar por separado
```bash
# Solo backend
run_backend.bat

# Solo frontend (en otra terminal)
run_frontend.bat
```

## 📋 Requisitos Previos

- Python 3.9+
- Cuenta en Stripe para pruebas
- Cuenta en SendGrid para envío de emails
- PostgreSQL (opcional, por defecto usa SQLite)

## 🔧 Configuración

1. Copiar las variables de entorno:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Editar `backend/.env` con tus valores de configuración:
   - Claves de API de Stripe
   - Clave de API de SendGrid
   - Otras configuraciones según necesites

3. Instalar dependencias del backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## 📖 Documentación Detallada

- [Documentación del Backend](backend/README.md)
- [Documentación del Frontend](frontend/README.md)

## 🐳 Ejecución con Docker

El backend incluye configuración Docker:
```bash
# Desde el directorio backend
docker-compose up -d
```

## 🧪 Pruebas

Ejecutar pruebas del backend:
```bash
cd backend
pytest
```

## 📡 Endpoints Principales del API

Ver la documentación completa en http://localhost:8000/docs cuando el backend esté ejecutándose.

### Autenticación
- `POST /token` - Obtener token de acceso
- `POST /register` - Registrar nuevo usuario
- `GET /users/me` - Obtener perfil del usuario actual

### Planes
- `GET /plans` - Obtener lista de planes
- `POST /plans` - Crear un nuevo plan
- `GET /plans/{plan_id}` - Obtener detalles de un plan

### Suscripciones
- `GET /subscriptions` - Obtener suscripciones del usuario
- `POST /subscriptions` - Crear una suscripción
- `PUT /subscriptions/{subscription_id}/cancel` - Cancelar una suscripción

### Pagos
- `GET /payments` - Obtener historial de pagos
- `POST /payments/{subscription_id}` - Realizar un pago

## 🤝 Contribuciones

1. Fork el repositorio
2. Crear una rama para la funcionalidad (`git checkout -b feature/funcionalidad`)
3. Realizar los cambios y commit (`git commit -m "Agrega funcionalidad"`)
4. Push a la rama (`git push origin feature/funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](backend/LICENSE) para más detalles.