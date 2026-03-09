import discord
from discord.ext import commands
from discord.ui import Button, View
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

mina_lines = []
sora_lines = []

class PanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

        mina_button = Button(label="Mina", style=discord.ButtonStyle.primary)
        sora_button = Button(label="Sora", style=discord.ButtonStyle.success)

        mina_button.callback = self.show_mina
        sora_button.callback = self.show_sora

        self.add_item(mina_button)
        self.add_item(sora_button)

    async def show_mina(self, interaction: discord.Interaction):
        if not mina_lines:
            await interaction.response.send_message("Mina panel empty.", ephemeral=True)
            return

        msg = "**Mina Panel:**\n"
        for i, line in enumerate(mina_lines, start=1):
            msg += f"{i}. {line}\n"

        await interaction.response.send_message(msg, ephemeral=True)

    async def show_sora(self, interaction: discord.Interaction):
        if not sora_lines:
            await interaction.response.send_message("Sora panel empty.", ephemeral=True)
            return

        msg = "**Sora Panel:**\n"
        for i, line in enumerate(sora_lines, start=1):
            msg += f"{i}. {line}\n"

        await interaction.response.send_message(msg, ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Show main panel
@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    await ctx.send("Choose a panel:", view=PanelView())

# Add to Mina
@bot.command()
@commands.has_permissions(administrator=True)
async def addm(ctx, *, text):
    new_lines = text.split("\n")

    count = 0
    for line in new_lines:
        line = line.strip()
        if line:
            mina_lines.append(line)
            count += 1

    await ctx.send(f"Added {count} lines to Mina.")

# Add to Sora
@bot.command()
@commands.has_permissions(administrator=True)
async def adds(ctx, *, text):
    new_lines = text.split("\n")

    count = 0
    for line in new_lines:
        line = line.strip()
        if line:
            sora_lines.append(line)
            count += 1

    await ctx.send(f"Added {count} lines to Sora.")

bot.run(os.getenv("TOKEN"))
