import traceback
import sys
from discord.ext import commands

from bot_instance import get_bot

from services.exceptions import PaymentException
from services.messages.interaction import send_interaction_message

bot = get_bot()


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, interaction, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        interaction: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """
        if hasattr(interaction.command, 'on_error'):
            return

        cog = interaction.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return
        
        if isinstance(error, commands.CommandNotFound):
            await send_interaction_message(
                interaction=interaction,
                message=f"Command **{error.name}** not found."
            )
            return
        
        elif isinstance(error, commands.CommandOnCooldown):
            await send_interaction_message(
                interaction=interaction,
                message=f"Command cooldown. Please wait {round(error.retry_after, 2)} seconds."
            )
            return
        
        elif isinstance(error, commands.DisabledCommand):
            await interaction.send(f'{interaction.command} has been disabled.')
        
        elif isinstance(error, PaymentException):
            await send_interaction_message(
                interaction=interaction,
                message=f"Payment error **[Status {error.status_code}]**. {error.message}"
            )
            
        else:
            await send_interaction_message(
                interaction=interaction,
                message="What's wrong?..."
            )
            print('Ignoring exception in command {}:'.format(interaction.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
