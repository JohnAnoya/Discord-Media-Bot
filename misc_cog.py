import discord 
import random

from discord import app_commands
from discord.ext import commands

async def setup(bot): 
    await bot.addcog(misc_cog(bot))

class misc_cog(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot
    
    @commands.command() 
    async def roll(self, ctx, num = 99):
      if(num is not None and type(num) == int and num > 0) :
        rand_num = random.randint(1, num)
      else:
        rand_num = random.randint(1, num)

      await ctx.reply("You rolled " + str(rand_num) + " point(s)")

    @commands.command() 
    async def assyrian(self, ctx):
      assyrian_embed = discord.Embed(title= "ASSYRIAN ALERT", color= 15548997,  image="https://img.thesitebase.net/10222/10222388/products/360x360@16259046659a480ba053.jpg",
                                    description="The Assyrians made everything, yeah they made you too. Bronah'd Ashur mashallah 💯🔥")

      await ctx.reply(embed = assyrian_embed)

    osmows_images = ["https://pbs.twimg.com/media/EzhFwKpXsAE_dxq.jpg", "https://pbs.twimg.com/media/GL-Mm8JWgAEZQvR.jpg", "http://en.spongepedia.org/images/3/32/Spongemund.jpg", "https://i.pinimg.com/736x/1f/41/de/1f41de53c882f886c3934ebce509f7b1.jpg"]
    @app_commands.command(name = "osmows", description="someone just ate osmows")
    @app_commands.describe(osmows_eater = "What is the name of the osmows eater?") 
    async def osmows(self, interaction: discord.Interaction, osmows_eater:str):
      print(len(misc_cog.osmows_images))
      rand_img = random.randint(0, len(misc_cog.osmows_images) - 1)

      osmows_embed = discord.Embed(title= "🚨OSMOWS EMERGENCY ALERT🚨", color= 15548997, description= osmows_eater + " ate osmows gg")
      osmows_embed.set_image(url = misc_cog.osmows_images[rand_img])

      await interaction.response.send_message(embed = osmows_embed)