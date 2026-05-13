import discord
import os
import re
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# Configuration / State
log_channel_id = None
whitelisted_users = [] # IDs of users who can perform "nuke" actions
last_join_times = [] # To detect mass joins
nuke_counts = {} # user_id: {type: count, last_time: timestamp}

# Regex for Discord Invites
INVITE_REGEX = r"(discord\.gg\/|discord\.com\/invite\/)[a-zA-Z0-9]+"

@bot.event
async def on_ready():
    print(f'Protection Bot online: {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for raids..."))

# --- ANTI-LINK ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check for invites
    if re.search(INVITE_REGEX, message.content):
        if message.author.id not in whitelisted_users:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, invite links are not allowed!", delete_after=5)
            except:
                pass

    await bot.process_commands(message)

# --- ANTI-NUKE (Channel/Role Deletion) ---
@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        user = entry.user
        if user.id == bot.user.id or user.id in whitelisted_users:
            return
        
        # Simple alert logic
        print(f"Channel {channel.name} deleted by {user}")
        # In a real bot, we'd check if they deleted multiple in X seconds

@bot.event
async def on_member_join(member):
    # --- ANTI-RAID (Mass Join) ---
    now = datetime.utcnow()
    last_join_times.append(now)
    
    # Keep only joins from last 10 seconds
    ten_seconds_ago = now - timedelta(seconds=10)
    joins_in_last_10 = [t for t in last_join_times if t > ten_seconds_ago]
    
    if len(joins_in_last_10) > 5: # 5+ joins in 10 seconds
        print(f"RAID DETECTED: {len(joins_in_last_10)} joins in 10s")
        # Alert staff
    
    # --- ANTI-BOT ---
    if member.bot:
        try:
            await member.kick(reason="Anti-Bot Protection: Unverified bot joined.")
        except:
            pass

@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist(ctx, user: discord.User):
    if user.id not in whitelisted_users:
        whitelisted_users.append(user.id)
        await ctx.send(f"✅ Added {user.name} to the whitelist.")
    else:
        await ctx.send("User is already whitelisted.")

@bot.command()
async def protect_status(ctx):
    await ctx.send("🛡️ Protection system is active.\n- Anti-Link: ON\n- Anti-Bot: ON\n- Anti-Nuke Monitoring: ON")

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found for Protection Bot.")
    else:
        bot.run(TOKEN)
