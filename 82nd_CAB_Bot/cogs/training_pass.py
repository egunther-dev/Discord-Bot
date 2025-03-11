import discord
from discord import app_commands
from discord.ext import commands
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "training-pass-448023-0da9bd2745bc.json" 


credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)


SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16nKruiXt_EmCQ5_nJvM2z_FM3tz85TNR-CS2GkKHNhY/edit#gid=487053636"
spreadsheet = gc.open_by_url(SPREADSHEET_URL)
sheet = spreadsheet.get_worksheet(2)  


AIRCRAFT_COLUMN_MAP = {
    "UH-60A": 7,
    "HH-60G": 8,
    "CH-47D": 9,
    "AH-64E": 10,
    "OH-58D": 11,
    "F-15E": 12,
    "F-15C": 13,
    "F-16C": 14,
    "F-35A": 15,
    "F-22A": 16,
    "A-10C": 17,
    "C-130": 18,
    "AC-130J": 19,
    "C-5": 20,
    "C-17": 21,
    "B-1B": 22,
    "B-2": 23,
    "B-21": 24,
    "B-52H": 25,
    "E-3": 26,
    "KC-10": 27,
    "KC-135": 28,
    "RQ-4": 29,
    "MQ-9": 30,
    "MQ-1": 31,
}


class Training_Pass(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Training cog is online!")

    @app_commands.command(name="training_pass", description="Log a training pass between a trainer and trainee.")
    @app_commands.describe(
        trainer="Select the trainer",
        trainee="Enter the trainee's name (as displayed in the sheet)",
        aircraft_type="Select the aircraft used in certification"
    )
    @app_commands.choices(
        aircraft_type=[
            app_commands.Choice(name="UH-60A", value="UH-60A"),
            app_commands.Choice(name="HH-60G", value="HH-60G"),
            app_commands.Choice(name="CH-47D", value="CH-47D"),
            app_commands.Choice(name="AH-64E", value="AH-64E"),
            app_commands.Choice(name="OH-58D", value="OH-58D"),
            app_commands.Choice(name="F-15E", value="F-15E"),
            app_commands.Choice(name="F-15C", value="F-15C"),
            app_commands.Choice(name="F-16C", value="F-16C"),
            app_commands.Choice(name="F-35A", value="F-35A"),
            app_commands.Choice(name="F-22A", value="F-22A"),
            app_commands.Choice(name="A-10C", value="A-10C"),
            app_commands.Choice(name="C-130", value="C-130"),
            app_commands.Choice(name="AC-130J", value="AC-130J"),
            app_commands.Choice(name="C-5", value="C-5"),
            app_commands.Choice(name="C-17", value="C-17"),
            app_commands.Choice(name="B-1B", value="B-1B"),
            app_commands.Choice(name="B-2", value="B-2"),
            app_commands.Choice(name="B-21", value="B-21"),
            app_commands.Choice(name="B-52H", value="B-52H"),
            app_commands.Choice(name="E-3", value="E-3"),
            app_commands.Choice(name="KC-10", value="KC-10"),
            app_commands.Choice(name="KC-135", value="KC-135"),
            app_commands.Choice(name="RQ-4", value="RQ-4"),
            app_commands.Choice(name="MQ-9", value="MQ-9"),
            app_commands.Choice(name="MQ-1", value="MQ-1"),
        ]
    )
    async def training_pass(
        self,
        interaction: discord.Interaction,
        trainer: discord.User,
        trainee: str,
        aircraft_type: app_commands.Choice[str],
    ):
        try:
  
            all_rows = sheet.get_all_values()

    
            headers = all_rows[3]
            print(f"Headers: {headers}")

            trainee_normalized = trainee.strip().lower()

        
            column = AIRCRAFT_COLUMN_MAP.get(aircraft_type.value)
            if column is None:
                await interaction.response.send_message(
                    content=f"Invalid aircraft type selected: {aircraft_type.name}",
                    ephemeral=True
                )
                return

   
            for i, row in enumerate(all_rows[4:], start=5): 
                row_name_normalized = row[3].strip().lower()  
                print(f"Checking row {i}: {row_name_normalized} against input: {trainee_normalized}")

                if row_name_normalized == trainee_normalized: 
                    sheet.update_cell(i, column, "TRUE")  
                    log_message = (
                        f"Training Logged:\n"
                        f"**Trainer:** {trainer.mention}\n"
                        f"**Trainee:** {trainee}\n"
                        f"**Aircraft Type:** {aircraft_type.name}\n"
                    )
                    await interaction.response.send_message(content=log_message, ephemeral=False)
                    return


            await interaction.response.send_message(
                content=f"Trainee **{trainee}** not found in the sheet. No updates were made.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                content=f"An error occurred while updating the spreadsheet: {str(e)}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Training_Pass(bot))
