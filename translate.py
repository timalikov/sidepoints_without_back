from config import RU_GUILDS


def get_lang_prefix(guild_id: int) -> str:
    return "ru" if guild_id in RU_GUILDS else "en"


translations = {
    'not_dm': {
        'en': "I can't use command on direct messages",
        'ru': "Ты не можешь использовать команду в личных сообщениях!"
    },
    'not_community': {
        'en': "Discord channel is not community!",
        'ru': "Ваш канал не является социальным"
    },
    'forum_no_permission': {
        'ru': 'У вас нет прав для использования этой команды!',
        'en': 'Oops, you do not have right to use this command!',
    },
    'forum_posts_created': {
        'ru': 'Посты созданы!',
        'en': 'Posts created!',
    },
    'order_new_alert': {
        'ru': 'Новый заказ: **{choice}** [30 минут]\nУ вас новый заказ на **{choice}**\nПол: **{gender}**.\nЯзык: **{language}**\nКомментарий юзера: {extra_text}',
        'en': 'New Order Alert: **{choice}** [30 minutes]\nYou have a new order for a **{choice}**\nGender: **{gender}**.\nLanguage: **{language}**\nCustomer extra request: {extra_text}',
    },
    'order_new_alert_new':{
        'ru': 'Юзер: ** {customer_discord_id} **\nЗаказ: **{choice}**\nСервер: **{server_name}**\nИгровой сервер: **{game_server}**\nЯзык: **{language}**\nПол: **{gender}**\nКомментарий юзера: {extra_text}',
        'en': 'Customer: ** {customer_discord_id} **\nAlert: **{choice}**\nServer: **{server_name}**\nGame server: **{game_server}**\nLanguage: **{language}**\nGender: **{gender}**\nCustomer extra request: {extra_text}',
    },
    'order_alert_title': {
        'ru': 'Новый заказ!',
        'en': 'New Order!',
    },
    'top_up_balance': {
        'en': 'Top up balance!',
        'ru': 'Пополнение баланса!',
    },
    'wallet_title': {
        'en': '💰 My Wallet',
        'ru': '💰 Мой кошелек',
    },
    'customer': {
        'ru': 'Юзер',
        'en': 'Customer'
    },
    'alert': {
        'ru': 'Заказ',
        'en': 'Alert'
    },
    'server': {
        'ru': 'Сервер',
        'en': 'Server'
    },
    'language': {
        'ru': 'Язык',
        'en': 'Language'
    },
    'gender': {
        'ru': 'Пол',
        'en': 'Gender'
    },
    'all_players': {
        'ru': 'Все игроки',
        'en': 'All players'
    },
    'profile_not_created': {
        'ru': "Похоже, вы еще не создали профиль! Пожалуйста, перейдите по ссылке, чтобы создать профиль.\n{link}/profile?side_auth=DISCORD",
        'en': "Looks like you haven't created a profile with us! Please click the link below to create your profile.\n{link}/profile?side_auth=DISCORD"
    },
    'profile_no_service': {
        'ru': "Похоже, вы создали профиль, но не создали услугу. Нажмите на ссылку ниже, чтобы создать свою первую услугу.\n{link}/services/create?side_auth=DISCORD",
        'en': "Seems like you have created a profile, but you haven't created a service. Please click on the link below to create your first service.\n{link}/services/create?side_auth=DISCORD"
    },
    'profile_found': {
        'ru': 'Ваш профиль найден!',
        'en': 'Your profile has been found!',
    },
    'wallet_message': {
        'ru': "Добро пожаловать в SideKick!\nНажмите на Кошелек 🏦 для управления им.\nНажмите на Пополнить 💵 для добавления средств.\nНажмите на Баланс 📊 для просмотра вашего баланса USDT.",
        'en': "Welcome to SideKick!\nClick on Wallet 🏦 to manage it.\nClick on Top Up 💵 to add funds.\nClick on Balance 📊 to view your USDT balance."
    },
    'failed_invite': {
        'ru': 'Не удалось создать приглашение. Проверьте мои права и повторите попытку.',
        'en': 'Failed to create an invite. Please check my permissions and try again.',
    },
    'leaderboard_title': {
        'ru': 'Таблица лидеров!',
        'en': 'Leaderboard!',
    },
    'leaderboard': {
        'ru': 'Нажмите, чтобы посмотреть таблицу лидеров!',
        'en': 'Click to check the leaderboard!',
    },
    'order_dispatching_title': {
        'en': 'Your order is dispatching now',
        'ru': 'Ваш заказ обрабатывается'
    },
    'order_dispatching': {
        'ru': 'Как только исполнители примут заказ, их профили будут отправлены вам в личные сообщения.\n{link}',
        'en': 'Once there are Kickers accepting the order, their profile will be sent to you via DM.\n{link}'
    },
    'order_in_process': {
        'en': '🔴 Order in Process',
        'ru': '🔴 Заказ в процессе'
    },
    'order_successful': {
        'en': '✅ Order Successful',
        'ru': '✅ Заказ успешен'
    },
    'order_successful_description': {
        'en': '@{customer} Customer has successfully ordered @{kicker} Kicker',
        'ru': '@{customer} Пользователь успешно заказал @{kicker} Кикер'
    },
    'points_message': {
        'ru': "Для доступных задач нажмите ссылку ниже:\n{link}",
        'en': "For available tasks press the link below:\n{link}"
    },
    'subscribe_success': {
        'ru': "Вы успешно подписались на команду /order. Каждый раз, когда пользователь использует команду /order, вы будете получать уведомление.",
        'en': "You have successfully subscribed to the order command. Each time the /order command is used by users, you will receive a notification."
    },
    'unsubscribe_success': {
        'ru': "Вы отписались от команды /order.",
        'en': "You have unsubscribed from the order command."
    },
    'no_players': {
        'ru': "Извините, игроков нет.",
        'en': "Sorry, there are no players.",
    },
    'invite_join_guild': {
        'ru': "Чтобы получить доступ к вашему профилю, вы должны присоединиться к нашему основному серверу. Пожалуйста, присоединитесь, используя это приглашение: {invite_url}",
        'en': "You must join our main guild to access your profile. Please join using this invite: {invite_url}"
    },
    'order_summon_alert': {
        'ru': "Новый заказ: {task_desc}.\nУ вас новый заказ на {task_desc}.\nПримите, чтобы отправить ваш профиль пользователю.\nПожалуйста, присоединитесь к нашему серверу, используя ссылку ниже: {main_link}",
        'en': "New Order Summon Alert: {task_desc}.\nYou have a new order summon for a {task_desc}.\nAccept to send your profile to the user.\nPlease ensure to join our server using the link below: {main_link}"
    },
    'timeout_message': {
        'en': "🔔 Sorry, the dispatching countdown has ended.\n🔔 Your order cannot be completed.",
        'ru': "🔔 Извините, время обработки заказа истекло.\n🔔 Ваш заказ не может быть завершен."
    },
    'order_terminated': {
        'en': "🔴 Order Terminated",
        'ru': "🔴 Заказ завершен"
    },
    'you_requested_stop_summon': {
        'en': "🔔 You just requested to stop summoning kickers 👾",
        'ru': "🔔 Вы только что запросили остановить призыв кикеров 👾"
    },
    'already_pressed': {
        'ru': "Уже нажато",
        'en': "Already pressed"
    },
    'not_kicker': {
        'ru': "Вы не кикер!",
        'en': "You are not a kicker!"
    },
    'request_received': {
        'ru': "Заказчик получил ваш запрос!",
        'en': "The customer has received your request!"
    },
    'please_join': {
        'ru': "Пожалуйста, присоединитесь к серверу перед продолжением: {link}",
        'en': "Please join the server before proceeding: {link}"
    },
    'finished': {
        'ru': "Завершено",
        'en': "Finished"
    },
    'canceled': {
        'ru': "Отменено",
        'en': "Canceled"
    },
    'timeout_auto_refund': {
        'en': "Sorry, we haven't received your decision in 5 minutes. The funds will be automatically refunded to your wallet.",
        'ru': "Извините, мы не получили ваше решение в течение 5 минут. Средства будут автоматически возвращены на ваш кошелек."
    },
    'refund_button': {
        'en': "Refund",
        'ru': "Возврат"
    },
    'refund_requested': {
        'en': "The refund has been requested.",
        'ru': "Запрошен возврат средств."
    },
    'refund_success_customer': {
        'en': "Your funds will be refunded to your wallet soon! Until then, you can search for a new kicker.",
        'ru': "Ваши средства скоро будут возвращены на ваш кошелек! Тем временем вы можете искать нового исполнителя."
    },
    'replace_kicker': {
        'en': "Replace Kicker",
        'ru': "Заменить исполнителя"
    },
    'replace_requested': {
        'en': (
            "The replacement has been requested. "
            "Please wait while we are looking for a replacement kicker 🔁🎮"
        ),
        'ru': (
            "Запрошена замена исполнителя. "
            "Пожалуйста, подождите, пока мы найдем замену исполнителю."
        )
    },
    'next_user': {
        'ru': "Загружаем следующего пользователя...",
        'en': "Loading next user..."
    },
    'share_profile': {
        'ru': "Профиль аккаунта: {profile_link}",
        'en': "Profile account: {profile_link}"
    },
    'chat_user': {
        'ru': "Нажмите для связи с пользователем: {chat_link}",
        'en': "Click to connect with the user: {chat_link}"
    },
    'boost_user': {
        'ru': "Чтобы продвинуть профиль, перейдите по следующей ссылке: {boost_link}",
        'en': "To boost the profile go to the link below: {boost_link}"
    },
    'profile_not_found': {
        'ru': "Профиль не найден!",
        'en': "Profile not found!"
    },
    'no_user_found': {
        'ru': "Пользователь не найден для продвижения.",
        'en': "No user found to boost."
    },
    'no_valid_players': {
        'ru': "Не найдено ни одного действительного игрока.",
        'en': "No more valid players found."
    },
    'profile_not_found_message': {
        'ru': "Профиль не найден!",
        'en': "Profile not found!"
    },
    'share_profile_account': {
        'ru': "Профиль аккаунта: {profile_link}",
        'en': "Profile account: {profile_link}"
    },
    'sidekicker_account_not_posted': {
        'ru': "Аккаунт SideKicker еще не опубликован, пожалуйста, подождите или вы можете поделиться именем пользователя.",
        'en': "The SideKicker account is not posted yet, please wait or you can share the username."
    },
    'trial_chat_with_kicker': {
        'ru': "Пробный чат с кикером: <@!{user_id}>",
        'en': "Trial chat with the Kicker: <@!{user_id}>"
    },
    'connect_with_user': {
        'ru': "Нажмите ниже, чтобы связаться с пользователем: https://discord.com/users/{user_id}",
        'en': "Click below to connect with user: https://discord.com/users/{user_id}"
    },
    'chat_with_user': {
        'ru': "Чат с пользователем: {chat_link}",
        'en': "Chat with the user: {chat_link}"
    },
    'boost_profile_link': {
        'ru': "Чтобы продвинуть профиль, перейдите по следующей ссылке: {boost_link}",
        'en': "To boost the profile go to the link below: {boost_link}"
    },
    'no_user_found_to_boost': {
        'ru': "Пользователь не найден для продвижения.",
        'en': "No user found to boost."
    },
    'button_already_pressed': {
        'ru': "Кнопка уже была нажата.",
        'en': "Button has already been pressed."
    },
    'thank_you_customer': {
        'ru': "Спасибо за использование Sidekick!\nНадеюсь, вам понравилась сессия с <@{kicker}>.",
        'en': "Thank you for using Sidekick!\nHope you enjoyed the session with <@{kicker}>."
    },
    'thank_you_kicker': {
        'ru': "Спасибо за вашу службу! Средства будут вскоре переведены на ваш кошелек!",
        'en': "Thank you for your service! The funds will be transferred to your wallet soon!"
    },
    'support_ticket': {
        'ru': "Пожалуйста, создайте тикет в поддержку, чтобы получить помощь от нашей команды поддержки.",
        'en': "Please create a support ticket to get assistance from our customer support team."
    },
    'session_not_delivered': {
        'ru': "Пользователь <@{customer}> заявил, что сессия не была выполнена. Ваша сессия больше не действительна.",
        'en': "User <@{customer}> has stated that the session was not delivered. Your session is no longer valid."
    },
    "accept_session_message": {
        "en": "Thanks for accepting the session with {customer_name}!",
        "ru": "Спасибо за принятие сессии с {customer_name}!"
    },
    "reject_session_message": {
        "en": "You have rejected the session. The session is no longer valid.",
        "ru": "Вы отклонили сессию. Сессия больше не действительна."
    },
    "kicker_not_accepted_title": {
        "en": "Sorry, the kicker {kicker_name} has not accepted the session.",
        "ru": "Извините, кикер {kicker_name} не принял сессию."
    },
    "refund_replace_prompt": {
        "en": "Would you like to replace the kicker?",
        "ru": "Хотите ли вы заменить кикера?"
    },
    "success_check": {
        "en": "Great! You've successfully passed the availability check. Keep up the quick responses!",
        "ru": "Отлично! Вы успешно прошли проверку доступности. Продолжайте быстро отвечать!"
    },
    "late_response": {
        "en": "Oops! You clicked the button too late. Remember, quick response times help ensure a better experience for your clients.",
        "ru": "Упс! Вы нажали кнопку слишком поздно. Помните, что быстрые ответы помогают обеспечить лучший опыт для ваших клиентов."
    },
    "missed_check": {
        "en": "It looks like you missed the availability check. Please make sure to be responsive for a better service experience.",
        "ru": "Похоже, вы пропустили проверку доступности. Пожалуйста, постарайтесь быть отзывчивым для лучшего обслуживания."
    },
    "role_assigned_message": {
        "en": "Good job! You've been given a special role.",
        "ru": "Молодец! Вам была назначена специальная роль."
    },
    "role_assignment_failed": {
        "en": "Failed to assign role: {error}",
        "ru": "Не удалось назначить роль: {error}"
    },
    "role_not_found": {
        "en": "Role not found.",
        "ru": "Роль не найдена."
    },
    "edit_service_link": {
        "en": "To edit your service go to the link below: {link}",
        "ru": "Чтобы отредактировать вашу услугу, перейдите по ссылке ниже: {link}",
    },
    "create_service_link": {
        "en": "To create a new service go to the link below: {link}",
        "ru": "Чтобы создать новую услугу, перейдите по ссылке ниже: {link}",
    },
    "cooldown_message": {
        "en": "Please wait {hours} hours {minutes} minutes {seconds} seconds before sharing again.",
        "ru": "Пожалуйста, подождите {hours} часов {minutes} минут {seconds} секунд, прежде чем делиться снова."
    },
    "message_shared": {
        "en": "Message has been shared across all affiliate channels.",
        "ru": "Сообщение было отправлено во все каналы-партнеры."
    },
    'share_embed_title': {
        "en": "Username: {username}",
        "ru": "Имя пользователя: {username}"
    },
    'share_embed_description': {
        "en": "**Description:** {service_description}\n**Category:** {category}\n**Price:** ${price}",
        "ru": "**Описание:** {service_description}\n**Категория:** {category}\n**Цена:** ${price}"
    },
    "press_wallet_link": {
        "en": "Press the link to get access to the wallet: {url}",
        "ru": "Нажмите на ссылку, чтобы получить доступ к кошельку: {url}",
    },
    "press_top_up_link": {
        "en": "Press the link to get access to the top up: {url}",
        "ru": "Нажмите на ссылку, чтобы пополнить баланс: {url}",
    },
    "your_balance": {
        "en": "Your balance: {balance} USDT",
        "ru": "Ваш баланс: {balance} USDT",
    },
    "create_wallet_prompt": {
        "en": "Please create a crypto-wallet connected to your discord account via link: {url}",
        "ru": "Пожалуйста, создайте криптокошелек, связанный с вашей учетной записью Discord, по ссылке: {url}",
    },
    "waiting_for_response": {
        "ru": "Пользователь <@{customer_id}> ждет вашего ответа.\nПожалуйста, примите или отклоните сессию.",
        "en": "User <@{customer_id}> is waiting for your response.\nPlease accept or reject the session."
    },
    "failed_to_edit_message": {
        "ru": "Не удалось отредактировать предыдущее сообщение: {error}",
        "en": "Failed to edit previous message: {error}"
    },
    'failed_refund_payment': {
        "ru": "Не удалось вернуть платеж. Пожалуйста, попробуйте снова позже.",
        "en": "Failed to refund the payment. Please try again later."
    },
    "session_purchased": {
        "en": (
            "**Session has been purchased**\n"
            "User: {customer_name}\n"
            "Kicker: {kicker_name}\n"
            "Service: {service_name}\n"
            "Price: {service_price}\n"
        ),
        "ru": (
            "**Сессия была куплена**\n"
            "Пользователь: {customer_name}\n"
            "Кикер: {kicker_name}\n"
            "Услуга: {service_name}\n"
            "Цена: {service_price}\n"
        )
    },
    "order_sent": {
        "en": "🔔 Your order has been sent to Kicker {kicker_name} for confirmation.\n📥  If there is no response within 5 minute, you will not be charged your balance and will be able to replace the Kicker.",
        "eu": "🔔 Ваш заказ отправлен кикеру {kicker_name} для подтверждения.\n📥  Если в течение 5 минут не будет ответа, ваш баланс не будет списан, и вы сможете заменить кикера."
    },
    "order_confirmed": {
        "en": "✅ Order Confirmed",
        "ru": "✅ Заказ подтвержден"
    },
    "service_purchased_title": {
        "en": "Your service has been purchased:",
        "ru": "Ваша услуга была куплена:"
    },
    "service_details": {
        "en": "Service: {service_name}\nPrice: {service_price}\nPlease Accept or Reject the session",
        "ru": "Услуга: {service_name}\nЦена: {service_price}\nПожалуйста, примите или отклоните сессию"
    },
    "failed_to_send_message": {
        "en": "Failed to send message: {error}",
        "ru": "Не удалось отправить сообщение: {error}"
    },
    "kicker_reaction_test_message": {
        "en": "Hi {kicker_name}, we’re doing a quick check to see if you're available online. Please click the 'Check' button below within the next 5 minutes to pass the test.",
        "ru": "Привет {kicker_name}, мы проводим быструю проверку, доступен ли ты онлайн. Пожалуйста, нажми кнопку 'Check' внизу в течение следующих 5 минут, чтобы пройти тест."
    },
    "kicker_session_started_message_title": {
        "en": "**Your session has started:**",
        "ru": "**Ваша сессия началась:**\n"
    },
    "kicker_session_started_message": {
        "en": (
            "User: <@{challenger_id}>\n"
            "Username: {challenger_name}\n"
            "User discord id: {challenger_id}\n"
            "Service: {service_name}\n"
            "Reach out to the user as soon as possible:\n"
            "Connect via Direct message:<@{challenger_id}>\n"
        ),
        "ru": (
            "Пользователь: <@{challenger_id}>\n"
            "Имя пользователя: {challenger_name}\n"
            "Discord ID пользователя: {challenger_id}\n"
            "Услуга: {service_name}\n"
            "Свяжитесь с пользователем как можно скорее:\n"
            "Подключитесь через Личное сообщение:<@{challenger_id}>\n"
        )
    },
    "user_order_accepted_message": {
        "en": (
            "🔔 Kicker has accepted your order and now starts the service. 🎉\n"
            "📍 Kicker username: {challenged_name}\n"
            "📍 Kicker Discord ID: {challenged_id}\n"
            "📍 Service: XXX {service_name}\n"
            "📍 Connect via direct message :<@{challenged_id}>\n"
        ),
        "ru": (
            "🔔 Кикер принял ваш заказ и теперь начинает обслуживание. 🎉\n"
            "📍 Имя пользователя кикера: {challenged_name}\n"
            "📍 Discord ID кикера: {challenged_id}\n"
            "📍 Услуга: XXX {service_name}\n"
            "📍 Свяжитесь через личное сообщение:<@{challenged_id}>\n"
        )
    },
    "welcome_message": {
        "en": (
            "Welcome to the Sidekick Private Session Room!\n"
            "We hope you enjoy the games and the time spent together ❤️.\n"
            "If anything goes wrong, please create a ticket in our <#1233350206280437760> channel!\n"
            "Your Kicker's username is @{kicker_username}"
        ),
        "ru": (
            "Добро пожаловать в Приватную Комнату Сессий Сайдкика!\n"
            "Надеемся, вам понравится игра и время, проведенное вместе ❤️.\n"
            "Если что-то пойдет не так, пожалуйста, создайте заявку в нашем канале <#1233350206280437760>!\n"
            "Имя вашего Кикера @{kicker_username}"
        )
    },
    "session_started_message": {
        "en": (
            "Session has started\n"
            "Kicker: @{challenged.name}\n"
            "User: @{challenger.name}\n"
            "Please check this private channel: {invite_url}."
        ),
        "ru": (
            "Сессия началась\n"
            "Кикер: @{challenged.name}\n"
            "Пользователь: @{challenger.name}\n"
            "Пожалуйста, проверьте этот приватный канал: {invite_url}."
        )
    },
    "kicker_intro_message": {
        "en": (
            "👋 Hi there! Welcome to the Web3 Mastery Tutorial!\n"
            "I'm CZ, here to guide you through your first steps into an exciting world🌐✨\n"
            "Congratulations on successfully placing your order 🎉\n"
            "You've just unlocked the title of 'Web3 Master,' but the journey doesn't stop here.\n"
            "Go through the info we’ve shared here carefully and hit the 'I’ve learnt all the acknowledgments above' button to claim your campaign POINTS.\n"
            "Remember, the $4 you spent will be refunded back to your account at the end of the campaign. Keep an eye on your balance!\n"
            "Place more orders and boost your POINTs tally significantly.\n"
            "Watch here: [Exploring Sidekick: All You Need to Know!](https://youtu.be/h9fzscEdC1Y)\n"
            "Let's make your crypto journey rewarding 🚀"
        ),
        "ru": (
            "👋 Привет! Добро пожаловать в Учебник по Мастерству Web3!\n"
            "Я CZ, и я здесь, чтобы провести вас через ваши первые шаги в захватывающий мир🌐✨\n"
            "Поздравляем с успешным размещением заказа 🎉\n"
            "Вы только что разблокировали титул 'Мастер Web3', но путь на этом не заканчивается.\n"
            "Внимательно ознакомьтесь с информацией, которую мы здесь поделились, и нажмите кнопку 'Я изучил все упомянутые выше вещи', чтобы получить свои БАЛЛЫ кампании.\n"
            "Помните, что $4, которые вы потратили, будут возвращены на ваш счет в конце кампании. Следите за своим балансом!\n"
            "Размещайте больше заказов и значительно увеличивайте свой счет БАЛЛОВ.\n"
            "Смотрите здесь: [Изучение Сайдкика: все, что вам нужно знать!](https://youtu.be/h9fzscEdC1Y)\n"
            "Давайте сделаем ваше путешествие в криптовалюте полезным 🚀"
        )
    },
    "link_message": {
        "en": "To initiate a session with {username}, please click on the link: {invite_link}",
        "ru": "Чтобы начать сессию с {username}, пожалуйста, нажмите на ссылку: {invite_link}"
    },
    "profile_description": {
        "en": "Discord username: <@{discord_id}>\n\n {service_description}",
        "ru": "Имя пользователя Discord: <@{discord_id}>\n\n {service_description}"
    },
    "profile_thread_name": {
        "en": "Profile: <@{username}>",
        "ru": "Профиль: <@{username}>"
    },
    "interaction_prompt": {
        "en": "Click 'Go' to interact with this profile!",
        "ru": "Нажмите 'Перейти', чтобы взаимодействовать с этим профилем!"
    },
    "price_field": {
        "en": "Price",
        "ru": "Цена"
    },
    "price_value": {
        "en": "${price} /hour",
        "ru": "${price} /час"
    },
    "category_field": {
        "en": "Category",
        "ru": "Категория"
    },
    "languages_field": {
        "en": "Languages",
        "ru": "Языки"
    },
    "accept_button": {
        "en": "Accept",
        "ru": "Принять"
    },
    "payment_message": {
        "en": "To participate in this session, please complete your payment here: {payment_link}",
        "ru": "Чтобы участвовать в этой сессии, пожалуйста, завершите платеж здесь: {payment_link}"
    },
    "sidekick_card_message": {
        "en": "Your sidekick card has been sent to the user.",
        "ru": "Ваша карточка помощника была отправлена пользователю."
    },
    "profile_account_message": {
        "en": "Profile account: {profile_link}",
        "ru": "Профиль аккаунта: {profile_link}"
    },
    "not_posted_yet": {
        "en": "The SideKicker account is not posted yet, please wait or you can share the username.",
        "ru": "Аккаунт SideKicker еще не опубликован, пожалуйста, подождите или можете поделиться именем пользователя."
    },
    "trial_chat_link": {
        "en": "Trial chat with the Kicker: <@!{user_id}>",
        "ru": "Пробный чат с помощником: <@!{user_id}>"
    },
    "connect_chat_link": {
        "en": "Click below to connect with user https://discord.com/users/{user_id}",
        "ru": "Нажмите ниже, чтобы связаться с пользователем https://discord.com/users/{user_id}"
    },
    "payment_link": {
        "en": "Payment link: {payment_link}",
        "ru": "Ссылка на платеж: {payment_link}"
    },
    "stopped_notifications": {
        "en": "Stopped all notifications",
        "ru": "Остановлены все уведомления"
    },
    "kicker_informed": {
        "en": "Kicker Informed",
        "ru": "Помощник проинформирован"
    },
    "inform_kicker": {
        "en": "Inform Kicker",
        "ru": "Сообщить помощнику"
    },
    "points_leaderboard_message": {
        "en": (
            "Points Leaderboard {now}\n"
            "Check out the top 20 points leaderboard users!\n"
            "For the full leaderboard check it out here: {leaderboard_url}"
        ),
        "ru": (
            "Таблица лидеров по очкам {now}\n"
            "Посмотрите на 20 лучших пользователей таблицы лидеров по очкам!\n"
            "Полную таблицу лидеров можно посмотреть здесь: {leaderboard_url}"
        )
    },
    "leaderboard_score": {
        "en": "Score: {score}",
        "ru": "Очки: {score}"
    },
    "kicker_not_responded_yet": {
        "en": "The kicker has not responded yet.",
        "ru": "Исполнитель пока не ответил."
    },
    "private_channel_deleted": {
        "en": "Sorry, the private channel has been deleted.",
        "ru": "Приватный канал был удален."
    },
    "private_channel_created": {
        "en": (
            "Also We've created a private channel for you!\n"
            "First you need to join the server: {invite_link}\nand then I will send you an invite to the private channel"
        ),
        "ru": (
            "Мы так же создали приватный канал для вас!\n"
            "Но прежде вы должны вступить в данный сервер: {invite_link}\nи мы тут же пришлем вам приглашение на приватный канал, в котором покупатель уже ожидает вас!"
        )
    },
    "private_channel_invite": {
        "en": "Here is your invite link to the private channel: {invite_link}",
        "ru": "А вот и ссылочка на приватный канал с покупателем. Вас уже ждут! {invite_link}"
    },
    "bot_guild_join_message": {
        "ru": "@everyone\nХорошие новости! SideKick теперь добавлен на **{server_name}**! \n\nSideKick — это платформа для поиска партнеров по играм, где вы можете найти товарищей для игр или общения. Интересно? Начните с простой команды /go от бота SideKick!",
        "en": "@everyone\nGood News! SideKick is now added to **{server_name}**! \n\nSideKick is a match to play platform where you can find mates to play games or chat with you. Interested? Start with a simple /go command from SideKick bot!"
    },
    "guide_boost_command_message": {
        "ru": "Используйте команду /boost от SideKick, чтобы продвигать своего любимого игрока среди всех участников сервера.",
        "en": "Use SideKick /boost command to promote your favourite kicker to all server members."
    },
    "guide_go_command_message": {
        "ru": "Используйте команду /go от SideKick, чтобы начать быстрый матч для ВСЕХ онлайн игроков одним нажатием.",
        "en": "Use SideKick /go command to start a quick match for ALL online kickers in one click."
    },
    "guide_find_command_message": {
        "ru": "Используйте команду /find от SideKick, чтобы найти конкретного игрока и начать игру прямо сейчас!",
        "en": "Use SideKick /find command to find a specific kicker to start playing now!"
    },
    "guide_order_command_message": {
        "ru": "Используйте команду /order от SideKick, чтобы найти партнера для игры прямо сейчас!",
        "en": "Use SideKick /order command to match to play now!"
    },
    "guide_check_kickers_message": {
        "ru": "Посмотрите игроков на SideKick, которые ждут вас — используйте /go, чтобы начать их призыв и запустить свою собственную сессию прямо сейчас!",
        "en": "Check out the Kickers on Sidekick waiting for you - use /go to start summoning them and have your own session now!"
    },
    "order_from_webapp": {
        "en": "Order from WebApp",
        "ru": "Ордер с Веб Сайта"
    },
    "add_sidekick_to_your_server": {
        "en": "Add Sidekick to your server",
        "ru": "Добавьте Sidekick на свой сервер"
    },
    "points": {
        "en": "Points",
        "ru": "Очки"
    },
    "total_points": {
        "en": "Total Points",
        "ru": "Всего очков"
    },
    "leaderboard_ranking": {
        "en": "Leaderboard ranking",
        "ru": "Рейтинг в таблице лидеров"
    },
    "check_out_details": {
        "en": "Check out the details here",
        "ru": "Узнайте подробности здесь"
    },
    "invite_user_to_sidekick": {
        "en": "Invite user to the SideKick Server",
        "ru": "Пригласить друга на сервер SideKick"
    },
    "already_invited": {
        "en": "You have already been rewarded for inviting this user",
        "ru": "Вы уже были вознаграждены за приглашение этого пользователя"
    },
    "success_payment": {
        "en": "💰Your balance: {balance} USD.\n⌛️Service price: {amount} USD/hr.\n🔔Thank you for making the order!",
        "ru": "💰Ваш баланс: {balance} USD.\n⌛️Цена услуги: {amount} USD/час.\n🔔Спасибо за покупку!"
    },
    "server_error_payment": {
        "en": "Oops, something went wrong. Please try again...",
        "ru": "Упс, что-то пошло не так. Попробуйте позже..."
    },
    "not_enough_money_payment": {
        "en": "❗️Oops, you don’t have enough balance to complete this payment.\n💶 Top up via below methods to proceed with the purchase.",
        "ru": "❗️Упс, у вас недостаточно средств для завершения платежа.\n💶 Пополните баланс через нижеуказанные методы, чтобы продолжить покупку."
    },
    "top_up_message": {
        "en": "Your current Discord SideKick balance is {balance} USD.\nTop up your balance to enjoy services in one click through the following methods:",
        "ru": "Ваш текущий баланс в Discord SideKick составляет {balance} USD.\nПополните баланс, чтобы наслаждаться услугами в один клик, выбрав один из следующих способов:"
    },
    "opbnb_balance_message": {
        "en": "Here is your wallet **{wallet}**. Please top up opBNB USDT to this address.",
        "ru": "Ваш кошелёк **{wallet}**. Пожалуйста пополните opBNB USDT по этому адресу."
    },
    "welcome_message": {
        "en": "♥️ Welcome to use the SideKick App!\n🔊Introduction:\nSideKick is an order-based social platform where you can find your gaming partners and play, rank up, chat or socialize with girls or professional gamers at a price range of $1-$10. \nYou can choose any game to play with them. Alternatively, register as a Kicker using /profile and earn money through your gaming skills. \nYou can earn 85% commission by playing games or chatting with clients, providing emotional value, and easily make $1000 per month.\n🔔 Services include: Chatting, Valorant, League of Legends, CSGO, Apex Legends, Naraka, PUBG, TFT... Languages include: English, Russian, Arabic, Chinese. Countries include: Europe, UK, Middle East, Russia, and neighboring countries.\n🕹Commands：\n/order：take orders\n/go：search kickers\n/find：find kickers\n/profile：register as a kicker\nIntroduce:  #Introduction\nPlace Order:  /order+requirement in #order-lobby.\nYou can send gifts or complete special order pricing by sending the command /boost+Kicker Name in #boost-a-kicker\nYou can register to earn money as a companion in #Join us or by sending the command /profile\n\n🍧 Thousands of girls are online for chatting and gaming, and professional players are ready to enhance your skills.\n🧸 Register as a Kicker and earn $5-20 per hour by playing games, chatting, and improving skills with users!\n✅Discord Link：https://discord.gg/sidekick\n✅Twitter Link：https://x.com/sidekick_labs",
        "ru": "♥️ Добро пожаловать в приложение SideKick!\n🔊Введение:\nSideKick — это социальная платформа на основе заказов, где вы можете найти партнеров по играм, играть, повышать ранги, общаться с девушками или профессиональными игроками по цене от 1 до 10 долларов. \nВы можете выбрать любую игру для совместной игры. Или зарегистрируйтесь в качестве Кикера, используя /profile, и зарабатывайте, используя свои игровые навыки. \nВы получаете 85% комиссии, играя в игры или общаясь с клиентами, принося им эмоциональную ценность и легко зарабатывая $1000 в месяц.\n🔔 Услуги включают: общение, Valorant, League of Legends, CSGO, Apex Legends, Naraka, PUBG, TFT... Доступные языки: английский, русский, арабский, китайский. Страны: Европа, Великобритания, Ближний Восток, Россия и соседние страны.\n🕹Команды:\n/order：получить заказы\n/go：найти кикеров\n/find：искать кикеров\n/profile：зарегистрироваться как кикер\nВведение:  #Introduction\nРазместить заказ:  /order+требование в #order-lobby.\nВы можете отправить подарок или оформить заказ, отправив команду /boost+имя кикера в #boost-a-kicker\nВы можете зарегистрироваться, чтобы зарабатывать деньги в качестве компаньона, нажав #Join us или отправив команду /profile\n\n🍧 Тысячи девушек онлайн для общения и игр, и профессиональные игроки готовы помочь вам повысить навыки.\n🧸 Зарегистрируйтесь как Кикер и зарабатывайте $5-20 в час, играя в игры, общаясь и помогая пользователям повышать свои навыки!\n✅Ссылка на Discord: https://discord.gg/sidekick\n✅Ссылка на Twitter: https://x.com/sidekick_labs"
    },
    "top_up_address_message": {
        "en": "📥 This is your {method} top up address: **{wallet}**.\n🔔 After a successful top up, you will receive a DM confirmation.\n📍 You can also use /wallet again to check your updated balance.",
        "ru": "📥 Это ваш адрес для пополнения {method}: **{wallet}**.\n🔔 После успешного пополнения вы получите подтверждение в ЛС.\n📍 Вы также можете использовать /wallet снова, чтобы проверить ваш обновленный баланс."
    },
    "wallet_balance_message": {
        "en": "💶 Wallet Balance: **{balance} USD** \n📍 Wallet Address (opBNB / USDT)  🗃: {wallet}\n⬇️ Select the amount to top up:",
        "ru": "💶 Баланс кошелька: **{balance} USD** \n📍 Адрес кошелька (opBNB / USDT)  🗃: {wallet}\n⬇️ Выберите количество средств для пополнения баланса:"
    },
    "balance_topped_up_message": {
        "en": "Hey! Your balance has been topped up by **{amount} USDT**. Please enjoy using Sidekick! Wallet: **{wallet}**",
        "ru": "Привет! Ваш баланс пополнен на **{amount} USDT**. Приятного использования Sidekick! Кошелёк: **{wallet}**"
    },
    "not_suitable_message": {
        "en": "You don't have suitable services!",
        "ru": "У тебя нет подходящего серивса!"
    },
    "guide_message_1": {
        "en": "🔔Ordering process:\n\n🎈1. Use the following commands in ⁠#📥order-lobby and find your Kicker\n\n🕹 /order: Place an order for a service\n\n(Please clearly specify and describe the service/language/server/rank/requirements)\n\n🕹 /go: Summon available Kickers\n\n🕹 /find +SideKick Name: Find specific Kickers\n\n🕹 /boost+SideKick Name: Gift and support a Kicker\n\n🎮/profile: Register as a Kicker\n\n🎈2. Choose your favorite Kickers and click 'go' in the private bot message.\n\n🎈3. Click on the webpage to pay the price per order/hour\n\n(for other prices, complete with a /boost gift)\n\n🎈4. Go to the link sent to you by sidekick-bot to complete the game.",
        "ru": "🔔Процесс заказа:\n\n🎈1. Используйте следующие команды в ⁠#📥order-lobby, чтобы найти Кикера\n\n🕹 /order: Разместить заказ на услугу\n\n(Пожалуйста, четко укажите и опишите услугу/язык/сервер/ранг/требования)\n\n🕹 /go: Вызвать доступных Кикеров\n\n🕹 /find +Имя SideKick: Найти конкретного Кикера\n\n🕹 /boost+Имя SideKick: Подарить и поддержать Кикера\n\n🎮/profile: Зарегистрироваться как Кикер\n\n🎈2. Выберите понравившихся Кикеров и нажмите 'go' в личном сообщении бота.\n\n🎈3. Нажмите на веб-страницу, чтобы оплатить заказ/час\n\n(для других цен завершите с подарком /boost)\n\n🎈4. Перейдите по ссылке, отправленной вам ботом sidekick-bot, чтобы завершить игру."
    },
    "guide_message_2": {
        "en": "💛 Register as a Kicker Process:\n\n💫 1. Use /profile to register\n\nFill in your personal information and create your service (multiple options available)\n\n💫 2. Private message @Reviewer on the right side of Discord to schedule an interview\n\nAfter passing the interview, you can start taking orders.\n\n💫 3. Take orders in the lobby: #order-lobby-kicker and click the 'go' button to receive orders.",
        "ru": "💛 Процесс регистрации как Кикер:\n\n💫 1. Используйте команду /profile для регистрации\n\nЗаполните личную информацию и создайте свои услуги (доступны несколько вариантов)\n\n💫 2. Напишите личное сообщение @Reviewer справа в Discord для назначения собеседования\n\nПосле успешного прохождения собеседования вы сможете принимать заказы.\n\n💫 3. Принимайте заказы в лобби: #order-lobby-kicker и нажимайте кнопку 'go' для получения заказов."
    },
    "guide_message_3": {
        "en": "SideKick Introduce:\n\nSideKick is an order-based social platform where you can connect with gaming partners to play, rank up, learn, chat, or socialize with female gamers or professional players for $1-15. Choose any game and start playing together! 🎮\n\nMatch to play with a Kicker through Sidekick Bot!\n\nUse the following commands in ⁠#📥order-lobby and find your kicker\n\n🕹 /order: Place an order service\n\n🕹 /go: Summon available Kickers\n\n🕹 /find +SideKick Name: Find specific Kickers\n\n🕹 /boost+SideKick Name: Gift and support a Kicker\n\n🎮/profile: Register as a Kicker\n\n🍧 Thousands of female players are online for chatting and gaming, and professional players are ready to be your ally to enhance your skills.\n\nFollow our socials:\n\n✅ Discord Link：https://discord.gg/sidekick\n\n✅ Twitter Link：https://x.com/sidekick_labs\n\nAre you a passionate gamer?\n\nIf yes, and you are interested to offer your time and gaming expertise: Become a Kicker and earn 85% commission by playing or chatting, potentially making up to $1,000/month!\n\n🔔 Services: Chatting, Valorant, League of Legends, CSGO, and more\n\n🌍 Languages: English, Russian, Arabic, Chinese\n\n🌍 Regions: Europe, UK, Middle East, Russia\n\nTo register, visit ⁠#⭐️become-a-kicker for more info.",
        "ru": "Введение в SideKick:\n\nSideKick — это социальная платформа на основе заказов, где вы можете найти партнёров по играм для совместных игр, повышения ранга, обучения, общения или социализации с девушками-геймерами или профессиональными игроками за 1-15 долларов. Выберите любую игру и начните играть вместе! 🎮\n\nИграйте с Кикером через бота Sidekick!\n\nИспользуйте следующие команды в ⁠#📥order-lobby, чтобы найти Кикера\n\n🕹 /order: Разместить заказ на услугу\n\n🕹 /go: Вызвать доступных Кикеров\n\n🕹 /find +Имя SideKick: Найти конкретного Кикера\n\n🕹 /boost+Имя SideKick: Подарить и поддержать Кикера\n\n🎮/profile: Зарегистрироваться как Кикер\n\n🍧 Тысячи девушек-игроков готовы к общению и играм, а профессиональные игроки помогут вам улучшить навыки.\n\nСледите за нами в соцсетях:\n\n✅ Ссылка на Discord: https://discord.gg/sidekick\n\n✅ Ссылка на Twitter: https://x.com/sidekick_labs\n\nВы увлечены играми?\n\nЕсли да, и вы готовы предложить своё время и игровые навыки: Станьте Кикером и получайте 85% комиссии, играя или общаясь, зарабатывая до $1,000 в месяц!\n\n🔔 Услуги: общение, Valorant, League of Legends, CSGO и другие\n\n🌍 Языки: английский, русский, арабский, китайский\n\n🌍 Регионы: Европа, Великобритания, Ближний Восток, Россия\n\nДля регистрации посетите ⁠#⭐️become-a-kicker для получения дополнительной информации."
    },
    "task_completed_message": {
        "en": "Task Completed\nYou have successfully checked in today and 10 points have been granted!\nTotal Points: **{total_points}**",
        "ru": "Задача выполнена\nВы успешно отметились сегодня, и вам начислено 10 баллов!\nОбщее количество баллов: **{total_points}**"
    },
    "already_checked_in_message": {
        "en": "Oops! You have already checked in today. Please try again tomorrow!",
        "ru": "Упс! Вы уже отметились сегодня. Пожалуйста, попробуйте снова завтра!"
    },
    "first_join": {
        "en": "Just joined the server",
        "ru": "Присоединился к серверу"
    },
    "already_invited": {
        "en": "{member_name} User already invited.",
        "ru": "{member_name} Уже приглашен."
    },
    "invited_user_point": {
        "en": "Inviter: {inviter_mention} (`{inviter}` | `{inviter_id}`)\nCode: `{code}`\nUses: `{uses}`\nPoints: 100",
        "ru": "Приглашающий : {inviter_mention} (`{inviter}` | `{inviter_id}`)\nКод: `{code}`\nИспользует: `{uses}`\nОчки: 100"
    },
    "used_invite": {
        "en": "Used invite",
        "ru": "Был приглашен"
    },
    "link_invite_message": {
        "en": "{member_name} has been invited to the SideKick server with your invite link: https://discord.gg/{used_invite_code} and you've gained 100 points.\nCheck out https://app.sidekick.fans/tasks or use the /points command.",
        "ru": "{member_name} был приглашен на сервер SideKick по вашему приглашению : https://discord.gg/{used_invite_code} за это вы получаете 100 очков.\nПереходите по ссылке https://app.sidekick.fans/tasks или используйте комманду /points."
    },
    "invite_already_rewarded": {
        "en": "You have already been rewarded for inviting this user.",
        "ru": "Вы уже были вознаграждены за приглашение этого пользователя."
    },
    "task_records_name": {
        "en": "Used invite",
        "ru": "Был приглашен"
    },
    "task_records_value": {
        "en": "Invite details could not be retrieved. Please check manually.",
        "ru": "Не удалось получить данные приглашения. Пожалуйста, проверьте вручную."
    },
    "task_records_error": {
        "en": "Error tracking invite on member join: {e}",
        "ru":"Ошибка отслеживания приглашения при присоединении участника: {e}"
    },
    "task_records_error_name": {
        "en": "Error",
        "ru": "Ошибка"
    },
    "task_records_error_value": {
        "en": "Failed to track invite usage.",
        "ru": "Не удалось отследить использование приглашения."
    },
    "guild_join_inviter": {
        "en": "You can receive points when the SideKick bot added to servers with 100 or more members.",
        "ru": "Вы можете получить очки когда SideKick бот добавит вас на сервер, где есть как минимум 100 участников."
    },
    "guild_bot_is_added" : {
        "en": "The SideKick bot has already been added to this server.",
        "ru": "SideKick бот уже добавлен на сервер."
    },
    "guild_reward_adding" : {
        "en": "You have already been rewarded for adding the SideKick bot to this server.",
        "ru": "Вы уже получили награду за добавление SideKick бота на этот сервер. "
    },
    "guild_bot_added_title": {
        "en" : "Bot added to server",
        "ru" : "Бот добавлен на сервер"
    },
    "guild_sidekick_app_added" : {
        "en": "The SideKick App has just been added to the server {guild_name} successfully and you’ve gained 1000 points.\nCheck out https://app.sidekick.fans/tasks or with the /points command.",
        "ru": "Приложение Sidekick было успешно добавлено на сервер {guild_name} получено 1000 очков\nПереходите по ссылке https://app.sidekick.fans/tasks или используйте команду /points command."
    },
    "guild_sidekick_app_added_full_title": {
        "en": "Bot added to the server",
        "ru": "Бот добавлен на сервер"
    },
    "guild_sidekick_app_added_full": {
        "en":"The SideKick App has just been added to the server {guild_name}.\nInviter: {inviter_mention} (`{inviter}` | `{inviter_id}`)\nPoints: 1000",
        "ru":"Приложение Sidekick только что было добавлено на сервер {guild_name}.\nПригласил: {inviter_mention} (`{inviter}` | `{inviter_id}`)\nОчки: 1000"
    },
    "public_boost_announcement_message": {
        "en": "@{username} has just boosted @{kickername} by {amount}. Let's celebrate!\nCheck it out in {link}",
        "ru": "@{username} только что поддержал @{kickername} на сумму {amount}. Давайте отпразднуем! Проверь в {link}"
    },
    "boost_question": {
        "en": "Are you sure to boost @{username} with **{amount} USD** ?",
        "ru": "Вы уверены что хотите забустить @{username} на сумму **{amount} USD** ?"
    },
    "thanks_for_placing_order": {
        "en": "🎟Thanks for placing an order",
        "ru": "🎟Спасибо за размещение заказа"
    },
    "thanks_for_placing_order_description": {
        "en": "While you wait for the order dispatch, please make sure you have 💰sufficient balance💰 on your account.\nYou may 💶top up💶 using the following methods.\nYour balance: {balance} 💰",
        "ru": "Пока вы ждете отправку заказа, убедитесь, что у вас есть 💰достаточный баланс💰 на вашем счету.\nВы можете 💶пополнить💶 с помощью следующих методов.\nВаш баланс: {balance} 💰"
    },
    "final_boost_step_title": {
        "en": "Final step!",
        "ru": "Последний шаг!"
    },
    "final_boost_step_message": {
        "en": "Only one step left to boost **{username}** by **{amount} USD**. Just click the button! 👇🏻",
        "ru": "Остался последний шаг, чтобы забустить **{username}** на сумму **{amount} USD**. Просто нажми на кнопку! 👇🏻"
    },
    "session_accepted_message": {
        "en": "Thanks for accepting the session with @{discord_user}!",
        "ru": "Спасибо за принятие сессии с @{discord_user}!"
    }
}
