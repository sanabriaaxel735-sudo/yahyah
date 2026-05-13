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

    whitelisted_users = []

    @bot.event
    async def on_ready():
        print(f"Logged in as Protection: {bot.user}")

    @bot.event
    async def on_message(message):
        if message.author.bot: return
        if re.search(INVITE_REGEX, message.content) and message.author.id not in whitelisted_users:
            try: await message.delete()
            except: pass
        await bot.process_commands(message)

    @bot.event
    async def on_member_join(member):
        if member.bot:
            try: await member.kick(reason="Anti-Bot")
            except: pass

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

    @bot.command()
    async def ping(ctx):
        await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

    return bot

async def main():
    bots = []
    if TOKEN_WELCOMER: bots.append(create_welcomer().start(TOKEN_WELCOMER))
    if TOKEN_PROTECTION: bots.append(create_protection().start(TOKEN_PROTECTION))
    if TOKEN_MANAGER: bots.append(create_manager().start(TOKEN_MANAGER))
    
    if not bots:
        print("ERROR: No tokens found in environment variables!")
        return

    print(f"Starting {len(bots)} bots in parallel...")
    await asyncio.gather(*bots)

if __name__ == "__main__":
    asyncio.run(main())
