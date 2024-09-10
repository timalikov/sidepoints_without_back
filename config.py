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
CUSTOMER_SUPPORT_TEAM_IDS = [575702446677164055, 419205987895869440, 1172872070804283405]

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

MESSAGES = [
    (10, "🚀 Just a quick update: We're on it! Thanks for your patience! 🌟 Kicker should join within 5 minutes, otherwise we will refund your money.", False),
    (20, "🔧 Our team is working their magic! Hang tight - we're almost there! Kicker should join within 4 minutes 40 seconds, otherwise we will refund your money.", False),
    (40, "⏳ Thanks for sticking with us! We’re making progress, stay tuned! 🚀 Kicker should join within 4 minutes 20 seconds, otherwise we will refund your money.", False),
    (60, "", True), 
    (80, "💪 We’re on a mission to get this sorted for you! Thanks for your patience! 🙌 Kicker should join within 3 minutes 40 seconds, otherwise we will refund your money.", False),
    (110, "🛠️ Almost there! Our team is busy behind the scenes. We appreciate your patience! 🎉 Kicker should join within 3 minutes 10 seconds, otherwise we will refund your money.", False),
    (150, "🎯 We’re making strides! Thanks for hanging in there – we’ll be with you shortly! 🚀 Kicker should join within 2 minutes 30 seconds, otherwise we will refund your money.", False),
    (180, "", True),
    (210, "✨ Just a little bit more time! We’re working hard to get everything sorted. Thanks! 💪 Kicker should join within 1 minute 30 seconds, otherwise we will refund your money.", False),
    (240, "🔍 Almost ready! Our team is doing their thing. Thanks for waiting! 🙌 Kicker should join within 1 minute, otherwise we will refund your money.", False),
    (255, "Oops! Looks like we hit a snag. We're on it and will make it right soon! 🙌 Kicker should join within 45 seconds, otherwise we will refund your money.", False),
    (270, "Oops! 😬 We hit a snag and couldn’t deliver. No worries – get your refund 💸 <#1233350206280437760>. Thanks for your patience! Kicker should join within 30 seconds, otherwise we will refund your money.", False),
    (285, "My bad! 🙊 We missed the delivery. Click  <#1233350206280437760> to grab your refund 💵 and we’ll get things sorted out. Thanks for sticking with us! Kicker should join within 15 seconds, otherwise we will refund your money.", False),
    (300, "Our bad! We couldn’t get it to you on time. Expect a refund soon, and we’ll make sure it doesn’t happen again! Click here <#1233350206280437760> to refund.", False)
]

HOST_PSQL = os.getenv('HOST_PSQL').strip()
USER_PSQL = os.getenv('USER_AWS_PSQL').strip()
PASSWORD_PSQL = os.getenv('PASSWORD_PSQL').strip()
DATABASE_PSQL = os.getenv('DATABASE_PSQL').strip()
PORT_PSQL = os.getenv('PORT_PSQL').strip()

BOOST_CHANNEL_ID = 1208438041991970868
ORDER_CHANNEL_ID = 1282984658014961675

FIRST_LIMIT_CHECK_MINUTES = 5
SECOND_LIMIT_CHECK_MINUTES = 30
