import discord
import os
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

@tasks.loop(minutes=1)
async def heartbeat():
    print("Bot is still alive and running (Background Task)...")

@bot.event
async def on_ready():
    print("---------------------------------------")
    print("DEBUG: THIS IS THE >>> MANAGER <<< BOT")
    print(f"Logged in as: {bot.user.name}")
    print("---------------------------------------")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".help | Managing..."))
    if not heartbeat.is_running():
        heartbeat.start()

# --- MODERATION COMMANDS ---

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'✅ {member.name} has been kicked. Reason: {reason}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'✅ {member.name} has been banned. Reason: {reason}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount > 100:
        return await ctx.send("❌ I can only delete up to 100 messages at once.")
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ Deleted {len(deleted)-1} messages.', delete_after=5)

# --- UTILITY COMMANDS ---

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} Info", color=discord.Color.blue())
    embed.add_field(name="Owner", value=guild.owner, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info - {member.name}", color=member.color)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="Joined Discord", value=member.created_at.strftime("%b %d, %Y"), inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# --- LOGGING EVENTS ---

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    print(f"Message by {message.author} deleted in {message.channel}: {message.content}")

@bot.event
async def on_message_edit(before, after):
    if before.author.bot: return
    if before.content != after.content:
        print(f"Message by {before.author} edited: {before.content} -> {after.content}")

# --- ERROR HANDLING ---

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found.")

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found for Manager Bot.")
    else:
        bot.run(TOKEN)
