import discord


async def send_interaction_message(
    *,
    interaction: discord.Integration,
    message: str = None,
    view: discord.ui.View = None,
    embed: discord.Embed = None,
    ephemeral: bool = True
) -> discord.Message:
    kwargs: dict = {}
    if ephemeral:
        kwargs["ephemeral"] = ephemeral
    if message:
        kwargs["content"] = message
    if view:
        kwargs["view"] = view
    if embed:
        kwargs["embed"] = embed
    try:
        if interaction.response.is_done():
            message = await interaction.followup.send(**kwargs)
        else:
            message = await interaction.response.send_message(**kwargs)
    except (discord.errors.InteractionResponded, discord.DiscordException):
        message = await interaction.followup.send(**kwargs)
    return message