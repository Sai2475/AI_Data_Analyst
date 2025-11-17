# api/index.py

from app import app  # Import your Flask app
from vercel_wsgi import handle

def handler(event, context):
    return handle(app, event, context)
