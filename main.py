import discord
import os

from music_cog import music_cog
from misc_cog import misc_cog
from game_server_cog import game_server_cog
from arr_services_cog import arr_services_cog
from discord.ext import commands

client = commands.Bot(command_prefix=".", activity=discord.Activity(type = discord.ActivityType.streaming, name = "/ythelp OR /mediahelp"), intents=discord.Intents.all()) 

@client.event
async def on_ready(): 
    print("Bot is Online!")
    await client.add_cog(music_cog(client)), 
    await client.add_cog(game_server_cog(client)), 
    await client.add_cog(arr_services_cog(client)),
    await client.add_cog(misc_cog(client))

    try: 
       synced = await client.tree.sync()
       print(f"Synced {len(synced)} command(s)")
    except Exception as e: 
       print(e)
  
client.run(os.environ.get('DISCORD_BOT_KEY'), reconnect=True) 