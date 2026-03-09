import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Bot is online!")

bot.run(os.getenv("TOKEN"))
