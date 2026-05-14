import discord
import os
import asyncio
import re
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
import booster_logic
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Load environment variables
load_dotenv()
TOKEN_WELCOMER = os.getenv('WELCOMER_TOKEN')
TOKEN_PROTECTION = os.getenv('PROTECTION_TOKEN')
TOKEN_MANAGER = os.getenv('MANAGER_TOKEN')
TOKEN_BOT4 = os.getenv('BOT4_TOKEN')
TOKEN_BOT5 = os.getenv('BOT5_TOKEN')
TOKEN_BOT6 = os.getenv('BOT6_TOKEN')
TOKEN_BOT7 = os.getenv('BOT7_TOKEN')
TOKEN_BOT8 = os.getenv('BOT8_TOKEN')
TOKEN_BOT9 = os.getenv('BOT9_TOKEN')
TOKEN_BOOSTER = os.getenv('BOOSTER_TOKEN')

# Common configuration
INVITE_REGEX = r"(discord\.gg\/|discord\.com\/invite\/)[a-zA-Z0-9]+"

# --- FASTAPI SETUP ---
app = FastAPI()
if os.path.exists("dashboard"):
    app.mount("/static", StaticFiles(directory="dashboard"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("dashboard/index.html")

# --- BOT CREATORS ---

def create_welcomer():
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='w!', intents=intents)
    @bot.event
    async def on_ready(): print(f"Logged in as Welcomer: {bot.user}")
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
    async def on_ready(): print(f"Logged in as Protection: {bot.user}")
    @bot.event
    async def on_message(message):
        if message.author.bot: return
        if re.search(INVITE_REGEX, message.content):
            try: await message.delete()
            except: pass
        await bot.process_commands(message)
    return bot

def create_manager():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix='.', intents=intents)
    @tasks.loop(minutes=1)
    async def heartbeat(): pass
    @bot.event
    async def on_ready():
        print(f"Logged in as Manager: {bot.user}")
        if not heartbeat.is_running(): heartbeat.start()
    return bot

import booster_standalone.intelligence as intelligence

def create_booster_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='b!', intents=intents)
    
    @bot.event
    async def on_ready(): 
        print(f"Logged in as Booster Bot (Nova GPT): {bot.user}")
        # Start key refresh loop
        if not auto_refresh_keys.is_running():
            auto_refresh_keys.start()

    @tasks.loop(hours=6)
    async def auto_refresh_keys():
        print("Elite System: Refreshing free AI keys...")
        import booster_standalone.fetch_free_keys as fetch_free_keys
        fetch_free_keys.fetch_keys()
        intelligence.engine.load_free_keys()

    @bot.event
    async def on_message(message):
        if message.author.bot: return
        if isinstance(message.channel, discord.DMChannel):
            async with message.channel.typing():
                response = await intelligence.engine.get_response(message.content, message.author.id)
                if len(response) > 2000:
                    for i in range(0, len(response), 2000):
                        await message.channel.send(response[i:i+2000])
                else:
                    await message.channel.send(response)
        await bot.process_commands(message)

    @bot.command()
    async def boost(ctx, invite_link: str):
        if not os.path.exists("tokens.txt"):
            await ctx.send("❌ `tokens.txt` not found!")
            return
        with open("tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
        if not tokens:
            await ctx.send("❌ No tokens found!")
            return
        status_msg = await ctx.send(f"🚀 Starting boost process with {len(tokens)} tokens...")
        results = []
        for token in tokens:
            res = await booster_logic.boost_with_token(token, invite_link)
            results.append(res)
            if len(results) % 5 == 0:
                await status_msg.edit(content=f"🚀 Progress: {len(results)}/{len(tokens)} tokens processed...")
        success_count = sum(1 for r in results if r['success'])
        await ctx.send(f"✅ Boost completed! Success: {success_count}/{len(tokens)}")
    return bot

# --- RUNNERS ---

async def run_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    tasks_list = []
    if TOKEN_WELCOMER: tasks_list.append(create_welcomer().start(TOKEN_WELCOMER))
    if TOKEN_PROTECTION: tasks_list.append(create_protection().start(TOKEN_PROTECTION))
    if TOKEN_MANAGER: tasks_list.append(create_manager().start(TOKEN_MANAGER))
    if TOKEN_BOOSTER: tasks_list.append(create_booster_bot().start(TOKEN_BOOSTER))
    
    # Always run FastAPI for the dashboard
    tasks_list.append(run_fastapi())

    if len(tasks_list) == 1: # Only FastAPI
        print("ERROR: No bot tokens found!")
        await run_fastapi()
    else:
        print(f"Starting {len(tasks_list)-1} bots and Dashboard...")
        await asyncio.gather(*tasks_list)

if __name__ == "__main__":
    asyncio.run(main())
