from typing import Literal
import discord

from translate import translations


class InformKickerButton(discord.ui.View):
    def __init__(self, kicker: discord.User, lang: Literal["ru", "en"] = "en"):
        super().__init__(timeout=None)
        self.kicker = kicker
        self.informed = False
        self.lang = lang

    @discord.ui.button(label="Inform Kicker", style=discord.ButtonStyle.primary, custom_id="inform_kicker_button")
    async def inform_kicker(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.informed:
            button.label = translations["kicker_informed"][self.lang]
            button.style = discord.ButtonStyle.success
            button.disabled = True
            self.informed = True

            await interaction.response.edit_message(view=self)
