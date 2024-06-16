import discord

class ProfileView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout=None if you don't want the buttons to expire
        self.add_item(discord.ui.Button(label="Go to Profile", url="https://sidekick.fans/dashboard", style=discord.ButtonStyle.url))
