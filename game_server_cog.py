import discord
import subprocess
import os

from discord import app_commands
from discord.ext import commands
from mcstatus import JavaServer
from subprocess import Popen

async def setup(bot):
    await bot.add_cog(game_server_cog(bot))


class game_server_cog(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   @app_commands.command(name = "startgameserver", description="start a game server")
   @app_commands.describe(server_type = "Which game server are you trying to run?")
   @app_commands.choices(server_type = [discord.app_commands.Choice(name = "Minecraft", value = os.environ.get('MINECRAFT_SERVER_DIR'))])
   async def start_game_server(self, interaction: discord.Interaction, server_type: discord.app_commands.Choice[str]):
      server_embed = discord.Embed(title= "", color= 5763719)

      match server_type.name :
         case "Minecraft" : 
            minecraft_server_instance.StartMC(server_type.value)

            server_embed.title = "Minecraft Server is Online"
            server_embed.add_field(name = "Server Address: ", value= minecraft_server_instance.server_url, inline = False)
            server_embed.add_field(name = "Version", value= "1.19.2 (forge)", inline = False)
            server_embed.add_field(name = "Mods", value= os.environ.get('MINECRAFT_MOD_URL'), inline = False)

            await interaction.response.defer()
            await interaction.followup.send(embed = server_embed)      
            return 

      await interaction.response.send_message("No matching game server found")

   @app_commands.command(name = "stopgameserver", description="stop a game server")
   @app_commands.describe(server_type = "Which game server are you trying to shutdown?")
   @app_commands.choices(server_type = [
      discord.app_commands.Choice(name = "Minecraft", value = os.environ.get('MINECRAFT_SERVER_URL') + ":25565"),
   ])
   async def stop_game_server(self, interaction: discord.Interaction, server_type: discord.app_commands.Choice[str]):
      server_embed = discord.Embed(title= "", color= 15548997)

      match server_type.name :
         case "Minecraft" : 
           try:
             await interaction.response.defer()
             minecraft_server_instance.StopMC()
             server_embed.title = "Minecraft Server is Offline"
             await interaction.followup.send(embed = server_embed)   
             return

           except: 
             await interaction.followup.send("ERROR: could not shutdown server")  

      await interaction.response.send_message("hi")

   @app_commands.command(name = "gameserverstatus", description="view game server status")
   @app_commands.describe(server_type = "Which game server's status are you trying to view?")
   @app_commands.choices(server_type = [
      discord.app_commands.Choice(name = "Minecraft", value =  os.environ.get('MINECRAFT_SERVER_URL') + ":25565"),
   ])
   async def game_server_status(self, interaction: discord.Interaction, server_type: discord.app_commands.Choice[str]):
       server_embed = discord.Embed(title= "Server Status", color= 3426654)

       match server_type.name :
         case "Minecraft" : 
             try: 
               await interaction.response.defer()
               server = JavaServer.lookup(server_type.value)
               status = server.status()
               server_embed.add_field(name = "Players Online: ", value= str(status.players.online), inline = False)
               server_embed.add_field(name = "Ping: ", value= str(status.latency) + "(ms)", inline = False)

               await interaction.followup.send(embed = server_embed)   
               return 
             except: 
                await interaction.followup.send("Failed to get server status!")   
                return 

       await interaction.response.send_message("hi")  

class MinecraftServer: 
   batch_file = "run.bat"
   server_url = os.environ.get('MINECRAFT_SERVER_URL')

   def StartMC(self, folder): 
    self.server = Popen(self.batch_file, cwd = folder, shell=True, stdin= subprocess.PIPE, text=True)
   
   def StopMC(self): 
    self.command('stop')
    self.server.communicate()

   def command(self, command):
    self.server.stdin.write(f'{command}\n')

minecraft_server_instance = MinecraftServer()  