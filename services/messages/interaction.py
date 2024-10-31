import discord


async def send_interaction_message(
    *,
    interaction: discord.Integration,
    message: str = None,
    view: discord.ui.View = None,
    embed: discord.Embed = None
) -> None:
    kwargs = {"ephemeral": True}
    if message:
        kwargs["content"] = message
    if view:
        kwargs["view"] = view
    if embed:
        kwargs["embed"] = embed
    try:
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(**kwargs)