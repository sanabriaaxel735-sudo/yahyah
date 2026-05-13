import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Define intents
intents = discord.Intents.default()
intents.members = True  # Required for on_member_join
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Game(name="Welcoming new members!"))

@bot.event
async def on_member_join(member):
    # Try to find a suitable channel
    channel_names = ['welcome', 'welcomes', 'general', 'chat']
    channel = None
    
    # 1. Try system channel
    if member.guild.system_channel:
        channel = member.guild.system_channel
    else:
        # 2. Search for common channel names
        for name in channel_names:
            channel = discord.utils.get(member.guild.text_channels, name=name)
            if channel:
                break
    
    # 3. Fallback to first available text channel
    if not channel:
        channel = member.guild.text_channels[0]

    if channel:
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}!",
            description=f"Hey {member.mention}, we're glad you're here! 🚀\n\nMake sure to read the rules and have a great time!",
            color=discord.Color.from_rgb(114, 137, 218) # Discord Blurple
        )
        
        # Add user's avatar if they have one
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar.url)
            
        embed.set_footer(text=f"Member #{len(member.guild.members)}")
        
        try:
            await channel.send(content=f"Welcome {member.mention}!", embed=embed)
        except Exception as e:
            print(f"Error sending welcome message: {e}")

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found in environment variables.")
    else:
        bot.run(TOKEN)
