import discord
from discord import app_commands
from discord.ext import commands


class Training_Fail(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Training cog is online!")

    @app_commands.command(name="training_fail", description="Log a training pass between a trainer and trainee.")
    @app_commands.describe(
        trainer="Select the trainer",
        trainee="Select the trainee",
        aircraft_type="Select the aircraft used in certification"
    )
    @app_commands.choices(
        aircraft_type=[
            app_commands.Choice(name="HH-60", value="helocopter"),
            app_commands.Choice(name="F-16C/D", value="fixed_wing_fighter"),
            app_commands.Choice(name="F-15C", value="fixed_wing_fighter"),
            app_commands.Choice(name="F-15E", value="fixed_wing_cas"),
            app_commands.Choice(name="C-130J", value="cargo"),
        ]
    )
    async def training_pass(
        self,
        interaction: discord.Interaction,
        trainer: discord.User,
        trainee: discord.User,
        aircraft_type: app_commands.Choice[str],
    ):
        
        await interaction.response.send_message(
            content=(
                f"Training Logged:\n"
                f"**Trainer:** {trainer.mention}\n"
                f"**Trainee:** {trainee.mention}\n"
                f"**Aircraft Type:** {aircraft_type.name}\n"
                f"**Pass of Fail: Fail**"
            ),
            ephemeral=False,  
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Training_Fail(bot))