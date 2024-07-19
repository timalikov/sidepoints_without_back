import threading
from multiprocessing import Process
from core_commands import run as run_bot
from web.flask_app import create_app
import web3_test
import push_order
from flask_cors import CORS
from config import PORT_ID

if __name__ == "__main__":
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Start the web3_interaction process
    process = Process(target=web3_test.main)
    process.start()

    # Start the Flask app
    flask_app = create_app()
    CORS(flask_app)  # This will enable CORS for all routes

    # Start the push notifications in a separate thread
    # push_notifications_thread = threading.Thread(target=push_order.start_push_notifications)
    # push_notifications_thread.start()
    flask_app.run(host='0.0.0.0', port=PORT_ID)
