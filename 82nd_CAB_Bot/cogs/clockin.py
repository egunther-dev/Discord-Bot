import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class Clockin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.time_logs = {}  # {user_id: {"clock_in": datetime, "total_time": timedelta, "log": [(datetime, duration)], "task": asyncio.Task}}
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Clockin command online!")

    @app_commands.command(name="clockin", description="Use to clock time for promotions!")
    async def clockin(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.now()

        if user_id in self.time_logs and "clock_in" in self.time_logs[user_id]:
            await interaction.response.send_message(f"You are already clocked in, {interaction.user.mention}.", ephemeral=True)
            return

        self.time_logs.setdefault(user_id, {"log": []})["clock_in"] = now
        await interaction.response.send_message(f"You have clocked in! {interaction.user.mention}", ephemeral=False)

        # Start auto clockout
        self.time_logs[user_id]["task"] = asyncio.create_task(self.auto_clockout(user_id))

    async def auto_clockout(self, user_id):
        try:
            await asyncio.sleep(30)
            if user_id in self.time_logs and "clock_in" in self.time_logs[user_id]:
                clock_in_time = self.time_logs[user_id].pop("clock_in")
                duration = datetime.now() - clock_in_time

                total_time = self.time_logs[user_id].get("total_time", timedelta())
                self.time_logs[user_id]["total_time"] = total_time + duration

                # Log the session
                self.time_logs[user_id]["log"].append((clock_in_time, duration))

                # Fetch the user
                user = self.bot.get_user(user_id)
                if user:
                    try:
                        await user.send(f"**Auto Clockout:** You have been clocked out after 30 seconds. \nSession Duration: {str(duration).split('.')[0]}.")
                    except discord.Forbidden:
                        print(f"Could not DM {user.name}, they may have DMs disabled.")
        except asyncio.CancelledError:
            # If the task is canceled (manual clockout), exit silently
            return

    @app_commands.command(name="clockout", description="Clock out to log activity!")
    async def clockout(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.now()

        if user_id not in self.time_logs or "clock_in" not in self.time_logs[user_id]:
            await interaction.response.send_message(f"You are not currently clocked in, {interaction.user.mention}.", ephemeral=True)
            return

        clock_in_time = self.time_logs[user_id].pop("clock_in")
        duration = now - clock_in_time

        total_time = self.time_logs[user_id].get("total_time", timedelta())
        self.time_logs[user_id]["total_time"] = total_time + duration

        # Log the session
        self.time_logs[user_id]["log"].append((clock_in_time, duration))

        # Cancel auto clockout task if it's still running
        if "task" in self.time_logs[user_id]:
            self.time_logs[user_id]["task"].cancel()
            del self.time_logs[user_id]["task"]

        await interaction.response.send_message(
            f"Clocked out! Thank you {interaction.user.mention}. "
            f"Session duration: {str(duration).split('.')[0]}.", ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Clockin(bot))