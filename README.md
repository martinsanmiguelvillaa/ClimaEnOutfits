# ClimaEnOutfits 🌤️👗

Sistema de recomendación de outfits basado en el clima en tiempo real. Dado una ciudad o ubicación, consulta el clima actual y genera una sugerencia de vestimenta personalizada usando inteligencia artificial, considerando temperatura, humedad, viento, índice UV y las preferencias del usuario.

## Funcionalidades

- 🔍 **Búsqueda por ciudad o ubicación GPS** — clima y outfit en segundos
- 👤 **Cuentas de usuario** — registro, login con JWT, perfil editable
- 💾 **Preferencias de estilo** — el usuario guarda sus preferencias y la IA las incorpora
- 🔔 **Notificaciones diarias automáticas** — a la hora que elija el usuario
- 📧 **Canal email** — notificación con HTML formateado via Resend
- 💬 **Canal WhatsApp** — notificación via Twilio con template aprobada
- 🧠 **Recomendación con IA** — GPT genera outfits considerando género, clima y preferencias

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML + CSS + JavaScript vanilla |
| Backend | FastAPI (Python 3.13) |
| Base de datos | MySQL 8 + SQLAlchemy |
| Autenticación | JWT (PyJWT) + bcrypt |
| Clima | OpenWeatherMap API |
| IA | OpenAI API (GPT) |
| Email | Resend API |
| WhatsApp | Twilio WhatsApp Business API |
| Scheduler | APScheduler |
| Deploy backend | Railway |
| Deploy frontend | Vercel |

## Estructura del proyecto

```
├── app/
│   ├── main.py                # Entrypoint FastAPI, CORS, middlewares
│   ├── auth.py                # JWT: creación y validación de tokens
│   ├── db.py                  # Conexión a MySQL
│   ├── limiter.py             # Rate limiting (SlowAPI)
│   ├── logger.py              # Configuración de logs
│   ├── models/
│   │   ├── user.py            # Modelo Usuario
│   │   ├── preferences.py     # Preferencias de outfit
│   │   ├── weather_logs.py    # Historial de clima consultado
│   │   ├── mail_logs.py       # Log de emails enviados
│   │   └── whatsapp_logs.py   # Log de WhatsApps enviados
│   ├── schemas/
│   │   ├── user.py            # Schemas de registro, login, respuestas
│   │   ├── outfit.py          # Schema de respuesta de outfit
│   │   ├── weather.py         # Schema de datos del clima
│   │   └── preferences.py     # Schema de preferencias
│   ├── routers/
│   │   ├── auth.py            # POST /auth/login
│   │   ├── users.py           # CRUD de usuarios + outfit personalizado
│   │   ├── weather.py         # GET /weather/{city} y /weather/location
│   │   ├── outfit.py          # GET /outfit/{city} y /outfit/location
│   │   ├── preferences.py     # CRUD de preferencias + notificaciones
│   │   └── notification.py    # POST /notifications/notify/{user_id}
│   └── services/
│       ├── weather.py         # Llamadas a OpenWeatherMap
│       ├── outfit.py          # Prompt a OpenAI + parseo de respuesta
│       ├── notification.py    # Orquestación email/WhatsApp
│       ├── mail.py            # Integración con Resend
│       ├── whatsapp.py        # Integración con Twilio
│       └── scheduler.py       # Jobs programados con APScheduler
├── frontend/
│   ├── index.html             # SPA: home, registro, dashboard
│   ├── css/style.css          # Estilos (glassmorphism)
│   └── js/app.js              # Lógica frontend, manejo de sesión y API calls
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── railway.toml
```

## API — Endpoints principales

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/auth/login` | No | Login, devuelve JWT |
| POST | `/users` | No | Registro de usuario |
| GET | `/users/{id}` | Sí | Perfil del usuario |
| PATCH | `/users/{id}` | Sí | Editar perfil |
| DELETE | `/users/{id}` | Sí | Eliminar cuenta |
| GET | `/weather/{city}` | No | Clima por ciudad |
| GET | `/weather/location` | No | Clima por coordenadas |
| GET | `/outfit/{city}` | No | Outfit por ciudad |
| GET | `/outfit/location` | No | Outfit por coordenadas |
| GET | `/users/{id}/outfit` | Sí | Outfit personalizado (con preferencias) |
| GET | `/preferences/{id}/preferences` | Sí | Ver preferencias |
| POST | `/preferences/{id}/outfit_preferences` | Sí | Agregar preferencia |
| PATCH | `/preferences/{id}/preference/{pref_id}` | Sí | Editar preferencia |
| DELETE | `/preferences/{id}/preference/{pref_id}` | Sí | Eliminar preferencia |
| PUT | `/preferences/{id}/notifications_moment` | Sí | Configurar notificaciones |
| POST | `/notifications/notify/{id}` | Sí | Enviar notificación ahora |

## Variables de entorno

```env
# Base de datos
DATABASE_URL=mysql+pymysql://user:password@host:port/dbname

# APIs externas
OPENWEATHER_API_KEY=
OPENAI_API_KEY=
RESEND_API_KEY=

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+15559123035
TWILIO_WHATSAPP_CONTENT_SID=

# Seguridad
SECRET_KEY=
```

## Correr localmente

**Requisitos:** Python 3.13+, MySQL 8

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.docker .env
# Editar .env con tus valores

# 3. Levantar la app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Con Docker Compose:**

```bash
docker-compose up
```

La API queda disponible en `http://localhost:8000`.
Documentación interactiva en `http://localhost:8000/docs`.

## Deploy

- **Backend:** Railway — conectado al repositorio, deploy automático en cada push a `main`. Variables de entorno configuradas en el dashboard de Railway.
- **Frontend:** Vercel — deploy automático desde el directorio `frontend/`.
- **Base de datos:** MySQL en Railway, tablas creadas automáticamente al iniciar la app.

## Seguridad

- Autenticación con JWT (expiración 7 días)
- Passwords hasheados con bcrypt
- Rate limiting: 60 req/min global, 10 req/min en endpoints de outfit
- CORS restringido al dominio de Vercel
- Límite de tamaño de request: 10 KB
- Validación de coordenadas geográficas
- Ownership checks en todos los endpoints protegidos
