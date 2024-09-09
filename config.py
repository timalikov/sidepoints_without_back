import os
from dotenv import load_dotenv
load_dotenv()
MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
FORUM_ID = int(os.getenv('FORUM_ID'))
FORUM_NAME = "🔎find-your-kickers"
PORT_ID = int(os.getenv('PORT_ID'))
LEADER_BOT_CHANNEL = int(os.getenv('LEADER_BOT_CHANNEL'))
# FORUM_ID_LIST = [1248303158313222255, 1240260161491439637, 1242449492280737843]
FORUM_ID_LIST = [1237300150301360138, 1244598037758738553]
CUSTOMER_SUPPORT_TEAM_IDS = [575702446677164055, 419205987895869440]

# link_to_back = f"http://127.0.0.1:8001/discordServices"
link_to_back = os.getenv('BOTAPI_URL') # f"http://172.31.7.179:8001/discordServices"

SERVER_ID_LIST = []

LEADER_BOT_CHANNEL_LIST = [1242448780801081475, 1240912296981561405, 1242449117461086290]

APP_CHOICES = {
    "BUDDY": "57c86488-8935-4a13-bae0-5ca8783e205d",
    "COACHING": "88169d78-85b4-4fa3-8298-3df020f13a6f",
    "JUST_CHATTING": "2974b0e8-69de-4d7c-aa4d-d5aa8e05d360",
    "MOBILE": "439d8a72-8b8b-4a56-bb32-32c6e5d918ec",
    "Watch Youtube": "d3ae39d2-fd86-41d7-bc38-0b582ce338b5",
    "Play Games": "79bf303a-318b-4815-bd56-7b0b49ae7bff",
    "Virtual Date": "d6b9fc04-bfb2-46df-88eb-6e8c149e34d9"
}

TASK_DESCRIPTIONS = {
    "57c86488-8935-4a13-bae0-5ca8783e205d": "BUDDY",
    "88169d78-85b4-4fa3-8298-3df020f13a6f": "COACHING",
    "2974b0e8-69de-4d7c-aa4d-d5aa8e05d360": "JUST_CHATTING",
    "439d8a72-8b8b-4a56-bb32-32c6e5d918ec": "MOBILE",
    "d3ae39d2-fd86-41d7-bc38-0b582ce338b5": "Watch Youtube",
    "79bf303a-318b-4815-bd56-7b0b49ae7bff": "Play Games",
    "d6b9fc04-bfb2-46df-88eb-6e8c149e34d9": "Virtual Date"
}

CATEGORY_TO_TAG = {
    "57c86488-8935-4a13-bae0-5ca8783e205d": "BUDDY",
    "88169d78-85b4-4fa3-8298-3df020f13a6f": "COACHING",
    "2974b0e8-69de-4d7c-aa4d-d5aa8e05d360": "JUST CHATTING",
    "439d8a72-8b8b-4a56-bb32-32c6e5d918ec": "MOBILE",
    "d3ae39d2-fd86-41d7-bc38-0b582ce338b5": "Watch Youtube",
    "79bf303a-318b-4815-bd56-7b0b49ae7bff": "Play Games",
    "d6b9fc04-bfb2-46df-88eb-6e8c149e34d9": "Virtual Date"
}

HOST_PSQL = os.getenv('HOST_PSQL').strip()
USER_PSQL = os.getenv('USER_AWS_PSQL').strip()
PASSWORD_PSQL = os.getenv('PASSWORD_PSQL').strip()
DATABASE_PSQL = os.getenv('DATABASE_PSQL').strip()
PORT_PSQL = os.getenv('PORT_PSQL').strip()

BOOST_CHANNEL_ID = 1208438041991970868
