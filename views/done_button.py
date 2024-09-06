import discord


class DoneButton(discord.ui.View):
    def __init__(self):
        # Setting timeout=None to make the button non-expirable
        super().__init__(timeout=None)

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Fetch the role from the guild using the provided role ID
        role_ids = [1235556503596040224, 1242457735988252692]  # Role ID to be assigned
        # role = interaction.guild.get_role(role_id)

        # Fetch the first valid role from the guild using the provided role IDs
        role = None
        for role_id in role_ids:
            role = interaction.guild.get_role(role_id)
            if role:
                break

        if role:
            # Add the role to the user who clicked the button
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("Good job! You've been given a special role.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Failed to assign role: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message("Role not found.", ephemeral=True)
