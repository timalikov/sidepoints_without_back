from config import RU_GUILDS


def get_lang_prefix(guild_id: int) -> str:
    return "ru" if guild_id in RU_GUILDS else "en"


translations = {
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
        'ru': 'Новый заказ: **{choice}** [30 минут]\nУ вас новый заказ на **{choice}** на русском языке.',
        'en': 'New Order Alert: **{choice}** [30 minutes]\nYou have a new order for a **{choice}** in English.'
    },
    'profile_not_created': {
        'ru': "Похоже, вы еще не создали профиль! Пожалуйста, перейдите по ссылке, чтобы создать профиль.\n{link}/profile?side_auth=DISCORD",
        'en': "Looks like you haven't created a profile with us! Please click the link below to create your profile.\n{link}/profile?side_auth=DISCORD"
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
    'order_dispatching': {
        'ru': 'Ваш заказ обрабатывается. Как только исполнители примут заказ, их профили будут отправлены вам в личные сообщения.\n{link}',
        'en': 'Your order is dispatching now. Once there are Kickers accepting the order, their profile will be sent to you via DM.\n{link}'
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
        'ru': "Извините, время ожидания истекло, и ваш заказ не был выполнен успешно.",
        'en': "Sorry, the dispatching countdown has ended and your order has not been completed successfully."
    },
    'already_pressed': {
        'ru': "Уже нажато",
        'en': "Already pressed"
    },
    'not_kicker': {
        'ru': "Вы не кикер!",
        'en': "You are not kicker!"
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
            "We have also issued a refund for this service to you. "
            "Please wait while we look for a replacement kicker."
        ),
        'ru': (
            "Запрошена замена исполнителя. "
            "Мы также оформили возврат средств за эту услугу. "
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
        "en": "Would you like a refund or replace the kicker?",
        "ru": "Хотите ли вы возврат средств или заменить кикера?"
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
        "en": "Your order has been sent to kicker {kicker_name}.\nIf there is no response within 1 minute, you will be able to replace the kicker, or refund the money.",
        "ru": "Ваш заказ отправлен кикеру {kicker_name}.\nЕсли не будет ответа в течение 1 минуты, вы сможете заменить кикера или вернуть деньги."
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
    "kicker_session_started_message": {
        "en": (
            "**Your session has started:**\n"
            "User: <@{challenger_id}>\n"
            "Username: {challenger_name}\n"
            "Service: {service_name}\n"
            "Reach out to the user as soon as possible:\n"
            "Connect via Direct message:<@{challenger_id}>\n"
        ),
        "ru": (
            "**Ваша сессия началась:**\n"
            "Пользователь: <@{challenger_id}>\n"
            "Имя пользователя: {challenger_name}\n"
            "Услуга: {service_name}\n"
            "Свяжитесь с пользователем как можно скорее:\n"
            "Подключитесь через Личное сообщение:<@{challenger_id}>\n"
        )
    },
    "user_order_accepted_message": {
        "en": (
            "Kicker has accepted your order:\n"
            "Kicker: <@{challenged_id}>\n"
            "Kicker username: {challenged_name}\n"
            "Service: {service_name}\n"
            "Connect via Direct message:<@{challenged_id}>\n"
        ),
        "ru": (
            "Кикер принял ваш заказ:\n"
            "Кикер: <@{challenged_id}>\n"
            "Имя кикера: {challenged_name}\n"
            "Услуга: {service_name}\n"
            "Подключитесь через Личное сообщение:<@{challenged_id}>\n"
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
    }
}
