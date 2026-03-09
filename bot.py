import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import os
import json

# ---------------- CONFIG ----------------
ALLOWED_ROLE = 1430823219736088658
ALLOWED_CHANNELS = [
    1479831346456170618,
    1478383164958314516,
    1468947884807426152
]

DATA_FILE = "panels.json"
PANEL_INTERVAL = 30  # seconds
# ----------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

panel_channel = None
panel_message = None
panel_data = {
    "mina": [],
    "sora": [],
    "kay": [],
    "brnzel": []
}
# Track the last panel item message per channel
last_items_message = {}

# ----------------- UTIL ------------------
def save_panels():
    with open(DATA_FILE, "w") as f:
        json.dump(panel_data, f, indent=4)

def load_panels():
    global panel_data
    try:
        with open(DATA_FILE, "r") as f:
            panel_data = json.load(f)
    except:
        save_panels()

def is_bot_staff():
    async def predicate(ctx):
        role = discord.utils.get(ctx.author.roles, id=ALLOWED_ROLE)
        return bool(role or ctx.author.guild_permissions.administrator)
    return commands.check(predicate)

# --------------- PANEL VIEW --------------
class PanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Mina", style=discord.ButtonStyle.primary, custom_id="mina_btn"))
        self.add_item(Button(label="Sora", style=discord.ButtonStyle.success, custom_id="sora_btn"))
        self.add_item(Button(label="Kay", style=discord.ButtonStyle.secondary, custom_id="kay_btn"))
        self.add_item(Button(label="Brnzel", style=discord.ButtonStyle.danger, custom_id="brnzel_btn"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        role = discord.utils.get(interaction.user.roles, id=ALLOWED_ROLE)
        if role or interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("❌ You cannot use this panel.", ephemeral=True)
        return False

    async def show_panel(self, interaction, key, title):
        lines = panel_data.get(key, [])
        if not lines:
            msg = await interaction.response.send_message(f"{title} is empty.", ephemeral=False)
        else:
            msg_content = f"**{title}:**\n"
            for i, line in enumerate(lines, start=1):
                msg_content += f"{i}. {line}\n"
            # Send as a normal message, not ephemeral
            msg = await interaction.response.send_message(msg_content, ephemeral=False)
        # Fetch the actual sent message object
        sent_msg = await interaction.original_response()
        # Save in last_items_message for this channel
        last_items_message[interaction.channel.id] = sent_msg

    @discord.ui.button(label="Mina", style=discord.ButtonStyle.primary, custom_id="mina_btn")
    async def show_mina(self, button, interaction):
        await self.show_panel(interaction, "mina", "Mina Panel")

    @discord.ui.button(label="Sora", style=discord.ButtonStyle.success, custom_id="sora_btn")
    async def show_sora(self, button, interaction):
        await self.show_panel(interaction, "sora", "Sora Panel")

    @discord.ui.button(label="Kay", style=discord.ButtonStyle.secondary, custom_id="kay_btn")
    async def show_kay(self, button, interaction):
        await self.show_panel(interaction, "kay", "Kay Panel")

    @discord.ui.button(label="Brnzel", style=discord.ButtonStyle.danger, custom_id="brnzel_btn")
    async def show_brnzel(self, button, interaction):
        await self.show_panel(interaction, "brnzel", "Brnzel Panel")

# ------------- PANEL LOOP ----------------
@tasks.loop(seconds=PANEL_INTERVAL)
async def panel_loop():
    global panel_message
    if panel_channel is None:
        return
    try:
        if panel_message:
            try:
                await panel_message.edit(content="Choose a panel:", view=PanelView())
            except:
                panel_message = await panel_channel.send("Choose a panel:", view=PanelView())
        else:
            panel_message = await panel_channel.send("Choose a panel:", view=PanelView())
    except Exception as e:
        print(e)

# ----------------- EVENTS ----------------
@bot.event
async def on_ready():
    load_panels()
    print(f"Logged in as {bot.user}")

# ---------------- COMMANDS ----------------
@bot.command()
@is_bot_staff()
async def panelstart(ctx):
    global panel_channel
    if ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("❌ This channel cannot run panel iteration.")
        return
    panel_channel = ctx.channel
    if not panel_loop.is_running():
        panel_loop.start()
    await ctx.send("✅ Panel iteration started.")

@bot.command()
@is_bot_staff()
async def panelstop(ctx):
    global panel_channel, panel_message
    if panel_loop.is_running():
        panel_loop.stop()
    if panel_message:
        try:
            await panel_message.delete()
        except:
            pass
    panel_channel = None
    panel_message = None
    await ctx.send("🛑 Panel loop stopped.")

@bot.command()
async def cmnds(ctx):
    msg = """
**Bot Commands**

!panelstart → start panel loop
!panelstop → stop panel loop
!pdel → delete last panel items message (not the main panel)

Add items
!addm text
!adds text
!addk text
!addb text

Delete items
!delm number
!dels number
!delk number
!delb number
"""
    await ctx.send(msg)

# --------- ADD / DELETE COMMANDS ---------
@bot.command()
@is_bot_staff()
async def addm(ctx, *, text):
    for line in text.split("\n"):
        if line.strip():
            panel_data["mina"].append(line.strip())
    save_panels()
    await ctx.send("Added to Mina panel.")

@bot.command()
@is_bot_staff()
async def adds(ctx, *, text):
    for line in text.split("\n"):
        if line.strip():
            panel_data["sora"].append(line.strip())
    save_panels()
    await ctx.send("Added to Sora panel.")

@bot.command()
@is_bot_staff()
async def addk(ctx, *, text):
    for line in text.split("\n"):
        if line.strip():
            panel_data["kay"].append(line.strip())
    save_panels()
    await ctx.send("Added to Kay panel.")

@bot.command()
@is_bot_staff()
async def addb(ctx, *, text):
    for line in text.split("\n"):
        if line.strip():
            panel_data["brnzel"].append(line.strip())
    save_panels()
    await ctx.send("Added to Brnzel panel.")

@bot.command()
@is_bot_staff()
async def delm(ctx, number: int):
    if 1 <= number <= len(panel_data["mina"]):
        removed = panel_data["mina"].pop(number - 1)
        save_panels()
        await ctx.send(f"Removed from Mina: {removed}")
    else:
        await ctx.send("Invalid number.")

@bot.command()
@is_bot_staff()
async def dels(ctx, number: int):
    if 1 <= number <= len(panel_data["sora"]):
        removed = panel_data["sora"].pop(number - 1)
        save_panels()
        await ctx.send(f"Removed from Sora: {removed}")
    else:
        await ctx.send("Invalid number.")

@bot.command()
@is_bot_staff()
async def delk(ctx, number: int):
    if 1 <= number <= len(panel_data["kay"]):
        removed = panel_data["kay"].pop(number - 1)
        save_panels()
        await ctx.send(f"Removed from Kay: {removed}")
    else:
        await ctx.send("Invalid number.")

@bot.command()
@is_bot_staff()
async def delb(ctx, number: int):
    if 1 <= number <= len(panel_data["brnzel"]):
        removed = panel_data["brnzel"].pop(number - 1)
        save_panels()
        await ctx.send(f"Removed from Brnzel: {removed}")
    else:
        await ctx.send("Invalid number.")

# --------- DELETE LAST ITEMS MESSAGE ONLY ---------
@bot.command()
@is_bot_staff()
async def pdel(ctx):
    if ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("❌ Cannot delete panel items in this channel.")
        return
    last_msg = last_items_message.get(ctx.channel.id)
    if last_msg:
        try:
            await last_msg.delete()
            last_items_message[ctx.channel.id] = None
            await ctx.send("✅ Last panel items message deleted.")
        except:
            await ctx.send("❌ Failed to delete message.")
    else:
        await ctx.send("❌ No panel items message to delete in this channel.")

# ---------------- RUN BOT ----------------
bot.run(os.getenv("TOKEN"))

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
            "❌ You cannot use this panel.",
            ephemeral=True
        )

        return False


    async def show_mina(self, interaction: discord.Interaction):

        if not await self.has_access(interaction):
            return

        if not mina_lines:
            await interaction.response.send_message("Mina panel empty.")
            return

        msg = "**Mina Panel:**\n"

        for i, line in enumerate(mina_lines, start=1):
            msg += f"{i}. {line}\n"

        await interaction.response.send_message(msg)


    async def show_sora(self, interaction: discord.Interaction):

        if not await self.has_access(interaction):
            return

        if not sora_lines:
            await interaction.response.send_message("Sora panel empty.")
            return

        msg = "**Sora Panel:**\n"

        for i, line in enumerate(sora_lines, start=1):
            msg += f"{i}. {line}\n"

        await interaction.response.send_message(msg)


    async def show_kay(self, interaction: discord.Interaction):

        if not await self.has_access(interaction):
            return

        if not kay_lines:
            await interaction.response.send_message("Kay panel empty.")
            return

        msg = "**Kay Panel:**\n"

        for i, line in enumerate(kay_lines, start=1):
            msg += f"{i}. {line}\n"

        await interaction.response.send_message(msg)


    async def show_brnzel(self, interaction: discord.Interaction):

        if not await self.has_access(interaction):
            return

        if not brnzel_lines:
            await interaction.response.send_message("Brnzel panel empty.")
            return

        msg = "**Brnzel Panel:**\n"

        for i, line in enumerate(brnzel_lines, start=1):
            msg += f"{i}. {line}\n"

        await interaction.response.send_message(msg)


@tasks.loop(seconds=30)
async def panel_loop():

    global panel_message

    if panel_channel is None:
        return

    try:

        if panel_message:
            try:
                await panel_message.delete()
            except:
                pass

        panel_message = await panel_channel.send(
            "Choose a panel:",
            view=PanelView()
        )

    except Exception as e:
        print(e)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
@is_bot_staff()
async def panelstart(ctx):

    global panel_channel

    if ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("❌ This channel cannot run panel iteration.")
        return

    panel_channel = ctx.channel

    if not panel_loop.is_running():
        panel_loop.start()

    await ctx.send("✅ Panel iteration started.")


@bot.command()
@is_bot_staff()
async def panelstop(ctx):

    global panel_channel
    global panel_message

    if panel_loop.is_running():
        panel_loop.stop()

    if panel_message:
        try:
            await panel_message.delete()
        except:
            pass

    panel_channel = None
    panel_message = None

    await ctx.send("🛑 Panel loop stopped.")


@bot.command()
async def cmnds(ctx):

    msg = """
**Bot Commands**

!panelstart → start panel loop
!panelstop → stop panel loop

Add items
!addm text
!adds text
!addk text
!addb text

Delete items
!delm number
!dels number
!delk number
!delb number
"""

    await ctx.send(msg)


@bot.command()
@is_bot_staff()
async def addm(ctx, *, text):

    for line in text.split("\n"):
        if line.strip():
            mina_lines.append(line.strip())

    await ctx.send("Added to Mina panel.")


@bot.command()
@is_bot_staff()
async def adds(ctx, *, text):

    for line in text.split("\n"):
        if line.strip():
            sora_lines.append(line.strip())

    await ctx.send("Added to Sora panel.")


@bot.command()
@is_bot_staff()
async def addk(ctx, *, text):

    for line in text.split("\n"):
        if line.strip():
            kay_lines.append(line.strip())

    await ctx.send("Added to Kay panel.")


@bot.command()
@is_bot_staff()
async def addb(ctx, *, text):

    for line in text.split("\n"):
        if line.strip():
            brnzel_lines.append(line.strip())

    await ctx.send("Added to Brnzel panel.")


@bot.command()
@is_bot_staff()
async def delm(ctx, number: int):

    if 1 <= number <= len(mina_lines):
        removed = mina_lines.pop(number - 1)
        await ctx.send(f"Removed from Mina: {removed}")
    else:
        await ctx.send("Invalid number.")


@bot.command()
@is_bot_staff()
async def dels(ctx, number: int):

    if 1 <= number <= len(sora_lines):
        removed = sora_lines.pop(number - 1)
        await ctx.send(f"Removed from Sora: {removed}")
    else:
        await ctx.send("Invalid number.")


@bot.command()
@is_bot_staff()
async def delk(ctx, number: int):

    if 1 <= number <= len(kay_lines):
        removed = kay_lines.pop(number - 1)
        await ctx.send(f"Removed from Kay: {removed}")
    else:
        await ctx.send("Invalid number.")


@bot.command()
@is_bot_staff()
async def delb(ctx, number: int):

    if 1 <= number <= len(brnzel_lines):
        removed = brnzel_lines.pop(number - 1)
        await ctx.send(f"Removed from Brnzel: {removed}")
    else:
        await ctx.send("Invalid number.")


bot.run(os.getenv("TOKEN"))
        await ctx.send("Invalid number.")


bot.run(os.getenv("TOKEN"))
