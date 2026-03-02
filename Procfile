# MarkoVision Procfile
# =====================
# Entry point for deployment platforms like Heroku, Render, etc.

web: gunicorn wsgi:app --workers 4 --bind 0.0.0.0:$PORT --timeout 120
