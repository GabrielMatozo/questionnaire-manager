import sys

if getattr(sys, "frozen", False):
    import multiprocessing

    multiprocessing.freeze_support()


import threading
import webbrowser

from app import create_app
from app.models import db
from app.tray import create_tray_icon

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    threading.Thread(target=create_tray_icon, daemon=True).start()
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
