import discord
from discord import app_commands
from discord.ext import commands
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets Setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "training-pass-448023-0da9bd2745bc.json" 

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16nKruiXt_EmCQ5_nJvM2z_FM3tz85TNR-CS2GkKHNhY/edit#gid=487053636"
spreadsheet = gc.open_by_url(SPREADSHEET_URL)
sheet = spreadsheet.get_worksheet(2)  # Ensure this selects the correct worksheet


class Roster(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Roster cog is online!")

    @app_commands.command(name="onboard", description="Add a new person to the roster.")
    @app_commands.describe(personnel_number="Enter the personnel number", name="Enter the person's name")
    async def onboard(self, interaction: discord.Interaction, personnel_number: str, name: str):
        """Adds a new person to the Google Sheet"""
        await interaction.response.defer(ephemeral=True)

        # Find first available row
        all_values = sheet.get_all_values()
        for row_idx, row in enumerate(all_values, start=1):
            if not any(row):  # Empty row found
                sheet.update(f"A{row_idx}", [[name, personnel_number]])  # Fill name and personnel number
                sheet.update(f"C{row_idx}:D{row_idx}", [[True, True]])  # Set UH-60A and HH-60G to True
                await interaction.followup.send(f"{name} has been onboarded successfully!", ephemeral=True)
                return

        await interaction.followup.send("No available rows found.", ephemeral=True)

    @app_commands.command(name="promote", description="Promote a person to the next rank.")
    @app_commands.describe(name="Enter the name of the person being promoted", new_rank="Enter their new rank")
    async def promote(self, interaction: discord.Interaction, name: str, new_rank: str):
        """Promotes a person to a new rank in Google Sheets"""
        await interaction.response.defer(ephemeral=True)

        # Fetch all rows
        all_values = sheet.get_all_values()

        # Find person in the sheet
        person_row = None
        for row_idx, row in enumerate(all_values, start=1):
            if row and row[0].strip().lower() == name.lower():
                person_row = row_idx
                break

        if not person_row:
            await interaction.followup.send(f"Person **{name}** not found in roster.", ephemeral=True)
            return

        personnel_number = sheet.cell(person_row, 2).value
        boolean_values = sheet.row_values(person_row)[2:]

        # Find first available row for new rank
        new_row = None
        for row_idx, row in enumerate(all_values, start=1):
            if row and row[0].strip().lower() == new_rank.lower():
                new_row = row_idx + 1  # First available below this rank
                while new_row < len(all_values) and any(all_values[new_row]):
                    new_row += 1
                break

        if not new_row:
            await interaction.followup.send(f"No available slot for rank **{new_rank}**.", ephemeral=True)
            return

        # Move person to new rank
        sheet.update(f"A{new_row}:B{new_row}", [[name, personnel_number]])
        sheet.update(f"C{new_row}:Z{new_row}", [boolean_values])  # Transfer all booleans

        # Clear old row
        sheet.update(f"A{person_row}:Z{person_row}", [["" for _ in range(len(all_values[0]))]])  # Clears row
        sheet.update(f"C{person_row}:Z{person_row}", [[False] * (len(boolean_values))])  # Reset booleans

        await interaction.followup.send(f"**{name}** has been promoted to **{new_rank}**!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Roster(bot))