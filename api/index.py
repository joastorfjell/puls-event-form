# Vercel serverless entrypoint for the Flask app
# Exposes a WSGI callable named `app` as required by Vercel's Python runtime.
from werkzeug.middleware.proxy_fix import ProxyFix
from app import app as flask_app

# Ensure correct X-Forwarded-* handling behind Vercel's proxy
flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Vercel looks for a top-level `app` WSGI callable
app = flask_app
