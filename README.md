# CampusConnect

CampusConnect is a Django campus event booking and management system for students, event organizers and administrators.

## Stack

- Django 5, Django ORM and Django authentication
- SQLite for local development; PostgreSQL/Neon for production
- HTML5, CSS and Bootstrap-compatible server-rendered templates
- Safaricom Daraja STK Push
- WhiteNoise and Gunicorn for Render deployment

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Set `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` and `DATABASE_URL` in `.env`. Never commit `.env`.

## Daraja

Set `DARJA_CONSUMER_KEY`, `DARJA_CONSUMER_SECRET`, `DARJA_SHORTCODE`, `DARJA_PASSKEY`, `DARJA_CALLBACK_URL` and `DARJA_ENVIRONMENT=sandbox`. The callback endpoint is `/payments/callback/`.

When Daraja is not configured in local development, paid-event forms provide an explicitly labeled simulation. It is disabled when `DEBUG=False`.

## Tests

```bash
python manage.py test
```

## Render deployment

1. Create a Neon PostgreSQL database and add its connection URL as `DATABASE_URL`.
2. Add `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and Daraja variables.
3. Set `DEBUG=False`.
4. Deploy with `gunicorn config.wsgi:application`.
5. Run `python manage.py migrate` after deployment.
6. Configure persistent media storage for poster and other uploads; local `media/` storage is unsuitable for ephemeral hosting.
