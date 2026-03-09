import discord
from discord.ext import commands
from discord.ui import Button, View
import os

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Storage for lines
lines = []

# Button view
class ShowLinesView(View):
    def __init__(self):
        super().__init__(timeout=None)

        show_button = Button(label="Show Lines", style=discord.ButtonStyle.green)
        show_button.callback = self.show_lines
        self.add_item(show_button)

    async def show_lines(self, interaction: discord.Interaction):
        if not lines:
            await interaction.response.send_message("No lines stored.", ephemeral=True)
            return

        msg = "**Stored Lines:**\n"
        for i, line in enumerate(lines, start=1):
            msg += f"{i}. {line}\n"

        await interaction.response.send_message(msg, ephemeral=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# Add line command
@bot.command()
async def add(ctx, *, text):
    lines.append(text)
    await ctx.send(f"Added line #{len(lines)}")


# Show button panel
@bot.command()
async def panel(ctx):
    await ctx.send("Press the button to show stored lines.", view=ShowLinesView())


# Delete by serial number
@bot.command()
async def delete(ctx, number: int):
    if number <= 0 or number > len(lines):
        await ctx.send("Invalid serial number.")
        return

    removed = lines.pop(number - 1)
    await ctx.send(f"Deleted: {removed}")


# Run bot using Railway variable
bot.run(os.getenv("TOKEN"))return

    removed = lines.pop(number - 1)
    await ctx.send(f"Deleted: {removed}")

bot.run(os.getenv("TOKEN"))
