import discord
from discord.ext import commands
from discord.ui import Button, View
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

lines = []

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

@bot.command()
async def add(ctx, *, text):
    lines.append(text)
    await ctx.send(f"Added line #{len(lines)}")

@bot.command()
async def panel(ctx):
    await ctx.send("Press button to show lines.", view=ShowLinesView())

@bot.command()
async def delete(ctx, number: int):
    if number <= 0 or number > len(lines):
        await ctx.send("Invalid serial number.")
        return

    removed = lines.pop(number - 1)
    await ctx.send(f"Deleted: {removed}")

bot.run(os.getenv("MTQwNzAwNTYzNjI4MTExMDY5MA.GHhQXs.Oy5MVsV3JZWrgIMy_A5R3pccIuhN-AsENx-53o"))
