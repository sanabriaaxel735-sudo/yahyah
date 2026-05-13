import discord
import os
import asyncio
import re
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
TOKEN_WELCOMER = os.getenv('WELCOMER_TOKEN')
TOKEN_PROTECTION = os.getenv('PROTECTION_TOKEN')
TOKEN_MANAGER = os.getenv('MANAGER_TOKEN')
TOKEN_BOT4 = os.getenv('BOT4_TOKEN')
TOKEN_BOT5 = os.getenv('BOT5_TOKEN')
TOKEN_BOT6 = os.getenv('BOT6_TOKEN')

# Common configuration
INVITE_REGEX = r"(discord\.gg\/|discord\.com\/invite\/)[a-zA-Z0-9]+"

def create_welcomer():
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='w!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as Welcomer: {bot.user}")

    @bot.event
    async def on_member_join(member):
        channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, name="welcome") or member.guild.text_channels[0]
        if channel:
            embed = discord.Embed(title=f"Welcome to {member.guild.name}!", description=f"Hey {member.mention}, welcome!", color=discord.Color.blue())
            await channel.send(content=f"Welcome {member.mention}!", embed=embed)
    
    return bot

def create_protection():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix='p!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as Protection: {bot.user}")

    @bot.event
    async def on_message(message):
        if message.author.bot: return
        if re.search(INVITE_REGEX, message.content):
            try: await message.delete()
            except: pass
        await bot.process_commands(message)

    @bot.event
    async def on_member_join(member):
        if member.bot:
            # Kicking is temporarily disabled to allow new bots to join safely!
            print(f"Bot joined: {member.name}. Kicking is currently OFF.")
            return

    return bot

def create_manager():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix='.', intents=intents)

    @tasks.loop(minutes=1)
    async def heartbeat():
        print("Manager Bot is alive...")

    @bot.event
    async def on_ready():
        print(f"Logged in as Manager: {bot.user}")
        if not heartbeat.is_running(): heartbeat.start()

    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)

    return bot

def create_placeholder(name="Placeholder"):
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {name}: {bot.user}")
    
    return bot

def create_embed_generator():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='e!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as Embed Generator: {bot.user}")

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def say(ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def embed(ctx, *, content):
        await ctx.message.delete()
        parts = content.split('|')
        title = parts[0].strip() if len(parts) > 0 else "No Title"
        desc = parts[1].strip() if len(parts) > 1 else "No Description"
        color_val = discord.Color.blue()
        if len(parts) > 2:
            try:
                hex_color = int(parts[2].strip().replace('#', ''), 16)
                color_val = discord.Color(hex_color)
            except: pass
        embed = discord.Embed(title=title, description=desc, color=color_val)
        await ctx.send(embed=embed)

    return bot

async def main():
    bots = []
    if TOKEN_WELCOMER: bots.append(create_welcomer().start(TOKEN_WELCOMER))
    if TOKEN_PROTECTION: bots.append(create_protection().start(TOKEN_PROTECTION))
    if TOKEN_MANAGER: bots.append(create_manager().start(TOKEN_MANAGER))
    if TOKEN_BOT4: bots.append(create_placeholder("Bot #4").start(TOKEN_BOT4))
    if TOKEN_BOT5: bots.append(create_embed_generator().start(TOKEN_BOT5))
    if TOKEN_BOT6: bots.append(create_placeholder("Bot #6").start(TOKEN_BOT6))
    
    if not bots:
        print("ERROR: No tokens found in environment variables!")
        return

    print(f"Starting {len(bots)} bots in parallel...")
    await asyncio.gather(*bots)

if __name__ == "__main__":
    asyncio.run(main())
