import threading
from core_commands import run as run_bot
from web.flask_app import create_app

from flask_cors import CORS
from config import PORT_ID

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    flask_app = create_app()
    CORS(flask_app)  # This will enable CORS for all routes
    flask_app.run(host='localhost', port=PORT_ID, debug=True)
