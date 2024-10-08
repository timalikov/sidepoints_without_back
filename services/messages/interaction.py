import discord


async def send_interaction_message(*, interaction: discord.Integration, message: str) -> None:
    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(message, ephemeral=True)