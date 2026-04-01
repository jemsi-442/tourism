# tourism

Tourism booking and admin dashboard project built with Django.

## Repository layout

- `tourism_backend/` contains the Django project
- `tourism_backend/main/` contains the app, templates, static files, and tests

## Stack

- Python 3
- Django 4.2
- Pillow
- SQLite for local development

## Local setup

```bash
cd tourism_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Environment variables

This project reads configuration from environment variables.

- `DJANGO_ENV`
- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`

For production-like environments, `DJANGO_SECRET_KEY` is required.

## Useful commands

```bash
cd tourism_backend
python3 manage.py migrate
python3 manage.py check
python3 manage.py test
python3 manage.py collectstatic --noinput
```

## Notes

- Local database files are ignored.
- Uploaded media is ignored.
- Python cache files are ignored.
- Static photos are ignored from git tracking.
- Copy values from `tourism_backend/.env.example` into your deployment environment before going live.

## PythonAnywhere

This project can be deployed on PythonAnywhere without Docker.

### Recommended setup

1. Clone the repo on PythonAnywhere
2. Create a virtualenv and install dependencies
3. Set environment values for:
   - `DJANGO_ENV=production`
   - `DJANGO_DEBUG=False`
   - `DJANGO_SECRET_KEY`
   - `DJANGO_ALLOWED_HOSTS`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`
4. Run:

```bash
cd ~/tourism/tourism_backend
python3 manage.py migrate
python3 manage.py collectstatic --noinput
```

5. In the PythonAnywhere Web tab:
   - point the WSGI file to this project
   - map `/static/` to `/home/yourusername/tourism/tourism_backend/staticfiles`
   - map `/media/` to `/home/yourusername/tourism/tourism_backend/media`

Use the example file at `tourism_backend/pythonanywhere_wsgi.py.example` as a starting point for your WSGI config.
