import discord
import os
import asyncio
import booster_logic
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN_BOOSTER = os.getenv('BOOSTER_TOKEN')

# --- FASTAPI SETUP ---
app = FastAPI()

class BoostRequest(BaseModel):
    token: str
    invite: str

# Serve static files from the dashboard directory
if os.path.exists("dashboard"):
    app.mount("/static", StaticFiles(directory="dashboard"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("dashboard/index.html")

@app.get("/style.css")
async def read_css():
    return FileResponse("dashboard/style.css")

@app.get("/script.js")
async def read_js():
    return FileResponse("dashboard/script.js")

@app.post("/api/boost")
async def api_boost(request: BoostRequest):
    result = await booster_logic.boost_with_token(request.token, request.invite)
    return result

# --- DISCORD BOT SETUP ---
def create_booster_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='b!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as Booster Bot: {bot.user}")

    @bot.command()
    async def boost(ctx, invite_link: str):
        if not os.path.exists("tokens.txt"):
            await ctx.send("❌ `tokens.txt` not found!")
            return

        with open("tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]

        if not tokens:
            await ctx.send("❌ No tokens found in `tokens.txt`!")
            return

        status_msg = await ctx.send(f"🚀 Starting boost process with {len(tokens)} tokens...")
        
        results = []
        for token in tokens:
            res = await booster_logic.boost_with_token(token, invite_link)
            results.append(res)
            
            if len(results) % 5 == 0:
                await status_msg.edit(content=f"🚀 Progress: {len(results)}/{len(tokens)} tokens processed...")

        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count
        
        embed = discord.Embed(title="Boost Process Completed", color=discord.Color.gold())
        embed.add_field(name="Total Tokens", value=str(len(tokens)), inline=True)
        embed.add_field(name="Success", value=str(success_count), inline=True)
        embed.add_field(name="Failed", value=str(fail_count), inline=True)
        
        if fail_count > 0:
            errors = "\n".join([r['message'] for r in results if not r['success']][:10])
            embed.add_field(name="Errors (Last 10)", value=f"```\n{errors}\n```", inline=False)

        await ctx.send(embed=embed)

    return bot

# --- MAIN RUNNER ---
async def run_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    bot = create_booster_bot()
    
    # Run both the bot and the dashboard
    if TOKEN_BOOSTER:
        print("Starting Booster Bot and Dashboard...")
        await asyncio.gather(
            bot.start(TOKEN_BOOSTER),
            run_fastapi()
        )
    else:
        print("ERROR: BOOSTER_TOKEN not found!")
        # Even if bot fails, run dashboard
        await run_fastapi()

if __name__ == "__main__":
    asyncio.run(main())
