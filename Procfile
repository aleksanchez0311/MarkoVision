# MarkoVision Procfile
# =====================
# Entry point for deployment platforms like Heroku, Render, etc.
# Waitress funciona tanto en Linux como Windows

web: waitress-serve --host=0.0.0.0 --port=$PORT --threads=6 wsgi:app
