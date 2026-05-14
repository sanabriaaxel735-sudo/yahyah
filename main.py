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
import booster_standalone.database as database
from discord import app_commands

def create_booster_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='b!', intents=intents)
    
    @bot.event
    async def on_ready(): 
        print(f"Logged in as Booster Bot (Nova GPT): {bot.user}")
        database.db.add_debug_key("NOVA-FREE-BETA")
        if not auto_refresh_keys.is_running():
            auto_refresh_keys.start()
        
        # Force Sync Slash Commands
        try:
            await bot.tree.sync()
            print("Elite System: Slash Commands Synced.")
        except Exception as e:
            print(f"Sync Error: {e}")

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

    # --- SLASH COMMANDS ---
    @bot.tree.command(name="boost", description="Boost a server")
    async def boost_slash(interaction: discord.Interaction, invite: str, count: int = 1):
        await interaction.response.send_message(f"🚀 Starting boost for {invite}...", ephemeral=True)
        if not os.path.exists("tokens.txt"):
            await interaction.followup.send("❌ `tokens.txt` missing!")
            return
        with open("tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()][:count]
        results = await booster_logic.multi_boost(tokens, invite)
        success = sum(1 for r in results if r['success'])
        await interaction.followup.send(f"✅ Completed! Success: {success}/{len(tokens)}")

    @bot.tree.command(name="redeem", description="Redeem a license key")
    async def redeem_slash(interaction: discord.Interaction, key: str):
        await interaction.response.defer(ephemeral=True)
        res = database.db.redeem_license(key, str(interaction.user.id))
        if res: await interaction.followup.send("✅ Key Redeemed! Premium features unlocked.")
        else: await interaction.followup.send("❌ Invalid or expired key.")

    @bot.tree.command(name="status", description="Check AI status")
    async def status_slash(interaction: discord.Interaction):
        auth = database.db.is_authorized(str(interaction.user.id))
        await interaction.response.send_message(f"Nova GPT Status: `{'Authorized' if auth else 'Locked'}`", ephemeral=True)

    @bot.tree.command(name="check-tokens", description="Check how many tokens are loaded")
    async def check_tokens_slash(interaction: discord.Interaction):
        if not os.path.exists("tokens.txt"):
            await interaction.response.send_message("❌ No `tokens.txt` found.", ephemeral=True)
            return
        with open("tokens.txt", "r") as f:
            count = len([line for line in f if line.strip()])
        await interaction.response.send_message(f"📊 You have **{count}** tokens loaded.", ephemeral=True)

    @bot.tree.command(name="add-tokens", description="Add more tokens to the list")
    async def add_tokens_slash(interaction: discord.Interaction, tokens: str):
        with open("tokens.txt", "a") as f:
            f.write(f"\n{tokens}")
        await interaction.response.send_message("✅ Tokens added successfully!", ephemeral=True)

    # --- PREFIX COMMANDS ---
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def sync(ctx):
        await ctx.send("🔄 Syncing slash commands...")
        await bot.tree.sync()
        await ctx.send("✅ Slash commands synced!")

    @bot.command()
    async def boost(ctx, invite_link: str):
        # (Existing boost logic)
        with open("tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
        results = []
        for token in tokens:
            res = await booster_logic.boost_with_token(token, invite_link)
            results.append(res)
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
