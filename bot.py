import discord
from discord.ext import commands
from discord.ui import Button, View
import os

ALLOWED_ROLE = 1430823219736088658

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

mina_lines = []
sora_lines = []
kay_lines = []
brnzel_lines = []


def is_bot_staff():
    async def predicate(ctx):
        role = discord.utils.get(ctx.author.roles, id=ALLOWED_ROLE)
        if role or ctx.author.guild_permissions.administrator:
            return True
        return False
    return commands.check(predicate)


class PanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

        mina_button = Button(label="Mina", style=discord.ButtonStyle.primary)
        sora_button = Button(label="Sora", style=discord.ButtonStyle.success)
        kay_button = Button(label="Kay", style=discord.ButtonStyle.secondary)
        brnzel_button = Button(label="Brnzel", style=discord.ButtonStyle.danger)

        mina_button.callback = self.show_mina
        sora_button.callback = self.show_sora
        kay_button.callback = self.show_kay
        brnzel_button.callback = self.show_brnzel

        self.add_item(mina_button)
        self.add_item(sora_button)
        self.add_item(kay_button)
        self.add_item(brnzel_button)

    async def has_access(self, interaction):
        role = discord.utils.get(interaction.user.roles, id=ALLOWED_ROLE)
        if role or interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message(
            "❌ You don't have permission to use this panel.",
            ephemeral=True
        )
        return False

    async def show_mina(self, interaction: discord.Interaction):
        if not await self.has_access(interaction):
            return
        if not mina_lines:
            await interaction.response.send_message("Mina panel empty.")
            return
        msg = "**Mina Panel:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(mina_lines))
        await interaction.response.send_message(msg)

    async def show_sora(self, interaction: discord.Interaction):
        if not await self.has_access(interaction):
            return
        if not sora_lines:
            await interaction.response.send_message("Sora panel empty.")
            return
        msg = "**Sora Panel:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(sora_lines))
        await interaction.response.send_message(msg)

    async def show_kay(self, interaction: discord.Interaction):
        if not await self.has_access(interaction):
            return
        if not kay_lines:
            await interaction.response.send_message("Kay panel empty.")
            return
        msg = "**Kay Panel:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(kay_lines))
        await interaction.response.send_message(msg)

    async def show_brnzel(self, interaction: discord.Interaction):
        if not await self.has_access(interaction):
            return
        if not brnzel_lines:
            await interaction.response.send_message("Brnzel panel empty.")
            return
        msg = "**Brnzel Panel:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(brnzel_lines))
        await interaction.response.send_message(msg)


# -------------------
# Helper: Send full panel
# -------------------
async def send_panel(ctx):
    view = PanelView()
    msg = "**Updated Panel:**\n"
    if mina_lines:
        msg += "\n**Mina:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(mina_lines))
    if sora_lines:
        msg += "\n**Sora:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(sora_lines))
    if kay_lines:
        msg += "\n**Kay:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(kay_lines))
    if brnzel_lines:
        msg += "\n**Brnzel:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(brnzel_lines))
    await ctx.send(msg, view=view)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def panel(ctx):
    await ctx.send("Choose a panel:", view=PanelView())


# -------------------
# Add commands
# -------------------
@bot.command()
@is_bot_staff()
async def addm(ctx, *, text):
    for line in text.split("\n"):
        if line.strip():
            mina_lines.append(line.strip())
    await send_panel(ctx)


@bot.command()
@is_bot_staff()
async def adds(ctx, *, text):
    for line in text.split("\n"):
        if line.strip():
            sora_lines.append(line.strip())
    await send_panel(ctx)


@bot.command()
@is_bot_staff()
async def addk(ctx, *, text):
    for line in text.split("\n"):
        if line.strip():
            kay_lines.append(line.strip())
    await send_panel(ctx)


@bot.command()
@is_bot_staff()
async def addb(ctx, *, text):
    for line in text.split("\n"):
        if line.strip():
            brnzel_lines.append(line.strip())
    await send_panel(ctx)


# -------------------
# Delete commands
# -------------------
@bot.command()
@is_bot_staff()
async def delm(ctx, number: int):
    if 1 <= number <= len(mina_lines):
        removed = mina_lines.pop(number - 1)
        await ctx.send(f"Removed from Mina: {removed}")
    else:
        await ctx.send("Invalid number.")
    await send_panel(ctx)


@bot.command()
@is_bot_staff()
async def dels(ctx, number: int):
    if 1 <= number <= len(sora_lines):
        removed = sora_lines.pop(number - 1)
        await ctx.send(f"Removed from Sora: {removed}")
    else:
        await ctx.send("Invalid number.")
    await send_panel(ctx)


@bot.command()
@is_bot_staff()
async def delk(ctx, number: int):
    if 1 <= number <= len(kay_lines):
        removed = kay_lines.pop(number - 1)
        await ctx.send(f"Removed from Kay: {removed}")
    else:
        await ctx.send("Invalid number.")
    await send_panel(ctx)


@bot.command()
@is_bot_staff()
async def delb(ctx, number: int):
    if 1 <= number <= len(brnzel_lines):
        removed = brnzel_lines.pop(number - 1)
        await ctx.send(f"Removed from Brnzel: {removed}")
    else:
        await ctx.send("Invalid number.")
    await send_panel(ctx)


bot.run(os.getenv("TOKEN"))
