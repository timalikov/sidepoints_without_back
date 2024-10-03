import discord
from typing import Literal

from translate import translations

class DoneButton(discord.ui.View):
    def __init__(self, lang: Literal["ru", "en"] = "en"):
        super().__init__(timeout=None)
        self.lang = lang

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Fetch the role from the guild using the provided role ID
        role_ids = [1235556503596040224, 1242457735988252692]
        role = None
        for role_id in role_ids:
            role = interaction.guild.get_role(role_id)
            if role:
                break

        if role:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(translations["role_assigned_message"][self.lang], ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(translations["role_assignment_failed"][self.lang].format(error=str(e)), ephemeral=True)
        else:
            await interaction.response.send_message(translations["role_not_found"][self.lang], ephemeral=True)
