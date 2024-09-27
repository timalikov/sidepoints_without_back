import threading
import asyncio
from typing import Any, List

import discord

from services.schedule_tasks.base import BaseScheduleTask

from bot_instance import get_bot

bot = get_bot()


class PeriodicRefundReplace(BaseScheduleTask):
    ...


periodic_refund_replace = PeriodicRefundReplace()
