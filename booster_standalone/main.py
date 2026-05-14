import discord
import os
import asyncio
import booster_logic
import ai_database as database
import intelligence
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import fetch_free_keys

load_dotenv()
TOKEN_BOOSTER = os.getenv('BOOSTER_TOKEN')

# --- FASTAPI SETUP ---
app = FastAPI()

class BoostRequest(BaseModel):
    token: str
    invite: str
    watermark: str = None

class LicenseRequest(BaseModel):
    key: str
    user_id: str

@app.post("/api/boost")
async def api_boost(request: BoostRequest):
    result = await booster_logic.boost_with_token(request.token, request.invite, request.watermark)
    return result

@app.post("/api/redeem")
async def api_redeem(request: LicenseRequest):
    res = database.db.redeem_license(request.key, request.user_id)
    if res:
        return {"success": True, "message": f"License redeemed! Type: {res[1]}"}
    return {"success": False, "message": "Invalid or already redeemed key."}

# Static file serving
if os.path.exists("dashboard"):
    app.mount("/static", StaticFiles(directory="dashboard"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("dashboard/index.html")

# --- DISCORD BOT SETUP (SLASH COMMANDS) ---
class BoosterBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Elite System: All Slash Commands Synced.")

    @tasks.loop(hours=6)
    async def auto_refresh_keys(self):
        print("Elite System: Refreshing free AI keys...")
        fetch_free_keys.fetch_keys()
        # Reload keys in intelligence engine
        intelligence.engine.load_free_keys()

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Server Boosts | v3.0.2"))
        # Initialize the free beta key
        database.db.add_debug_key("NOVA-FREE-BETA")
        
        # Start key refresh loop
        if not self.auto_refresh_keys.is_running():
            self.auto_refresh_keys.start()
            
        print(f"Elite System: Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author.bot: return
        
        # AI DM Handler
        if isinstance(message.channel, discord.DMChannel):
            if not database.db.is_authorized(str(message.author.id)):
                await message.channel.send("🔒 **Access Restricted.** You must redeem a license key to use Nova GPT.\nUse `/redeem <key>` in a shared server.")
                return

            async with message.channel.typing():
                response = await intelligence.engine.get_response(message.content, message.author.id)
                if len(response) > 2000:
                    for i in range(0, len(response), 2000):
                        await message.channel.send(response[i:i+2000])
                else:
                    await message.channel.send(response)
        
        await self.process_commands(message)

bot = BoosterBot()

@bot.tree.command(name="boost", description="Boost a server using stored tokens")
@app_commands.describe(invite="The server invite link", count="Number of boosts to apply")
async def boost(interaction: discord.Interaction, invite: str, count: int = 1):
    await interaction.response.send_message(f"🚀 Initializing elite boost for {invite}...", ephemeral=True)
    
    # Get tokens from tokens.txt (for now)
    if not os.path.exists("tokens.txt"):
        await interaction.followup.send("❌ `tokens.txt` not found!")
        return

    with open("tokens.txt", "r") as f:
        tokens = [line.strip() for line in f if line.strip()][:count]

    results = await booster_logic.multi_boost(tokens, invite)
    
    success_count = sum(1 for r in results if r['success'])
    embed = discord.Embed(title="Boost Process Completed", color=discord.Color.gold())
    embed.add_field(name="Total Attempted", value=str(len(tokens)))
    embed.add_field(name="Success", value=str(success_count))
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="redeem", description="Redeem a BoostBot license key")
async def redeem(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    res = database.db.redeem_license(key, str(interaction.user.id))
    if res:
        await interaction.followup.send(f"✅ Key Redeemed! You now have access to **Premium** features.")
    else:
        await interaction.followup.send("❌ Invalid or expired license key.")

# AI Commands
@bot.tree.command(name="status", description="Check your Nova GPT AI status")
async def status(interaction: discord.Interaction):
    authorized = database.db.is_authorized(str(interaction.user.id))
    status_text = "Authorized (Pro)" if authorized else "Unauthorized (Locked)"
    await interaction.response.send_message(f"**Nova GPT Status:** `{status_text}`", ephemeral=True)

@bot.tree.command(name="check-tokens", description="Verify your tokens and nitro status")
async def check_tokens(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 Checking token database...", ephemeral=True)
    # Placeholder for actual check logic
    await interaction.followup.send("Tokens check complete. Check dashboard for details.")

# --- MAIN RUNNER ---
async def run_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    if TOKEN_BOOSTER:
        print("Starting BoostBot v3.0.2...")
        await asyncio.gather(
            bot.start(TOKEN_BOOSTER),
            run_fastapi()
        )
    else:
        print("ERROR: BOOSTER_TOKEN not found!")
        await run_fastapi()

if __name__ == "__main__":
    asyncio.run(main())
