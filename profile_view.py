import discord
import os

class ProfileView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout=None if you don't want the buttons to expire
        self.add_item(discord.ui.Button(label="Go to Profile", url=f"{os.getenv('WEB_APP_URL')}/profile", style=discord.ButtonStyle.url))

class WalletView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Go to Wallet", url=f"{os.getenv('WEB_APP_URL')}/manage", style=discord.ButtonStyle.url))
