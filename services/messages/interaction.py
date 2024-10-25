import discord


async def send_interaction_message(
    *,
    interaction: discord.Integration,
    message: str,
    view: discord.ui.View = None
) -> None:
    kwargs = {
        "content": message,
        "ephemeral": True
    }
    if view:
        kwargs["view"] = view
    try:
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(**kwargs)