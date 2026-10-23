"""WSGI entry point for gunicorn: `gunicorn iris_classifier.wsgi:app`."""

from .api import create_app

app = create_app()
