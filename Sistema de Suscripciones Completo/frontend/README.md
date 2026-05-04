# Frontend - Sistema de Gestión de Suscripciones

Interfaz de usuario web para el Sistema de Gestión de Suscripciones y Pagos Recurrentes.

## Estructura

```
frontend/
├── static/
│   ├── index.html       # Página principal
│   ├── css/
│   │   └── styles.css   # Estilos personalizados
│   └── js/
│       └── app.js       # Lógica de la aplicación frontend
```

## Tecnologías Utilizadas

- HTML5
- CSS3 (con Bootstrap 5.3)
- JavaScript ES6
- Bootstrap Icons

## Características

- Dashboard con vista general
- Gestión de planes de suscripción
- Visualización y gestión de suscripciones activas
- Historial de pagos
- Perfil de usuario
- Diseño responsivo

## Cómo Funciona

El frontend se comunica con el backend a través de las siguientes APIs:

- Autenticación: `/token`, `/register`, `/users/me`
- Planes: `/plans`
- Suscripciones: `/subscriptions`
- Pagos: `/payments`

Para que el frontend funcione correctamente, el backend debe estar ejecutándose en `http://localhost:8000`.

## Desarrollo

Para ejecutar el frontend en modo desarrollo:
```bash
cd frontend
python -m http.server 3000
```

Luego abre tu navegador en `http://localhost:3000`

## Personalización

Puedes modificar:
- `static/css/styles.css` para cambiar los estilos
- `static/js/app.js` para modificar la lógica de la aplicación
- `static/index.html` para cambiar la estructura HTML