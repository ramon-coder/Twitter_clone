# Sistema de Suscripciones Completo - Documentación Completa

## Descripción General

Este documento describe la arquitectura, funcionamiento de la API, implementación del cliente y procedimientos de prueba para el Sistema de Suscripciones y Pagos Recurrentes.

El sistema está construido con:
- **Backend**: FastAPI (Python) con base de datos SQLite/PostgreSQL
- **Frontend**: JavaScript vanilla con Bootstrap 5
- **Autenticación**: JWT (JSON Web Tokens)
- **Pagos**: Integración con Stripe

---

## Tabla de Contenidos

1. [Arquitectura de la API](#1-arquitectura-de-la-api)
2. [Endpoints de la API](#2-endpoints-de-la-api)
3. [Implementación del Cliente](#3-implementación-del-cliente)
4. [Pruebas](#4-pruebas)
5. [Flujos de Trabajo](#5-flujos-de-trabajo)

---

## 1. Arquitectura de la API

### Estructura del Proyecto

```
backend/
├── main.py              # Configuración principal de FastAPI
├── routers/             # Rutas de la API
│   ├── auth.py         # Autenticación y usuarios
│   ├── plans.py        # Gestión de planes
│   ├── subscriptions.py # Gestión de suscripciones
│   ├── payments.py     # Procesamiento de pagos
│   ├── users.py        # Gestión de usuarios
│   └── webhooks.py     # Webhooks de Stripe
├── models/              # Modelos de base de datos
│   ├── user.py
│   ├── plan.py
│   ├── subscription.py
│   ├── payment.py
│   └── invoice.py
├── services/            # Servicios de negocio
│   ├── payment_service.py
│   ├── email_service.py
│   └── scheduled_tasks.py
└── tests/               # Pruebas automatizadas
```

### Configuración Principal

**main.py** configura:
- Aplicación FastAPI con CORS
- Middleware de límite de tasa (Rate Limiting)
- Conexión a base de datos (SQLAlchemy)
- Autenticación JWT
- Manejo global de errores
- Tareas programadas para renovaciones

### Autenticación

- **Esquema**: OAuth2 Password Flow con JWT
- **Algoritmo**: HS256
- **Expiración**: 30 minutos (configurable)
- **Almacenamiento**: Token en localStorage del cliente

**Variables de entorno críticas**:
```bash
SECRET_KEY=your-secret-key-minimum-32-chars
DATABASE_URL=sqlite:///./subscriptions.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
SCHEDULER_ENABLED=True
```

---

## 2. Endpoints de la API

### 2.1 Autenticación (`/auth/`)

#### Registro de Usuario
```http
POST /auth/register
```
**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string",
  "phone_number": "string"
}
```
**Responses:**
- `200`: Registro exitoso
- `400`: Usuario ya existe

#### Login (Obtener Token)
```http
POST /auth/token
```
**Request Body (x-www-form-urlencoded):**
```
username=string&password=string
```
**Response:**
```json
{
  "access_token": "token.jwt",
  "token_type": "bearer"
}
```

#### Obtener Usuario Actual
```http
GET /auth/users/me
Authorization: Bearer <token>
```

#### Cambiar Contraseña
```http
POST /auth/change-password
Authorization: Bearer <token>
```
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

#### Resetear Contraseña
```http
POST /auth/reset-password
```
```json
{
  "email": "string"
}
```

### 2.2 Planes (`/plans/`)

#### Listar Planes
```http
GET /plans?active_only=true
```
**Query Parameters:**
- `active_only`: boolean (default: true)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Premium",
    "description": "Plan premium",
    "price": 29.99,
    "duration": 30,
    "features": "[\"Feature1\", \"Feature2\"]",
    "is_active": true
  }
]
```

#### Obtener Plan Específico
```http
GET /plans/{plan_id}
```

#### Crear Plan (Admin)
```http
POST /plans/
Authorization: Bearer <token>
```
```json
{
  "name": "string",
  "description": "string",
  "price": 0.0,
  "duration": 30,
  "features": "string"
}
```

#### Actualizar Plan (Admin)
```http
PUT /plans/{plan_id}
Authorization: Bearer <token>
```
```json
{
  "name": "string",
  "description": "string",
  "price": 0.0,
  "duration": 30,
  "features": "string",
  "is_active": true
}
```

#### Eliminar Plan (Admin)
```http
DELETE /plans/{plan_id}
Authorization: Bearer <token>
```

### 2.3 Suscripciones (`/subscriptions/`)

#### Listar Suscripciones
```http
GET /subscriptions?user_id=1&plan_id=1&status=active
Authorization: Bearer <token>
```
**Query Parameters (opcionales):**
- `user_id`: Filtrar por usuario
- `plan_id`: Filtrar por plan
- `status`: Filtrar por estado

**Nota**: Usuarios no-admin solo ven sus propias suscripciones.

#### Obtener Suscripción Específica
```http
GET /subscriptions/{subscription_id}
Authorization: Bearer <token>
```

#### Crear Suscripción
```http
POST /subscriptions/
Authorization: Bearer <token>
```
```json
{
  "plan_id": 1,
  "auto_renew": true
}
```

**Reglas de negocio:**
- No se pueden crear suscripciones duplicadas activas al mismo plan
- La fecha de fin se calcula automáticamente según la duración del plan

#### Actualizar Suscripción
```http
PUT /subscriptions/{subscription_id}
Authorization: Bearer <token>
```
```json
{
  "plan_id": 2,
  "auto_renew": false
}
```

#### Cancelar Suscripción
```http
PUT /subscriptions/{subscription_id}/cancel
Authorization: Bearer <token>
```

#### Renovar Suscripción
```http
PUT /subscriptions/{subscription_id}/renew
Authorization: Bearer <token>
```

### 2.4 Pagos (`/payments/`)

#### Listar Pagos
```http
GET /payments
Authorization: Bearer <token>
```

#### Crear Pago (Checkout)
```http
POST /payments/
Authorization: Bearer <token>
```
```json
{
  "amount": 29.99,
  "currency": "usd",
  "payment_method_id": "pm_card_..."
}
```

### 2.5 Webhooks (`/webhooks/`)

#### Stripe Webhook
```http
POST /webhooks/stripe
```

Maneja eventos de Stripe:
- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`

---

## 3. Implementación del Cliente

### 3.1 Estructura del Frontend

```
frontend/cliente/
├── static/js/app.js      # Lógica principal
└── templates/            # Plantillas HTML
```

### 3.2 Configuración

**Configuración base:**
```javascript
const API_BASE = 'http://localhost:8000';
let token = localStorage.getItem('token');
let currentUser = null;
```

### 3.3 Autenticación

#### Login
```javascript
async function login(username, password) {
    const response = await fetch(`${API_BASE}/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    });
    
    if (response.ok) {
        const data = await response.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        await loadCurrentUser();
        navigateTo('dashboard');
    }
}
```

#### Logout
```javascript
function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    showLoginModal();
}
```

#### Encabezados de Autenticación
```javascript
function getAuthHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}
```

### 3.4 Navegación

**Sistema de enrutamiento simple:**
```javascript
let currentPage = 'dashboard';

async function navigateTo(page) {
    currentPage = page;
    // Renderiza la página correspondiente
    switch (page) {
        case 'dashboard':
            await renderDashboard();
            break;
        case 'plans':
            await renderPlans();
            break;
        // ... otros casos
    }
}
```

**Páginas disponibles:**
- `dashboard`: Vista general con estadísticas
- `plans`: Listado de planes disponibles
- `subscriptions`: Gestión de suscripciones
- `payments`: Historial de pagos
- `profile`: Perfil de usuario
- `settings`: Configuración (cambio de contraseña)

### 3.5 Gestión de Suscripciones

#### Listar Suscripciones
```javascript
async function renderSubscriptions() {
    const response = await fetch(`${API_BASE}/subscriptions`, {
        headers: getAuthHeaders()
    });
    const subscriptions = await response.json();
    
    // Renderiza tabla con suscripciones
}
```

#### Crear Suscripción
```javascript
async function subscribeToPlan(planId) {
    const response = await fetch(`${API_BASE}/subscriptions`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ 
            plan_id: planId, 
            auto_renew: true 
        })
    });
    
    if (response.ok) {
        showAlert('Suscripción creada', 'success');
    }
}
```

#### Cancelar Suscripción
```javascript
async function cancelSubscription(subscriptionId) {
    const response = await fetch(
        `${API_BASE}/subscriptions/${subscriptionId}/cancel`,
        {
            method: 'PUT',
            headers: getAuthHeaders()
        }
    );
}
```

### 3.6 Manejo de Estados

**Colores de estado:**
```javascript
function getStatusColor(status) {
    const colors = {
        'active': 'success',
        'cancelled': 'danger',
        'expired': 'secondary',
        'pending': 'warning'
    };
    return colors[status] || 'secondary';
}
```

**Colores de estado de pago:**
```javascript
function getPaymentStatusColor(status) {
    const colors = {
        'succeeded': 'success',
        'pending': 'warning',
        'failed': 'danger',
        'refunded': 'info'
    };
    return colors[status] || 'secondary';
}
```

### 3.7 Alertas

```javascript
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = message;
    content.insertBefore(alertContainer, content.firstChild);
    
    setTimeout(() => alertContainer.remove(), 5000);
}
```

---

## 4. Pruebas

### 4.1 Configuración de Pruebas

Las pruebas utilizan **pytest** con el cliente de prueba de FastAPI.

**Estructura de pruebas:**
```
backend/tests/
├── conftest.py         # Fixtures compartidas
├── test_auth.py        # Pruebas de autenticación
├── test_plans.py       # Pruebas de planes
└── test_subscriptions.py # Pruebas de suscripciones
```

### 4.2 Ejecutar Pruebas

```bash
# Desde el directorio backend
cd backend
pytest tests/ -v
```

**Opciones útiles:**
```bash
pytest tests/ -v          # Detallado
pytest tests/ -k auth     # Filtrar por nombre
pytest tests/ --cov       # Con cobertura
pytest tests/ -x          # Detener en primera falla
```

### 4.3 Estructura de una Prueba

**Ejemplo: Crear suscripción**

```python
def test_create_subscription(client):
    # 1. Crear usuario admin
    client.post("/auth/register", json={...})
    
    # 2. Login para obtener token
    admin_login = client.post("/auth/token", data={
        "username": "admin",
        "password": "adminpassword"
    })
    admin_token = admin_login.json()["access_token"]
    
    # 3. Crear plan
    client.post("/plans/", json={...}, 
                headers={"Authorization": f"Bearer {admin_token}"})
    
    # 4. Crear usuario regular
    client.post("/auth/register", json={...})
    
    # 5. Login usuario regular
    login = client.post("/auth/token", data={
        "username": "user",
        "password": "password"
    })
    token = login.json()["access_token"]
    
    # 6. Obtener ID del plan
    plans = client.get("/plans/", 
                      headers={"Authorization": f"Bearer {token}"})
    plan_id = plans.json()[0]["id"]
    
    # 7. Crear suscripción
    response = client.post("/subscriptions/", json={
        "plan_id": plan_id,
        "auto_renew": True
    }, headers={"Authorization": f"Bearer {token}"})
    
    # 8. Verificar resultado
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Subscription created successfully"
    assert data["subscription"]["plan_id"] == plan_id
```

### 4.4 Casos de Prueba Disponibles

#### Autenticación (`test_auth.py`)

1. **test_register_user**: Registro exitoso
2. **test_register_existing_user**: Error al registrar usuario duplicado
3. **test_login_with_valid_credentials**: Login exitoso
4. **test_login_with_invalid_credentials**: Login fallido
5. **test_get_current_user**: Obtener perfil del usuario
6. **test_change_password**: Cambiar contraseña
7. **test_change_password_invalid_current**: Error al cambiar con contraseña incorrecta
8. **test_reset_password**: Solicitar reseteo
9. **test_reset_password_nonexistent_email**: Error con email inexistente

#### Planes (`test_plans.py`)

1. **test_get_all_plans**: Listar planes
2. **test_create_plan**: Crear plan (admin)
3. **test_create_plan_with_existing_name**: Error nombre duplicado
4. **test_get_specific_plan**: Obtener plan por ID
5. **test_get_nonexistent_plan**: Error plan inexistente
6. **test_update_plan**: Actualizar plan
7. **test_delete_plan**: Eliminar plan
8. **test_non_admin_cannot_create_plan**: Validación de permisos

#### Suscripciones (`test_subscriptions.py`)

1. **test_create_subscription**: Crear suscripción
2. **test_get_subscriptions**: Listar suscripciones
3. **test_get_specific_subscription**: Obtener suscripción
4. **test_update_subscription**: Actualizar suscripción
5. **test_cancel_subscription**: Cancelar suscripción
6. **test_renew_subscription**: Renovar suscripción
7. **test_get_user_subscriptions**: Suscripciones del usuario

### 4.5 Flujo de Pruebas Completo

```bash
# Ejecutar todas las pruebas
pytest tests/ -v

# Ejecutar solo pruebas de autenticación
pytest tests/test_auth.py -v

# Ejecutar con reporte detallado
pytest tests/ -v --tb=short

# Ejecutar en modo silencioso (solo fallos)
pytest tests/ --quiet

# Ver tiempos de ejecución
pytest tests/ --durations=10
```

### 4.6 Mocks y Fixtures

**Fixture común (`conftest.py`):**
```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)
```

**Uso en pruebas:**
```python
def test_something(client):
    # client ya está configurado
    response = client.get("/endpoint")
```

### 4.7 Buenas Prácticas de Pruebas

1. **Independencia**: Cada prueba debe ser independiente
2. **Orden**: No depender del orden de ejecución
3. **Limpieza**: Las pruebas no deben dejar datos residuales
4. **Datos únicos**: Usar nombres/emails únicos por prueba
5. **Aserciones claras**: Verificar todos los campos relevantes
6. **Escenarios de error**: Probar casos inválidos

---

## 5. Flujos de Trabajo

### 5.1 Flujo de Autenticación

```mermaid
sequenceDiagram
    participant Cliente
    participant API
    participant DB
    
    Cliente->>API: POST /auth/register (crear cuenta)
    API->>DB: Guardar usuario
    DB-->>API: Usuario creado
    API-->>Cliente: 200 OK
    
    Cliente->>API: POST /auth/token (login)
    API->>DB: Validar credenciales
    DB-->>API: Usuario válido
    API-->>Cliente: JWT Token
    
    Cliente->>API: GET /users/me (con token)
    API->>API: Validar JWT
    API->>DB: Obtener usuario
    DB-->>API: Datos del usuario
    API-->>Cliente: Datos del usuario
```

### 5.2 Flujo de Suscripción

```mermaid
sequenceDiagram
    participant Cliente
    participant API
    participant DB
    
    Cliente->>API: GET /plans (listar planes)
    API->>DB: Consultar planes activos
    DB-->>API: Lista de planes
    API-->>Cliente: Planes disponibles
    
    Cliente->>API: POST /subscriptions (crear)
    Note over Cliente,API: Con token JWT
    API->>API: Validar JWT
    API->>DB: Verificar plan
    API->>DB: Verificar suscripción existente
    DB-->>API: Resultados
    API->>DB: Crear suscripción
    DB-->>API: Suscripción creada
    API-->>API: Calcular fechas
    API-->>Cliente: Suscripción confirmada
```

### 5.3 Flujo de Cancelación/Renovación

```mermaid
sequenceDiagram
    participant Cliente
    participant API
    participant DB
    
    Cliente->>API: PUT /subscriptions/{id}/cancel
    Note over Cliente,API: Con token JWT
    API->>API: Validar JWT
    API->>DB: Verificar propiedad
    DB-->>API: Subscripción
    API->>API: Validar estado (activa)
    API->>DB: Actualizar estado
    DB-->>API: Confirmación
    API-->>Cliente: Suscripción cancelada
    
    Cliente->>API: PUT /subscriptions/{id}/renew
    Note over Cliente,API: Con token JWT
    API->>DB: Verificar propiedad
    DB-->>API: Subscripción y plan
    API->>API: Calcular nueva fecha
    API->>DB: Actualizar fecha fin
    DB-->>API: Confirmación
    API-->>Cliente: Suscripción renovada
```

### 5.4 Flujo de Pagos (Stripe)

```mermaid
sequenceDiagram
    participant Cliente
    participant API
    participant Stripe
    participant Webhook
    
    Cliente->>API: POST /payments (intentar pago)
    Note over Cliente,API: Con token JWT
    API->>Stripe: Crear PaymentIntent
    Stripe-->>API: PaymentIntent ID
    API-->>Cliente: Confirmar pago
    
    Cliente->>Stripe: Procesar tarjeta
    Stripe-->>Cliente: Resultado
    
    Stripe->>Webhook: Evento (succeeded/failed)
    Note over Stripe,Webhook: Llamada asincrónica
    Webhook->>API: POST /webhooks/stripe
    API->>DB: Actualizar estado pago
    API-->>Webhook: 200 OK
```

---

## 6. Seguridad

### 6.1 Autenticación y Autorización

**Protección de endpoints:**
- Rutas de usuarios, suscripciones, pagos: Requieren token JWT
- Rutas de admin (crear/actualizar/eliminar): Requieren `is_admin=True`
- Validación de propietario: Los usuarios solo ven/modifican sus propios datos

**Manejo de errores:**
```python
# 401: No autorizado (token inválido/expirado)
# 403: Prohibido (sin permisos)
# 404: No encontrado
# 400: Solicitud inválida
# 500: Error interno
```

### 6.2 Rate Limiting

Middleware que limita:
- Solicitudes por IP
- Ventana de tiempo configurable
- Encabezados de respuesta:
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Window`

### 6.3 Seguridad de Contraseñas

- Hasheo con bcrypt
- Salt automático
- Verificación segura

### 6.4 CORS

**Desarrollo:**
```python
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
]
```

**Producción:**
```python
origins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

---

## 7. Despliegue

### 7.1 Variables de Entorno Necesarias

```bash
# Obligatorias
SECRET_KEY=your-32-char-secret-key
DATABASE_URL=sqlite:///./subscriptions.db

# Opcionales
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_ENV=development
DEBUG=True
SCHEDULER_ENABLED=True

# Stripe (si aplica)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (si aplica)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=app-password
```

### 7.2 Iniciar la Aplicación

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend (servidor estático)
cd frontend/cliente
python -m http.server 8000
```

### 7.3 Base de Datos

**SQLite (desarrollo):**
```bash
# Se crea automáticamente al iniciar
sqlite:///./subscriptions.db
```

**PostgreSQL (producción):**
```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
```

**Migraciones:**
```bash
# Alembic para migraciones
alembic revision --autogenerate -m "message"
alembic upgrade head
```

---

## 8. Monitoreo y Logging

### 8.1 Health Check

```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T12:00:00",
  "version": "1.0.0",
  "environment": "development",
  "checks": {
    "database": "healthy",
    "redis": "not_configured",
    "scheduler": "running"
  }
}
```

### 8.2 Logs

**Niveles:**
- `INFO`: Operaciones normales
- `WARNING`: Advertencias (ej. configuración)
- `ERROR`: Errores recuperables
- `CRITICAL`: Errores fatales

**Archivo de logs:**
```bash
tail -f app.log
```

### 8.3 Documentación API

**Swagger UI:**
```
http://localhost:8000/docs
```

**ReDoc:**
```
http://localhost:8000/redoc
```

---

## 9. Extensibilidad

### 9.1 Añadir Nuevo Router

```python
# 1. Crear router
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_items():
    return {"message": "Items"}

# 2. Importar en main.py
from routers import items

# 3. Incluir router
app.include_router(items.router, prefix="/items", tags=["Items"])
```

### 9.2 Añadir Nuevo Modelo

```python
# models/new_model.py
from sqlalchemy import Column, Integer, String
from database import Base

class NewModel(Base):
    __tablename__ = "new_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
```

### 9.3 Añadir Middleware

```python
# middleware/my_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware

class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Lógica antes
        response = await call_next(request)
        # Lógica después
        return response

# En main.py
app.add_middleware(MyMiddleware)
```

---

## Conclusión

Este sistema proporciona una base robusta para la gestión de suscripciones y pagos recurrentes. Con su arquitectura modular, pruebas automatizadas y documentación completa, es fácilmente extensible y mantenible.

**Siguientes pasos recomendados:**
1. Implementar pruebas de integración completas
2. Añadir monitoreo con Prometheus/Grafana
3. Implementar caché con Redis
4. Añadir colas de tareas con Celery
5. Implementar CI/CD

**Recursos adicionales:**
- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación Stripe](https://stripe.com/docs)
- [Documentación SQLAlchemy](https://docs.sqlalchemy.org/) 
