import discord
from discord import app_commands
from play_view import PlayView
from profile_view import ProfileView
from bot_instance import get_bot
from background_tasks import delete_old_channels, post_user_profiles, delete_all_threads_and_clear_csv
#post_weekly_leaderboard

#delete_all_threads_and_clear_csv
from config import MAIN_GUILD_ID, DISCORD_BOT_TOKEN
from sql_order import Order_Database

main_guild_id = MAIN_GUILD_ID
bot = get_bot()
##### To get list of users who are currently online #####
async def list_online_users(guild):
    if guild is None:
        return []
    online_members = [member for member in guild.members if str(member.status) == 'online']
    online_member_ids = [member.id for member in online_members]
    return online_member_ids

@bot.tree.command(name="profile", description="Use this command if you wish to be part of the Sidekick Playmates network.")
async def profile(interaction: discord.Interaction):
    # guild = bot.get_guild(main_guild_id)
    # if guild is None:
    #     await interaction.response.send_message("Error: Main guild not found.", ephemeral=True)
    #     return

    guild = interaction.guild
    # Check if the user is a member of the guild
    member = guild.get_member(interaction.user.id)
    if member:
        # print("HE IS A MEMBER")
        view = ProfileView()
        await interaction.response.send_message("Welcome onboard!\nClick on go to profile to set up or edit your profile", view=view, ephemeral=True)
        return
    else:
        await interaction.response.defer(ephemeral=True)
        # Generate an invite link if the user is not in the guild
        try:
            # Create an invite that expires in 24 hours with a maximum of 10 uses
            invite = await guild.text_channels[0].create_invite(max_age=86400, max_uses=10, unique=True)
            await interaction.response.send_message(f"You must join our main guild to access your profile. Please join using this invite: {invite.url}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Failed to create an invite. Please check my permissions and try again.", ephemeral=True)
            print(e)  # For debugging purposes


async def list_all_users_with_online_status(guild):
    if guild is None:
        return []
    all_member_ids = [member.id for member in guild.members]
    # online_member_ids = [member.id for member in guild.members if str(member.status) == 'online']
    return all_member_ids

@bot.tree.command(name="go", description="Use this command and start looking for playmates!")
@app_commands.choices(choices=[app_commands.Choice(name="All players", value="ALL"),
                               app_commands.Choice(name="Buddy", value="57c86488-8935-4a13-bae0-5ca8783e205d"),
                               app_commands.Choice(name="Coaching", value="88169d78-85b4-4fa3-8298-3df020f13a6f"),
                               app_commands.Choice(name="Chatting", value="2974b0e8-69de-4d7c-aa4d-d5aa8e05d360"),
                               app_commands.Choice(name="Mobile", value="439d8a72-8b8b-4a56-bb32-32c6e5d918ec")
                               ])
async def play(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    view = PlayView(user_choice=choices.value)
    if view.no_user:
        await interaction.followup.send(content="Sorry, there are no players.", ephemeral=True)
    else:
        await interaction.followup.send(embed=view.profile_embed, view=view, ephemeral=True)


@bot.tree.command(name="find", description="Find a user profile by their username.")
@app_commands.describe(username="The username to find.")
async def find(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    view = PlayView(user_choice="ALL", username=username)
    if view.no_user:
        await interaction.followup.send(content="Sorry, there are no players.", ephemeral=True)
    else:
        await interaction.followup.send(embed=view.profile_embed, view=view, ephemeral=True)

async def get_guild_invite_link(guild_id):
    guild = bot.get_guild(guild_id)
    if guild:
        # Create an invite link
        invite = "https://discord.gg/sidekick"  # Expires in 1 day, 1 use
        return invite
    return None

@bot.tree.command(name="order", description="Use this command to post your service request and summon Kickers to take the order.")
@app_commands.choices(choices=[app_commands.Choice(name="Buddy", value="57c86488-8935-4a13-bae0-5ca8783e205d"),
                               app_commands.Choice(name="Coaching", value="88169d78-85b4-4fa3-8298-3df020f13a6f"),
                               app_commands.Choice(name="Chatting", value="2974b0e8-69de-4d7c-aa4d-d5aa8e05d360"),
                               app_commands.Choice(name="Mobile", value="439d8a72-8b8b-4a56-bb32-32c6e5d918ec")
                               ])
async def order(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    order_data = {
        'user_id': interaction.user.id,
        'task_id': choices.value
    }
    await Order_Database.set_user_data(order_data)
    main_link = await get_guild_invite_link(MAIN_GUILD_ID)
    await interaction.followup.send(f"Your Kickers summon order successfully placed. \nPlease check your DM for Kicker summon responses. Please wait further instructions and join to our server using the link below\n{main_link}", ephemeral=True)


@bot.event
async def on_ready():
    # delete_old_channels.start()
    # post_weekly_leaderboard.start()
    await bot.tree.sync()
    await delete_all_threads_and_clear_csv()
    post_user_profiles.start()
    print(f'We have logged in as {bot.user}')

def run():
    bot.run(DISCORD_BOT_TOKEN)
