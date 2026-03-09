import discord
from discord.ext import commands
import os

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

lines = []

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Add line
@bot.command()
@commands.has_permissions(administrator=True)
async def add(ctx, *, text):
    lines.append(text)
    await ctx.send(f"Added line #{len(lines)}")

# Show all lines directly
@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    if not lines:
        await ctx.send("No lines stored.")
        return

    msg = "**Stored Lines:**\n"
    for i, line in enumerate(lines, start=1):
        msg += f"{i}. {line}\n"

    await ctx.send(msg)

# Delete line
@bot.command()
@commands.has_permissions(administrator=True)
async def delete(ctx, number: int):
    if number <= 0 or number > len(lines):
        await ctx.send("Invalid serial number.")
        return

    removed = lines.pop(number - 1)
    await ctx.send(f"Deleted: {removed}")

bot.run(os.getenv("TOKEN"))

    removed = lines.pop(number - 1)
    await ctx.send(f"Deleted: {removed}")

bot.run(os.getenv("TOKEN"))
