# 🌸 Roseline Music Bot

Roseline ek Discord Music Bot hai jo playlists, premium system aur music controls support karta hai.  
Python + Discord.py + yt-dlp use karke banaya gaya hai.

---

# 📱 Full Termux + Ubuntu Installation Guide

## ✅ Step 1 — Install Termux

Download latest Termux from:

- F-Droid
- GitHub Releases

---

# ✅ Step 2 — Update Packages

Open Termux and run:

```bash
pkg update && pkg upgrade -y


---

✅ Step 3 — Install Required Packages

pkg install git wget curl proot-distro -y


---

✅ Step 4 — Install Ubuntu

proot-distro install ubuntu

Start Ubuntu:

proot-distro login ubuntu


---

✅ Step 5 — Update Ubuntu

Inside Ubuntu run:

apt update && apt upgrade -y


---

✅ Step 6 — Install Python + FFmpeg

apt install python3 python3-pip git ffmpeg -y

Check versions:

python3 --version
ffmpeg -version


---

✅ Step 7 — Clone GitHub Repository

git clone https://github.com/hero334330000-wq/Roslines.git

Enter folder:

cd Roslines


---

✅ Step 8 — Create Virtual Environment

python3 -m venv venv

Activate venv:

source venv/bin/activate


---

✅ Step 9 — Install Python Libraries

pip install -U pip

Install bot packages:

pip install -U discord.py yt-dlp pynacl ffmpeg-python


---

✅ Step 10 — Add Discord Bot Token

Create bot.txt file:

nano bot.txt

Paste token:

YOUR_DISCORD_BOT_TOKEN

Save:

CTRL + X

Y

ENTER



---

✅ Step 11 — Run Bot

python3 resebot.py

If successful:

Roseline Bot is ready!


---

🎵 Slash Commands

Command	Description

/play song	Single song play
/pl_play name	Playlist play
/pl_create name	Create playlist
/pl_list	Show playlists
/help	Help menu



---

🌸 Music Controls

Roseline supports:

⏭️ Skip

⏹️ Stop

🔁 Playlist Loop



---

⭐ Premium System

Owner command:

/p_send userid

Premium lasts 30 days automatically.


---

🗄️ Database

Bot automatically creates:

roseline_music.db

Tables:

premium

playlists

playlist_songs



---

🔧 Common Fixes

❌ python command not found

Use:

python3 resebot.py


---

❌ FFmpeg Error

Install again:

apt install ffmpeg -y


---

❌ Voice Not Working

Install PyNaCl:

pip install pynacl


---

❌ Slash Commands Not Showing

Invite bot with:

applications.commands

bot


permissions.

Wait 1-5 minutes after starting bot.


---

🔗 GitHub Repository

https://github.com/hero334330000-wq/Roslines


---

❤️ Made With

Python

Discord.py

yt-dlp

SQLite

FFmpeg



---

👑 Developer by Hero3288
