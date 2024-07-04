import discord

class ProfileView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout=None if you don't want the buttons to expire
        self.add_item(discord.ui.Button(label="Go to Profile", url="https://app.sidekick.fans/profile", style=discord.ButtonStyle.url))


class WalletView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Go to Wallet", url="https://app.sidekick.fans/manage", style=discord.ButtonStyle.url))
