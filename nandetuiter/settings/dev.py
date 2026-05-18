"""Settings de desarrollo. Hereda de base."""
from .base import *  # noqa: F401,F403

DEBUG = True

# Permitir todo en dev (Angular en 4200, Django en 8000)
CORS_ALLOW_ALL_ORIGINS = True

# En dev usamos SQLite para no depender de Postgres local.
# Prod sigue usando Postgres (ver prod.py / base.py).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
