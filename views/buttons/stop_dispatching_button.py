import discord


class StopDispatchingButton(discord.ui.Button):
    def __init__(self, *, order_view: discord.ui.View, order_dm_view: discord.ui.View):
        super().__init__(label="Stop Dispatching", style=discord.ButtonStyle.danger, custom_id="stop_dispatching")
        self.order_view = order_view
        self.order_dm_view = order_dm_view

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.response.edit_message(view=self.order_dm_view)
        await self.order_view.on_timeout(stop_button_pressed=True)
