import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import yt_dlp
import os
import asyncio
from datetime import datetime, timedelta

# --- TOKEN LOADING ---
if os.path.exists("bot.txt"):
    with open("bot.txt", "r") as f:
        TOKEN = f.read().strip()
else:
    print("Error: bot.txt file nahi mili!")
    exit()

ADMIN_ID = 1297870217124515890

# --- DATABASE SETUP ---
db = sqlite3.connect('roseline_music.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS premium (user_id TEXT PRIMARY KEY, expiry_date TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS playlists (user_id TEXT, pl_name TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS playlist_songs (user_id TEXT, pl_name TEXT, song_info TEXT)')
db.commit()

# --- MUSIC SETTINGS ---
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class RoselineBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.loop_status = {} # guild_id: bool
        self.current_playlist = {} # guild_id: [songs]
        self.original_playlist = {} # guild_id: [songs] backup for loop

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Roseline Bot is ready!")

bot = RoselineBot()

# --- PREMIUM CHECK ---
async def check_premium(interaction: discord.Interaction):
    if interaction.user.id == ADMIN_ID:
        return True
    cursor.execute('SELECT expiry_date FROM premium WHERE user_id = ?', (str(interaction.user.id),))
    result = cursor.fetchone()
    if result:
        expiry = datetime.strptime(result[0], '%Y-%m-%d')
        if datetime.now() < expiry:
            return True
        else:
            cursor.execute('DELETE FROM premium WHERE user_id = ?', (str(interaction.user.id),))
            db.commit()
    await interaction.response.send_message("❌ Aapke paas **Roseline Premium Pass** nahi hai!", ephemeral=True)
    return False

# --- CONTROL BUTTONS VIEW ---
class ControlView(discord.ui.View):
    def __init__(self, vc, guild_id):
        super().__init__(timeout=None)
        self.vc = vc
        self.guild_id = guild_id

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def skip(self, interaction, button):
        if self.vc.is_playing():
            self.vc.stop()
            await interaction.response.send_message("⏭️ Song Skipped!", ephemeral=True)
        else:
            await interaction.response.send_message("Abhi kuch nahi baj raha.", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️")
    async def stop(self, interaction, button):
        bot.current_playlist[self.guild_id] = []
        bot.original_playlist[self.guild_id] = []
        await self.vc.disconnect()
        await interaction.response.send_message("⏹️ Roseline Disconnected.", ephemeral=True)

    @discord.ui.button(label="Loop Playlist", style=discord.ButtonStyle.primary, emoji="🔁")
    async def loop(self, interaction, button):
        current = bot.loop_status.get(self.guild_id, False)
        bot.loop_status[self.guild_id] = not current
        status = "Enabled" if bot.loop_status[self.guild_id] else "Disabled"
        await interaction.response.send_message(f"🔁 Playlist Loop {status}!", ephemeral=True)

# --- ENGINE ---
async def play_music_engine(interaction, song_name):
    guild_id = interaction.guild.id
    vc = interaction.guild.voice_client

    if not vc: return

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=False)['entries'][0]
            url, title, thumbnail = info['url'], info['title'], info['thumbnail']
        except:
            return await interaction.followup.send(f"❌ `{song_name}` nahi mila.")

    def after_playing(error):
        coro = check_next_and_play(interaction)
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except:
            pass

    if vc.is_playing(): vc.stop()
    vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=after_playing)

    embed = discord.Embed(title="Roseline Player 🌸", description=f"🎶 **Now Playing:**\n{title}", color=0xFF69B4)
    embed.set_image(url=thumbnail)
    embed.set_footer(text=f"Requested by {interaction.user.name} | Loop: {'ON' if bot.loop_status.get(guild_id) else 'OFF'}")
    
    await interaction.followup.send(embed=embed, view=ControlView(vc, guild_id))

async def check_next_and_play(interaction):
    guild_id = interaction.guild.id
    vc = interaction.guild.voice_client
    
    if not vc: return

    if bot.current_playlist.get(guild_id):
        next_song = bot.current_playlist[guild_id].pop(0)
        await play_music_engine(interaction, next_song)
    else:
        # Agar loop ON hai, toh original playlist reset karo
        if bot.loop_status.get(guild_id) and bot.original_playlist.get(guild_id):
            bot.current_playlist[guild_id] = list(bot.original_playlist[guild_id])
            next_song = bot.current_playlist[guild_id].pop(0)
            await play_music_engine(interaction, next_song)

# --- COMMANDS ---

@bot.tree.command(name="play", description="Single gana bajayein")
async def play(interaction: discord.Interaction, song: str):
    if not await check_premium(interaction): return
    if not interaction.user.voice: return await interaction.response.send_message("Pehle VC join karein!")
    
    await interaction.response.defer()
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    
    bot.current_playlist[interaction.guild.id] = [] # Clear playlist if playing single song
    bot.original_playlist[interaction.guild.id] = []
    await play_music_engine(interaction, song)

@bot.tree.command(name="pl_play", description="Poori playlist UI ke sath bajayein")
async def pl_play(interaction: discord.Interaction, name: str):
    if not await check_premium(interaction): return
    if not interaction.user.voice: return await interaction.response.send_message("Pehle VC join karein!")
    
    cursor.execute('SELECT song_info FROM playlist_songs WHERE user_id = ? AND pl_name = ?', (str(interaction.user.id), name))
    songs = [r[0] for r in cursor.fetchall()]
    
    if not songs: return await interaction.response.send_message(f"❌ `{name}` playlist khali hai!")

    await interaction.response.defer()
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()

    bot.original_playlist[interaction.guild.id] = list(songs) # Backup for loop
    bot.current_playlist[interaction.guild.id] = list(songs)
    
    first_song = bot.current_playlist[interaction.guild.id].pop(0)
    await play_music_engine(interaction, first_song)

@bot.tree.command(name="p_send", description="Premium Pass (Admin Only)")
async def p_send(interaction: discord.Interaction, userid: str):
    if interaction.user.id != ADMIN_ID: return await interaction.response.send_message("Owner only!")
    expiry = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    cursor.execute('INSERT OR REPLACE INTO premium (user_id, expiry_date) VALUES (?, ?)', (userid, expiry))
    db.commit()
    await interaction.response.send_message(f"⭐ **Roseline Premium** activated for <@{userid}> (30 Days).")

@bot.tree.command(name="pl_create", description="Playlist banayein")
async def pl_create(interaction: discord.Interaction, name: str):
    if not await check_premium(interaction): return
    cursor.execute('INSERT INTO playlists (user_id, pl_name) VALUES (?, ?)', (str(interaction.user.id), name))
    db.commit()
    await interaction.response.send_message(f"✅ Playlist `{name}` create ho gayi!")

@bot.tree.command(name="pl_list", description="Sari playlists")
async def pl_list(interaction: discord.Interaction):
    if not await check_premium(interaction): return
    cursor.execute('SELECT pl_name FROM playlists WHERE user_id = ?', (str(interaction.user.id),))
    rows = cursor.fetchall()
    res = "\n".join([f"📂 {r[0]}" for r in rows]) if rows else "Koi playlist nahi mili."
    await interaction.response.send_message(embed=discord.Embed(title="Your Playlists", description=res, color=0xFF69B4))

@bot.tree.command(name="help", description="Help Menu")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🌸 Roseline Help", color=0xFF69B4)
    embed.add_field(name="Music", value="`/play`, `/pl_play (name)`, `/stop`", inline=False)
    embed.add_field(name="Playlist", value="`/pl_create`, `/pl_add`, `/pl_list`", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
