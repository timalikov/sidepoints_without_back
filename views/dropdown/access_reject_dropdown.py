from typing import List, Literal

import discord

from message_constructors import create_profile_embed


class OrderAccessRejectDropdown(discord.ui.Select):
    def __init__(
        self,
        *,
        services: List[dict],
        default_service: dict,
        lang: Literal["en", "ru"] = "en"
    ):
        self.services = services
        options = [
            discord.SelectOption(
                label=service["tag"] + " - " + str(service["service_price"]) + "$",
                description=(
                    service["service_description"]
                    if len(service["service_description"]) < 95
                    else service["service_description"][:90] + "..."
                ),
                value=index,
                default=True if service == default_service else False
            )
            for index, service in enumerate(services)
        ]
        self.lang = lang
        super().__init__(placeholder="Select service...", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])
        service = self.services[index]
        self.view.service = service
        embed = create_profile_embed(profile_data=service, lang=self.lang)
        embed.set_footer(text="The following Kicker has responded to your order. Click Go if you want to proceed.")
        for option in self.options:
            option.default = (str(option.value) == str(index))
        await interaction.response.edit_message(
            embed=embed,
            view=self.view
        )
