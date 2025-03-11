import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
import os
import asyncio


bot = commands.Bot(command_prefix = ".", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot Online")
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("An error with syncing application commands has occured: ", e)


with open("token.txt") as file:
    token = file.read()

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(token)            

asyncio.run(main())