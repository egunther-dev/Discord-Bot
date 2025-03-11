import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View


class RoleDropdown(Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(label=role.name,value = str(role.id), description="Assigns Role")
            for role in roles if role is not None
        ]
        super().__init__(
            placeholder = "Choose a role...",
            min_values = 1,
            max_values = 1,
            options=options
        )
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        role_id = int(self.values[0])
        guild = interaction.guild
        role = guild.get_role(role_id)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            feedback_message = f"Removed the {role.name} role from you!"
        else:
            await interaction.user.add_roles(role)
            feedback_message = f"Added the {role.name} role from you!"

        self.placeholder = "Choose another role..."
        await interaction.edit_original_response(content="Select what aircraft you'd like:", view=self.view)
        await interaction.followup.send(content=feedback_message, ephemeral=True)


class Request(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @app_commands.command(name = "roles", description = "Select a role from the dropdown:")
    async def roles(self, interaction: discord.Interaction):
        
        role_ids = [
            1329280871005425734, 
            1329281192700149760, 
            1329281226200186921, 
            1329281224325337098, 
            1329281227617996810, 
            1329280869780819968, 
            1329281234119032832,
            1329281230989955114,
            1329281235868057691,
            1329281239651450993,
            1329281229413154849,
            1329281249654607872,
            1329281247968493671,
            1329281251345039391,
            1329281241232576563,
            1329281237755363338,
            1329281246353686528,
            1329281242822344724,
            1329281260354273384,
            1329281253026828409,
            1329281254679380030,
            1329281261935661176,
            1329281232508420116
        ]
        guild_roles = [interaction.guild.get_role(role_id) for role_id in role_ids]
        valid_roles = [role for role in guild_roles if role is not None]
        dropdown = RoleDropdown(valid_roles)
        view = View()
        view.add_item(dropdown)

        await interaction.response.send_message("Use the dropdown to select which aircraft you want to be certified in:", view = view)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online!")

async def setup(bot):
    await bot.add_cog(Request(bot))