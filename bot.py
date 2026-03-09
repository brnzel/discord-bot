import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import os
import sqlite3
from flask import Flask
from threading import Thread

ALLOWED_ROLE = 1430823219736088658
ALLOWED_CHANNELS = [1479831346456170618, 1478383164958314516, 1468947884807426152]
PANEL_INTERVAL = 30
DATABASE = "panels.db"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

panel_channel = None
panel_message = None
last_items_message = {}

# -------------- DATABASE ----------------
def init_db():
    with sqlite3.connect(DATABASE, check_same_thread=False) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS panels (key TEXT PRIMARY KEY, content TEXT)""")
        for key in ["mina","sora","kay","brnzel"]:
            c.execute("INSERT OR IGNORE INTO panels (key, content) VALUES (?,?)",(key,""))
        conn.commit()

def get_panel(key):
    with sqlite3.connect(DATABASE, check_same_thread=False) as conn:
        c = conn.cursor()
        c.execute("SELECT content FROM panels WHERE key=?", (key,))
        result = c.fetchone()
    return result[0].split("\n") if result and result[0] else []

def add_panel_line(key, line):
    lines = get_panel(key)
    lines.append(line)
    with sqlite3.connect(DATABASE, check_same_thread=False) as conn:
        c = conn.cursor()
        c.execute("UPDATE panels SET content=? WHERE key=?",
                  ("\n".join(lines), key))
        conn.commit()

def del_panel_line(key, index):
    lines = get_panel(key)
    if 0 <= index < len(lines):
        removed = lines.pop(index)
        with sqlite3.connect(DATABASE, check_same_thread=False) as conn:
            c = conn.cursor()
            c.execute("UPDATE panels SET content=? WHERE key=?",
                      ("\n".join(lines), key))
            conn.commit()
        return removed
    return None

# ---------------- UTIL ------------------
def is_bot_staff():
    async def predicate(ctx):
        role = discord.utils.get(ctx.author.roles, id=ALLOWED_ROLE)
        return bool(role or ctx.author.guild_permissions.administrator)
    return commands.check(predicate)

# ---------------- PANEL VIEW ------------------
class PanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Mina", style=discord.ButtonStyle.primary, custom_id="mina_btn"))
        self.add_item(Button(label="Sora", style=discord.ButtonStyle.success, custom_id="sora_btn"))
        self.add_item(Button(label="Kay", style=discord.ButtonStyle.secondary, custom_id="kay_btn"))
        self.add_item(Button(label="Brnzel", style=discord.ButtonStyle.danger, custom_id="brnzel_btn"))

    async def interaction_check(self, interaction):
        role = discord.utils.get(interaction.user.roles, id=ALLOWED_ROLE)
        if role or interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("❌ You cannot use this panel.", ephemeral=True)
        return False

    async def show_panel(self, interaction, key, title):
        lines = get_panel(key)
        if not lines:
            msg = await interaction.response.send_message(f"{title} is empty.", ephemeral=False)
        else:
            content = f"**{title}:**\n" + "\n".join(f"{i+1}. {l}" for i,l in enumerate(lines))
            msg = await interaction.response.send_message(content, ephemeral=False)
        last_items_message[interaction.channel.id] = await interaction.original_response()

    @discord.ui.button(label="Mina", style=discord.ButtonStyle.primary)
    async def show_mina(self, button, interaction):
        await self.show_panel(interaction, "mina", "Mina Panel")
    @discord.ui.button(label="Sora", style=discord.ButtonStyle.success)
    async def show_sora(self, button, interaction):
        await self.show_panel(interaction, "sora", "Sora Panel")
    @discord.ui.button(label="Kay", style=discord.ButtonStyle.secondary)
    async def show_kay(self, button, interaction):
        await self.show_panel(interaction, "kay", "Kay Panel")
    @discord.ui.button(label="Brnzel", style=discord.ButtonStyle.danger)
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
            await panel_message.edit(content="Choose a panel:", view=PanelView())
        else:
            panel_message = await panel_channel.send("Choose a panel:", view=PanelView())
    except Exception as e:
        print("Panel loop error:", e)

# --------------- KEEP ALIVE ----------------
app = Flask("")
@app.route("/")
def home(): return "Bot is alive"
def run(): app.run(host="0.0.0.0", port=8080)
def keep_alive(): Thread(target=run).start()

# --------------- EVENTS ----------------
@bot.event
async def on_ready():
    init_db()
    print(f"Logged in as {bot.user}")

# --------------- COMMANDS ----------------
@bot.command()
@is_bot_staff()
async def panelstart(ctx):
    global panel_channel
    if ctx.channel.id not in ALLOWED_CHANNELS:
        return await ctx.send("❌ This channel cannot run panel iteration.")
    panel_channel = ctx.channel
    if not panel_loop.is_running(): panel_loop.start()
    await ctx.send("✅ Panel iteration started.")

@bot.command()
@is_bot_staff()
async def panelstop(ctx):
    global panel_channel, panel_message
    if panel_loop.is_running(): panel_loop.stop()
    if panel_message:
        try: await panel_message.delete()
        except: pass
    panel_channel = None
    panel_message = None
    await ctx.send("🛑 Panel loop stopped.")

@bot.command()
@is_bot_staff()
async def addm(ctx, *, text):
    for l in text.split("\n"): 
        if l.strip(): add_panel_line("mina", l.strip())
    await ctx.send("Added to Mina panel.")
@bot.command()
@is_bot_staff()
async def adds(ctx, *, text):
    for l in text.split("\n"): 
        if l.strip(): add_panel_line("sora", l.strip())
    await ctx.send("Added to Sora panel.")
@bot.command()
@is_bot_staff()
async def addk(ctx, *, text):
    for l in text.split("\n"): 
        if l.strip(): add_panel_line("kay", l.strip())
    await ctx.send("Added to Kay panel.")
@bot.command()
@is_bot_staff()
async def addb(ctx, *, text):
    for l in text.split("\n"): 
        if l.strip(): add_panel_line("brnzel", l.strip())
    await ctx.send("Added to Brnzel panel.")

@bot.command()
@is_bot_staff()
async def delm(ctx, number:int):
    r = del_panel_line("mina", number-1)
    await ctx.send(f"Removed from Mina: {r}" if r else "Invalid number.")
@bot.command()
@is_bot_staff()
async def dels(ctx, number:int):
    r = del_panel_line("sora", number-1)
    await ctx.send(f"Removed from Sora: {r}" if r else "Invalid number.")
@bot.command()
@is_bot_staff()
async def delk(ctx, number:int):
    r = del_panel_line("kay", number-1)
    await ctx.send(f"Removed from Kay: {r}" if r else "Invalid number.")
@bot.command()
@is_bot_staff()
async def delb(ctx, number:int):
    r = del_panel_line("brnzel", number-1)
    await ctx.send(f"Removed from Brnzel: {r}" if r else "Invalid number.")

@bot.command()
@is_bot_staff()
async def pdel(ctx):
    if ctx.channel.id not in ALLOWED_CHANNELS: return await ctx.send("❌ Cannot delete panel items here.")
    msg = last_items_message.get(ctx.channel.id)
    if msg:
        try: await msg.delete(); last_items_message[ctx.channel.id]=None; await ctx.send("✅ Deleted last items message.")
        except: await ctx.send("❌ Failed to delete.")
    else: await ctx.send("❌ No items message to delete.")

keep_alive()
bot.run(os.getenv("TOKEN"))

# ---------------- RUN BOT ----------------
keep_alive()
bot.run(os.getenv("TOKEN"))
