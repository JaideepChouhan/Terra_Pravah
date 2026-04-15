"""WSGI entrypoint for production servers."""

from backend.app import create_app

app = create_app()
